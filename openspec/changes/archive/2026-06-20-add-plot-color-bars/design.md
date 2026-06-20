# Design: PlotColorBars Native Plot Series

## Context
The target use cases are candle-volume style bars, price-binned horizontal volume bars, and viewport-edge overlays that remain visually attached to a plot edge during pan and zoom. The existing `DrawInPlot` pattern is flexible, but it computes and mutates geometry outside the plot's own render pass, which creates timing gaps for edge-anchored bars and makes per-bar styling expensive.

## Goals
- Add a native plot series that renders bars directly during plot drawing
- Support horizontal and vertical bars with a single API
- Support per-bar fill colors and optional border colors without splitting data into many series
- Support viewport-edge anchoring based on the live visible limits of the attached plot axes
- Preserve normal plot attachment, legend, theme, and axis behaviors expected from native series

## Non-Goals
- Replacing or changing `PlotBars`
- Adding hit-testing or hover metadata for individual bars in this change
- Introducing a generalized normalized-value rendering mode beyond axis-edge anchoring

## Public API
The proposed public class is:

```python
class PlotColorBars(plotElementXY):
    def __init__(
        self,
        context,
        *,
        X=...,
        Y=...,
        colors=...,
        line_colors=...,
        horizontal=False,
        weight=1.0,
        anchor="baseline",
        anchor_value=0.0,
        ignore_fit=False,
        label="",
        axes=(Axis.X1, Axis.Y1),
        theme=...,
        show=True,
        enabled=True,
        no_legend=False,
        user_data=...,
    ):
        ...
```

### Semantics
- In vertical mode, `X` stores bar centers and `Y` stores bar lengths.
- In horizontal mode, `Y` stores bar centers and `X` stores bar lengths.
- `weight` is the thickness of each bar on the orthogonal axis, in plot units.
- `anchor` accepts `baseline`, `axis_min`, and `axis_max`.
- `anchor_value` is used only for `baseline` anchoring.
- `colors` and `line_colors` accept either a single broadcast color or one color per bar.

## Rendering Strategy
`PlotColorBars` should be implemented as a custom renderer in `draw_element()` rather than as a wrapper around `ImPlot::PlotBars`.

### Rationale
- The existing bar-series wrapper surface supports whole-series styling, not per-bar colors.
- Edge anchoring requires resolving geometry from the current visible plot limits during the same draw pass as the rest of the plot.
- A custom draw-list loop allows direct control over clipping, per-bar colors, and anchor handling without changing `PlotBars` semantics.

### Draw Path
1. Validate array sizes and cached property state.
2. Read the current visible limits for the attached axes.
3. Resolve the baseline or viewport-edge anchor from those live limits.
4. Convert each bar rectangle from plot coordinates to pixels.
5. Draw each bar through the plot draw list inside the plot clip rect.

For right-anchored horizontal bars, the core calculation is:

```text
visible_right = current visible X-axis max
bar_right = visible_right
bar_left = visible_right - bar_width
```

For bottom-anchored vertical bars, the core calculation is:

```text
visible_bottom = current visible Y-axis min
bar_bottom = visible_bottom
bar_top = visible_bottom + bar_height
```

## Data Model
At the Cython layer the series should follow the existing native plot-element family and extend `plotElementXY` with bar-specific state.

Suggested internal fields:

```cython
cdef class PlotColorBars(plotElementXY):
    cdef DCG1DArrayView _colors
    cdef DCG1DArrayView _line_colors
    cdef double _weight
    cdef bint _horizontal
    cdef int32_t _anchor_mode
    cdef double _anchor_value
    cdef bint _ignore_fit
    cdef void check_arrays(self) noexcept nogil
    cdef void draw_element(self) noexcept nogil
```

If the existing 1D array view cannot efficiently store packed colors, the implementation should introduce or reuse a packed-color representation that avoids per-frame Python conversion.

## Validation Rules
Validation should happen on assignment or configuration, with only cheap safety checks during draw.

- `len(X)` SHALL equal `len(Y)`
- `len(colors)` SHALL be `0`, `1`, or `len(X)`
- `len(line_colors)` SHALL be `0`, `1`, or `len(X)`
- `weight` SHALL be greater than `0`
- `anchor` SHALL be one of `baseline`, `axis_min`, or `axis_max`

## Fit and Axis Semantics
- `baseline` bars behave like ordinary plot data and participate in fit by default.
- `axis_min` and `axis_max` are viewport-decoration patterns and should normally be paired with `ignore_fit=True`.
- Edge-anchored bars remain plot-coordinate data; they are not post-processed draw items and they are not implicitly normalized bands.
- For bottom-band candle volume behavior, the recommended pattern is to attach the series to a dedicated fixed secondary axis.

## Alternatives Considered

### Extend `PlotBars`
Rejected because it mixes ordinary bar semantics with per-bar styling and viewport-edge behavior that require a different rendering model.

### Continue using `DrawInPlot` plus Python callbacks
Rejected because it preserves the frame-lag problem this change is intended to remove.

## Risks and Trade-offs
- Custom rendering code is more maintenance than a thin ImPlot wrapper.
- Per-bar draw loops may be slower than a single whole-series primitive, but they remove the much larger overhead of managing one Python child draw item per bar.
- Hover and hit-testing can be added later, but they are intentionally not part of this initial capability.

## Migration Guidance
Python-side helpers that manage one rectangle per bar can migrate to a single `PlotColorBars` instance. The most direct replacement for right-anchored horizontal overlays is `horizontal=True`, `anchor="axis_max"`, and `ignore_fit=True`.