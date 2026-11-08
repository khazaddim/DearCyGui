## ADDED Requirements

### Requirement: Native PlotColorBars Series
The system SHALL provide a native `PlotColorBars` plot series that is a `plotElementXY` plot element, not a `DrawInPlot` child collection. Like other native plot elements, it SHALL take part in axis attachment, visibility, legend and theme behavior.

#### Scenario: Create a vertical native bar series
- **WHEN** application code creates `PlotColorBars` inside a `Plot` with `horizontal=False`, matching `X` and `Y` arrays, and a positive `weight`
- **THEN** DearCyGui SHALL render one vertical bar per data point, centered at `X[i]`, with a length of `Y[i]` and a width of `weight`, as part of normal plot rendering

### Requirement: Horizontal Orientation
The system SHALL support horizontal `PlotColorBars`, where `Y` gives the bar center positions and `X` gives the bar lengths.

#### Scenario: Create a horizontal native bar series
- **WHEN** application code creates `PlotColorBars` with `horizontal=True`
- **THEN** DearCyGui SHALL render one horizontal bar per data point, centered at `Y[i]`, with a length of `X[i]` in the attached plot coordinate space

### Requirement: Broadcast and Per-Bar Fill Colors
The system SHALL accept `colors` as empty, a single color, or one color per bar. An empty value SHALL fall back to the theme fill color.

#### Scenario: Apply fill colors
- **WHEN** `colors` contains one color value
- **THEN** DearCyGui SHALL fill every bar with that color
- **AND WHEN** `colors` contains exactly one color per bar
- **THEN** DearCyGui SHALL fill each bar with its corresponding color

### Requirement: Optional Border Colors
The system SHALL draw bar borders only when `line_colors` is non-empty. `line_colors` follows the same broadcast and per-bar rules as `colors`.

#### Scenario: Borders are opt-in
- **WHEN** `line_colors` is omitted or empty
- **THEN** DearCyGui SHALL render bars without borders
- **AND WHEN** `line_colors` contains one value or one value per bar
- **THEN** DearCyGui SHALL draw borders using the broadcast or corresponding color and the item's theme line weight

### Requirement: Baseline Anchoring
The system SHALL draw bars from a fixed plot-coordinate baseline (`anchor_value`, default `0`) when `anchor="baseline"`, which is the default.

#### Scenario: Anchor bars to a baseline
- **WHEN** a `PlotColorBars` series is configured with `anchor="baseline"` and `anchor_value=v`
- **THEN** DearCyGui SHALL start each bar at `v` on the value axis and extend it by the bar length

### Requirement: Viewport-Edge Anchoring
The system SHALL support `anchor="axis_min"` and `anchor="axis_max"`. These start each bar at the visible minimum or maximum of the value axis: X for horizontal bars, Y for vertical bars. `axis_max` bars SHALL extend toward decreasing values.

#### Scenario: Anchor bars to the visible maximum
- **WHEN** a horizontal `PlotColorBars` series is configured with `anchor="axis_max"`
- **THEN** DearCyGui SHALL start each bar at the current visible maximum of the attached X axis and extend it toward smaller X values

#### Scenario: Anchor bars to the visible minimum
- **WHEN** a `PlotColorBars` series of either orientation is configured with `anchor="axis_min"`
- **THEN** DearCyGui SHALL start each bar at the current visible minimum of the attached value axis

### Requirement: Frame-Synchronous Geometry Resolution
The system SHALL resolve edge anchors and normalized lengths during the native plot render pass, using the live plot limits, and SHALL NOT depend on Python callbacks.

#### Scenario: Pan without one-frame lag
- **WHEN** the user pans or zooms a plot containing edge-anchored `PlotColorBars`
- **THEN** the bars SHALL remain visually attached to the active plot edge in the same frame, without any Python resize or axis-change callback

### Requirement: Normalized Length Mode
The system SHALL provide an opt-in `value_space="normalized"` mode. In this mode, the effective bar length is `length * normalized_max_fraction * visible_value_axis_span`, computed at draw time.

