# Runtime Crash Investigation

After the OpenSpec feature work and the normalized-mode follow-up were merged, `PlotColorBars` reached a surprising state:

- the extension built successfully
- `dearcygui` imported successfully
- `PlotColorBars` existed on the public API
- the dedicated demo launched briefly, then died with a Windows access violation

This chapter explains the actual root cause and the debugging process that exposed it.

## Why This Failure Was Hard To Read

The crash did not look like a normal Python bug.

- there was no ordinary Python exception
- `faulthandler` only showed that the process died inside the viewport loop
- a lot of surrounding integration work had happened recently, so stale generated C++ and rendering logic were both plausible suspects

The cheap discriminating checks mattered more than broad theory at this point.

## First Narrowing Step: Prove The Runtime Is Healthy Elsewhere

Before touching `PlotColorBars`, the debugging flow first ruled out broader runtime instability:

- a bare DearCyGui window survived
- a bare plot survived
- an empty `PlotColorBars` item that entered `BeginItem` and exited cleanly also survived

That immediately localized the fault to the per-bar body of `PlotColorBars.draw_element()` rather than the whole viewport loop or the surrounding plot/container machinery.

## The `continue` Probe Technique

The most useful debugging trick here was moving a temporary `continue` through the render loop.

The draw loop was simplified in stages:

1. keep `BeginItem` and `EndItem`, but skip the whole bar loop
2. allow anchor resolution, then `continue`
3. allow the first `_get_1d_plot_value` call, then `continue`
4. allow both reads, then `continue`
5. allow `PlotToPixels`, then `continue`
6. finally restore the rectangle draw calls

This worked because each step produced a crisp falsifiable result. As soon as the crash returned, the fault window collapsed to only a few lines.

In practice, the first `_get_1d_plot_value` call was enough to bring the crash back.

## The Real Root Cause

The bad helper boundary looked innocent at first:

```cython
cdef inline double _get_1d_plot_value(DCG1DArrayView values, int32_t index) noexcept nogil
```

The problem is the first argument. `DCG1DArrayView` is not a trivial POD bag of numbers. It carries ownership and cleanup state for Python-backed buffers. Passing it by value inside a hot draw loop means Cython can materialize temporaries whose destruction releases or corrupts the underlying view bookkeeping.

The fixed signature is:

```cython
cdef inline double _get_1d_plot_value(DCG1DArrayView& values, int32_t index) noexcept nogil
```

That keeps the helper working on the existing array view owned by the `PlotColorBars` instance instead of a copied temporary.

## The Second Bug Hidden Nearby: Stride Semantics

While investigating the helper, there was a second correctness issue nearby. `DCG1DArrayView.stride()` is stored in bytes, not in typed-element units. The final helper therefore reads values using byte-address arithmetic before casting to the right numeric pointer type.

That matters because the draw loop needs to handle DearCyGui's array views the same way the underlying C++ helper type stores them.

## Why `PlotToPixels` Was Not The Culprit

`PlotToPixels` was an early suspect because the crash only appeared during the custom native renderer, but the staged probe ruled it out.

- the crash happened before rectangle emission
- then before `PlotToPixels`
- then before the second per-bar read
- finally it was traced to the first helper-based array access

This is a good reminder that the most visible native API call is not always where the corruption starts.

## Final Fixed Mental Model

The repaired draw path now depends on three low-level invariants:

- `PlotColorBars` owns stable `DCG1DArrayView` instances through its base class
- helper functions must borrow those views by reference, not by value
- stride-aware reads must use byte addressing that matches `DCG1DArrayView` storage

Once those invariants held, the rest of the renderer worked again without redesign.

## Debugging Lessons To Reuse

- Start with the narrowest runtime that can still fail. The minimal `PlotColorBars` repro was far more useful than the full demo at first.
- Probe native render loops incrementally. Moving a `continue` through the loop is cheap, reversible, and highly discriminating.
- When a helper touches Python-backed native storage, check signature semantics before chasing rendering math.
- If a view type stores strides in bytes, never assume typed-pointer indexing semantics.

The end result is encouraging: the renderer design was sound, and the bug was local. The failure came from a low-level helper boundary, not from the overall `PlotColorBars` architecture.
