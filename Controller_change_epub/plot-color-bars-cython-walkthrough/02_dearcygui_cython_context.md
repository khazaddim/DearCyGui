# DearCyGui Cython Context

## Why There Is Both `plot.pxd` And `plot.pyx`

DearCyGui uses the standard Cython split:

- `plot.pxd` declares C-level layout and method signatures
- `plot.pyx` implements behavior

For `PlotColorBars`, the declaration looks like this in simplified form:

```cython
cdef class PlotColorBars(plotElementXY):
    cdef DCGVector[int32_t] _colors
    cdef DCGVector[int32_t] _line_colors
    cdef double _weight
    cdef bint _horizontal
    cdef int32_t _anchor_mode
    cdef double _anchor_value
    cdef int32_t _value_space
    cdef double _normalized_max_fraction
    cdef void _validate_configuration(self)
    cdef void draw_element(self) noexcept nogil
```

Read the real declaration at:

- `dearcygui/plot.pxd:114`
- `_value_space` field: `dearcygui/plot.pxd:121`
- `_normalized_max_fraction` field: `dearcygui/plot.pxd:122`

This is doing two things at once:

- it defines the compiled storage layout for each `PlotColorBars` instance
- it tells Cython that `draw_element()` can be called as a C-level method

## How This Fits DearCyGui

`PlotColorBars` inherits from `plotElementXY`, which means it reuses the standard DearCyGui storage for X and Y arrays. That is why the feature only needed to add bar-specific state instead of reinventing array handling.

The implementation then relies on DearCyGui helper types and wrappers:

- `DCG1DArrayView` for numeric array storage inherited from the base class
- `DCGVector[int32_t]` for packed colors
- ImGui and ImPlot wrapper namespaces for plotting and drawing calls
- DearCyGui locking helpers around Python-visible property setters

Relevant source anchors:

- `PlotColorBars` implementation starts at `dearcygui/plot.pyx:3039`
- constructor defaults at `dearcygui/plot.pyx:3047`
- validation function at `dearcygui/plot.pyx:3057`
- draw loop at `dearcygui/plot.pyx:3245`

## Important Helper Functions

Near the `PlotColorBars` block, the module defines a few small helpers that make the draw loop simpler:

```cython
cdef inline double _get_1d_plot_value(DCG1DArrayView& view, int32_t idx) noexcept nogil
cdef inline imgui.ImU32 _get_vector_color(DCGVector[int32_t]& colors, int32_t idx, imgui.ImU32 fallback) noexcept nogil
cdef inline double _resolve_anchor_value(implot.ImPlotRect limits, bint horizontal, int32_t anchor_mode, double anchor_value) noexcept nogil
cdef void _reset_color_vector(DCGVector[int32_t]& target, object value)
```

These helpers show a common DearCyGui pattern:

- Python parsing happens once in a setter, not every frame
- per-frame draw code works with compact C data
- repeated logic is pushed out of the main renderer

Read the real helpers here:

- `_get_1d_plot_value`: `dearcygui/plot.pyx:2985`
- `_resolve_anchor_value`: `dearcygui/plot.pyx:2999`
- `_get_vector_color`: `dearcygui/plot.pyx:3010`
- `_reset_color_vector`: `dearcygui/plot.pyx:3023`

One of those helpers turned out to be central to the runtime fix. `_get_1d_plot_value` must take `DCG1DArrayView` by reference, not by value, because the view carries ownership and cleanup state for Python buffers. Passing it by value in a hot draw loop risks copying and destructing the underlying view bookkeeping.

## The `nogil` Point

`draw_element()` is declared `noexcept nogil`. In practical terms, that means:

- the draw loop is intended to run without the Python GIL
- it should avoid Python object work inside the rendering path
- errors should have been rejected earlier by validation instead of being discovered during draw

This is one of the key reasons the setters call `_validate_configuration()` aggressively. It keeps the hot path simple and safe.

Follow that split in the source:

- validating properties begin in the `PlotColorBars` block around `dearcygui/plot.pyx:3079`
- `value_space` getter/setter at `dearcygui/plot.pyx:3213` and `dearcygui/plot.pyx:3221`
- `normalized_max_fraction` getter/setter at `dearcygui/plot.pyx:3233` and `dearcygui/plot.pyx:3239`
