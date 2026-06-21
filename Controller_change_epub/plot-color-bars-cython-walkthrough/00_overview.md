# PlotColorBars Cython Walkthrough

This short book packages the two OpenSpec changes around `PlotColorBars`, plus the post-integration crash investigation that followed, into a Cython-focused review:

1. `add-plot-color-bars` introduced the new native series.
2. `add-plot-color-bars-normalized-mode` added viewport-relative bar lengths.
3. a later runtime-debugging pass fixed a native access violation in the custom draw loop.

The goal here is not only to review what changed, but to explain how the feature was implemented and stabilized in DearCyGui's style:

- state is stored in Cython `cdef class` fields
- Python properties validate and mutate that state
- draw-time behavior lives in `draw_element()`
- rendering decisions are made from live ImPlot limits inside the native draw pass
- helper signatures and memory semantics matter just as much as the high-level rendering math

The most important file is `dearcygui/plot.pyx`. That file contains the actual `PlotColorBars` class, its validation logic, the native draw loop that emits one rectangle per bar, and the helper boundary that caused the runtime crash.

## Follow Along In Source

- OpenSpec base proposal: `openspec/changes/archive/2026-06-20-add-plot-color-bars/proposal.md:1`
- OpenSpec base design: `openspec/changes/archive/2026-06-20-add-plot-color-bars/design.md:1`
- OpenSpec normalized proposal: `openspec/changes/add-plot-color-bars-normalized-mode/proposal.md:1`
- OpenSpec normalized design: `openspec/changes/add-plot-color-bars-normalized-mode/design.md:1`
- Cython declaration: `dearcygui/plot.pxd:114`
- Cython implementation start: `dearcygui/plot.pyx:3039`
- Public Python stub surface: `dearcygui/core.pyi:33745`
- Demo script entry points: `PlotColorBars_Demo.py:149`, `PlotColorBars_Demo.py:171`, `PlotColorBars_Demo.py:202`, `PlotColorBars_Demo.py:219`

## What To Watch For

If you are new to Cython, focus on these patterns while reading:

- `cdef class PlotColorBars(plotElementXY)`: a Python-visible extension type with C-level fields.
- `cdef` fields in `plot.pxd`: this is the compiled storage layout declaration.
- Python `@property` methods in `plot.pyx`: these are the user-facing mutation points.
- `noexcept nogil` draw code: performance-sensitive code that avoids Python overhead during rendering.
- helper functions near the `PlotColorBars` block: these isolate low-level type and color handling.
- targeted draw-loop probes: these are a practical way to debug native renderers without immediately reaching for a C++ debugger.

## Why This Feature Belongs In Cython

The first OpenSpec change is fundamentally about timing. Viewport-edge bars must stay locked to the visible plot edge while panning or zooming. Doing that from Python callbacks or post-draw geometry updates risks visible lag. The Cython implementation fixes this by reading plot limits and drawing the bars in the same native render pass as the rest of the plot.

The second OpenSpec change builds on that same idea. Normalized mode also needs the live visible span of the axis, so it belongs in the same native draw path instead of a Python zoom handler.

The later crash fix reinforces a second lesson: once render-time logic moves into native helpers, helper signatures and memory semantics matter as much as the high-level algorithm. In this case, the problem was not ImPlot itself, but an unsafe helper boundary inside the Cython layer.
