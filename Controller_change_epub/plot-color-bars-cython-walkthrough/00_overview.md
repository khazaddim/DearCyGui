# PlotColorBars Cython Walkthrough

This short book packages the last two OpenSpec changes around `PlotColorBars` into a Cython-focused review:

1. `add-plot-color-bars` introduced the new native series.
2. `add-plot-color-bars-normalized-mode` added viewport-relative bar lengths.

The goal here is not only to review what changed, but to explain how the feature was implemented in DearCyGui's style:

- state is stored in Cython `cdef class` fields
- Python properties validate and mutate that state
- draw-time behavior lives in `draw_element()`
- rendering decisions are made from live ImPlot limits inside the native draw pass

The most important file is `dearcygui/plot.pyx`. That file contains the actual `PlotColorBars` class, its validation logic, and the native draw loop that emits one rectangle per bar.

## Follow Along In Source

- OpenSpec base proposal: `openspec/changes/archive/2026-06-20-add-plot-color-bars/proposal.md:1`
- OpenSpec base design: `openspec/changes/archive/2026-06-20-add-plot-color-bars/design.md:1`
- OpenSpec normalized proposal: `openspec/changes/add-plot-color-bars-normalized-mode/proposal.md:1`
- OpenSpec normalized design: `openspec/changes/add-plot-color-bars-normalized-mode/design.md:1`
- Cython declaration: `dearcygui/plot.pxd:114`
- Cython implementation start: `dearcygui/plot.pyx:3045`
- Public Python stub surface: `dearcygui/core.pyi:33745`
- Demo script entry points: `PlotColorBars_Demo.py:125`, `PlotColorBars_Demo.py:169`, `PlotColorBars_Demo.py:186`, `PlotColorBars_Demo.py:217`

## What To Watch For

If you are new to Cython, focus on these patterns while reading:

- `cdef class PlotColorBars(plotElementXY)`: a Python-visible extension type with C-level fields.
- `cdef` fields in `plot.pxd`: this is the compiled storage layout declaration.
- Python `@property` methods in `plot.pyx`: these are the user-facing mutation points.
- `noexcept nogil` draw code: performance-sensitive code that avoids Python overhead during rendering.
- helper functions near the top of the module: these isolate low-level type and color handling.

## Why This Feature Belongs In Cython

The first OpenSpec change is fundamentally about timing. Viewport-edge bars must stay locked to the visible plot edge while panning or zooming. Doing that from Python callbacks or post-draw geometry updates risks visible lag. The Cython implementation fixes this by reading plot limits and drawing the bars in the same native render pass as the rest of the plot.

The second OpenSpec change builds on that same idea. Normalized mode also needs the live visible span of the axis, so it belongs in the same native draw path instead of a Python zoom handler.