#### Scenario: Normalized vertical bars track Y zoom
- **WHEN** a vertical series uses `value_space="normalized"`
- **THEN** DearCyGui SHALL scale bar lengths by the current visible Y-axis span, so the bars keep a consistent proportion of the viewport as Y zoom changes

#### Scenario: Normalized horizontal bars track X zoom
- **WHEN** a horizontal series uses `value_space="normalized"`
- **THEN** DearCyGui SHALL scale bar lengths by the current visible X-axis span

### Requirement: Normalized Occupancy Fraction
The system SHALL scale normalized lengths by `normalized_max_fraction`, which defaults to `1.0` and must be in the range `0 < f <= 1`.

#### Scenario: Apply occupancy fraction
- **WHEN** `normalized_max_fraction=0.25` is set on a normalized series whose bar length is `1.0`
- **THEN** that bar SHALL span one quarter of the visible value-axis span

### Requirement: Data Mode Is the Default
The system SHALL interpret bar lengths in data units unless normalized mode is explicitly enabled.

#### Scenario: Default value space
- **WHEN** a `PlotColorBars` series is created without a `value_space` override
- **THEN** `value_space` SHALL read back as `"data"` and lengths SHALL be interpreted in data units

### Requirement: Anchor Semantics Are Mode-Independent
The system SHALL apply the same anchor semantics in both data mode and normalized mode. Normalized length conversion SHALL be applied before computing the bar end.

#### Scenario: Edge anchor with normalized mode
- **WHEN** a normalized series uses `anchor="axis_max"` or `anchor="axis_min"`
- **THEN** DearCyGui SHALL start each bar at the visible axis edge and compute the opposite edge from the normalized length

### Requirement: Configuration Validation
The system SHALL reject invalid `PlotColorBars` configuration by raising `ValueError` when the property is set.

#### Scenario: Reject invalid configuration
- **WHEN** any of the following is set:
  - `X` and `Y` with different non-zero lengths
  - `colors` or `line_colors` with a length other than 0, 1 or the bar count
  - `weight <= 0`
  - an `anchor` other than `baseline`, `axis_min` or `axis_max`
  - a `value_space` other than `data` or `normalized`
  - `normalized_max_fraction` outside `(0, 1]`
- **THEN** DearCyGui SHALL raise `ValueError`

### Requirement: Exclusion from Axis Fitting
`PlotColorBars` SHALL NOT contribute bounds to either axis during continuous autofit or a one-time fit request. This SHALL apply to both orientations, all anchors, and both value spaces. The system SHALL retain the inherited `ignore_fit` property for compatibility, but neither `True` nor `False` SHALL enable fitting for this series.

#### Scenario: Ignore fit for viewport decorations
- **WHEN** a plot containing `PlotColorBars` with `ignore_fit=True` performs an axis fit
- **THEN** the series SHALL NOT affect either axis's fitted range
- **AND** the series SHALL still render against the visible limits

#### Scenario: False does not opt into fitting
- **WHEN** a plot containing `PlotColorBars` with `ignore_fit=False` performs an axis fit, for any orientation, anchor, or value space
- **THEN** the series SHALL NOT affect either axis's fitted range
- **AND** the inherited property SHALL still read back as `False`

#### Scenario: Prevent viewport-dependent fitting feedback
- **WHEN** a plot with fitting-enabled data series continuously autofits across multiple frames and also contains edge-anchored or normalized `PlotColorBars`
- **THEN** its fitted axis ranges SHALL match those of an equivalent plot without the color bars
- **AND** color-bar geometry SHALL continue to resolve against the live plot limits without contributing bounds back to the fitter

### Requirement: Verification Demo
The repository SHALL include a runnable `PlotColorBars_Demo.py`. The demo SHALL show at least one vertical per-bar-color series, one horizontal edge-anchored series, and a normalized-mode series with a control to compare it against data mode.

#### Scenario: Run the demo
- **WHEN** a developer runs `PlotColorBars_Demo.py` against the built package
- **THEN** the demo SHALL open without errors and make it possible to visually confirm edge anchoring during pan and zoom, as well as normalized scaling
