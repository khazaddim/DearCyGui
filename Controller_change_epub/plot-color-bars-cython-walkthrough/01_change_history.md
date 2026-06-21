# Change History

This walkthrough now covers three milestones rather than only the two original OpenSpec changes.

## Change 1: `add-plot-color-bars`

Source references:

- Proposal: `openspec/changes/archive/2026-06-20-add-plot-color-bars/proposal.md:1`
- Design: `openspec/changes/archive/2026-06-20-add-plot-color-bars/design.md:1`
- Cython class added in practice at `dearcygui/plot.pyx:3039`
- Cython storage declaration at `dearcygui/plot.pxd:114`
- Public API surface at `dearcygui/core.pyi:33745`

The archived change started with a design goal: create a native plot series for colored bars that supports:

- per-bar fill colors
- optional per-bar border colors
- horizontal and vertical rendering
- three anchor modes: `baseline`, `axis_min`, `axis_max`
- resolution of viewport-edge anchors from live visible plot limits during rendering

The design explicitly rejected a Python-side `DrawInPlot` callback approach because the feature needed frame-synchronous geometry.

### Result In Code

This change introduced:

- a new `PlotColorBars` Cython class in `dearcygui/plot.pyx`
- storage declarations in `dearcygui/plot.pxd`
- public constructor and property surface in `dearcygui/core.pyi`
- a dedicated demo script for manual verification

## Change 2: `add-plot-color-bars-normalized-mode`

Source references:

- Proposal: `openspec/changes/add-plot-color-bars-normalized-mode/proposal.md:1`
- Design: `openspec/changes/add-plot-color-bars-normalized-mode/design.md:1`
- New internal fields in `dearcygui/plot.pxd:121` and `dearcygui/plot.pxd:122`
- New properties in `dearcygui/plot.pyx:3213` and `dearcygui/plot.pyx:3233`
- Draw-time normalized conversion in `dearcygui/plot.pyx:3245`
- Public stub updates in `dearcygui/core.pyi:33754`, `dearcygui/core.pyi:33789`, `dearcygui/core.pyi:33914`, and `dearcygui/core.pyi:33931`

The second change modified the existing capability rather than creating a new series. The user need was stable on-screen bar size while zooming.

The design introduced two new API knobs:

- `value_space = "data" | "normalized"`
- `normalized_max_fraction`

In normalized mode, bar length is no longer interpreted directly as data units. Instead, the draw loop multiplies the raw value by the currently visible axis span and the configured fraction.

## Why These Two Changes Fit Together

The first change establishes the rendering model:

- store a small amount of series state
- validate at assignment time
- convert plot-space rectangles to pixels during `draw_element()`

The second change only works cleanly because that rendering model already exists. Once the bars are computed from live plot limits inside the native draw pass, adding normalized scaling becomes a local change:

- add two fields
- add two validating properties
- branch in the draw loop before computing `end_value`

That is a useful Cython lesson: once the right abstraction boundary exists, the follow-up feature becomes an incremental state-and-branch change instead of a redesign.

## Change 3: Runtime Crash Investigation And Fix

The original two changes built and imported successfully, but later integration work exposed a native access violation in `PlotColorBars` at runtime. The failure was especially misleading because:

- the extension compiled cleanly
- `import dearcygui` worked
- a bare window and a bare plot both worked
- the crash only appeared once the per-bar `PlotColorBars` draw path started reading data in the render loop

The final fix was not a rendering redesign. It was a helper-correctness fix in `dearcygui/plot.pyx`:

- `_get_1d_plot_value` now takes `DCG1DArrayView&` by reference instead of by value
- the helper also reads array elements using byte-stride addressing, which matches `DCG1DArrayView` storage semantics

That bug and the debugging process are covered in the runtime chapter, but it belongs in the change history because it materially changed the final implementation readers will see in source.

If you want to compare spec intent to code directly, read in this order:

1. `openspec/changes/archive/2026-06-20-add-plot-color-bars/design.md:1`
2. `dearcygui/plot.pxd:114`
3. `dearcygui/plot.pyx:3039`
4. `openspec/changes/add-plot-color-bars-normalized-mode/design.md:1`
5. `dearcygui/plot.pyx:3213`
6. `dearcygui/plot.pyx:3245`
7. the runtime debugging chapter in this book
