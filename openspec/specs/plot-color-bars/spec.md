# plot-color-bars Specification

## Purpose
TBD - created by archiving change add-plot-color-bars. Update Purpose after archive.
## Requirements
### Requirement: Native PlotColorBars Series
The system SHALL provide a native `PlotColorBars` plot series that behaves as a plot element rather than as a `DrawInPlot` child collection.

#### Scenario: Create a vertical native bar series
- **WHEN** application code creates `PlotColorBars` with `horizontal=False`, matching `X` and `Y` arrays, and a positive `weight`
- **THEN** DearCyGui SHALL render one vertical bar per data point as part of normal plot rendering
- **AND** the series SHALL participate in normal plot axis attachment, visibility, enablement, legend, and theme behaviors expected of native plot elements

#### Scenario: Create a horizontal native bar series
- **WHEN** application code creates `PlotColorBars` with `horizontal=True`
- **THEN** DearCyGui SHALL interpret `Y` as bar center positions and `X` as bar lengths
- **AND** the series SHALL render horizontal bars in the attached plot coordinate space

### Requirement: Per-Bar Fill and Border Colors
The system SHALL support either broadcast or per-bar colors for `PlotColorBars` fills and borders.

#### Scenario: Broadcast a single fill color
- **WHEN** `colors` contains one color value for a series with one or more bars
- **THEN** DearCyGui SHALL apply that fill color to every rendered bar

#### Scenario: Apply one fill color per bar
- **WHEN** `colors` contains exactly one color per bar
- **THEN** DearCyGui SHALL render each bar using its corresponding fill color

#### Scenario: Apply optional border colors
- **WHEN** `line_colors` is omitted or empty
- **THEN** DearCyGui SHALL render bars without borders by default
- **AND WHEN** `line_colors` contains one value or one value per bar
- **THEN** DearCyGui SHALL render borders using the broadcast or corresponding border color

### Requirement: Viewport-Edge Anchoring
The system SHALL support viewport-edge anchoring for `PlotColorBars` using the currently visible limits of the attached plot axes.

#### Scenario: Anchor bars to the visible maximum
- **WHEN** a horizontal `PlotColorBars` series is configured with `anchor="axis_max"`
- **THEN** DearCyGui SHALL resolve the starting edge of each bar from the current visible maximum of the attached X axis during drawing
- **AND** the bars SHALL remain visually locked to that visible edge while the plot pans or zooms

#### Scenario: Anchor bars to the visible minimum
- **WHEN** a vertical or horizontal `PlotColorBars` series is configured with `anchor="axis_min"`
- **THEN** DearCyGui SHALL resolve the starting edge of each bar from the current visible minimum of the attached primary value axis during drawing

#### Scenario: Anchor bars to a baseline
- **WHEN** a `PlotColorBars` series is configured with `anchor="baseline"` and an `anchor_value`
- **THEN** DearCyGui SHALL draw each bar from that fixed plot-coordinate baseline

### Requirement: Frame-Synchronous Geometry Resolution
The system SHALL resolve edge-anchored `PlotColorBars` geometry during native plot rendering rather than through a later Python callback.

#### Scenario: Pan without one-frame lag
- **WHEN** the user pans a plot containing edge-anchored `PlotColorBars`
- **THEN** DearCyGui SHALL compute the active anchor edge from the live visible plot limits in the same render pass as the plot
- **AND** the bars SHALL not depend on a subsequent Python resize or axis-change callback to stay visually attached to the plot edge

### Requirement: Configuration Validation
The system SHALL reject invalid `PlotColorBars` configuration inputs before drawing.

#### Scenario: Reject mismatched data lengths
- **WHEN** `len(X)` differs from `len(Y)`
- **THEN** DearCyGui SHALL raise a configuration error

#### Scenario: Reject invalid color array lengths
- **WHEN** `colors` or `line_colors` has a length other than `0`, `1`, or the bar count
- **THEN** DearCyGui SHALL raise a configuration error

#### Scenario: Reject invalid weight or anchor name
- **WHEN** `weight` is not strictly positive or `anchor` is not one of `baseline`, `axis_min`, or `axis_max`
- **THEN** DearCyGui SHALL raise a configuration error

### Requirement: Fit Control for Edge-Anchored Bars
The system SHALL allow edge-anchored `PlotColorBars` to be excluded from autofit calculations.

#### Scenario: Ignore fit for viewport decorations
- **WHEN** a `PlotColorBars` series is configured with `ignore_fit=True`
- **THEN** DearCyGui SHALL avoid expanding plot autofit ranges because of that series
- **AND** the series SHALL still render against the currently visible limits of its attached axes

### Requirement: Verification Demo
The system SHALL include a runnable demo file that verifies the main `PlotColorBars` behaviors manually.

#### Scenario: Demo covers the primary rendering modes
- **WHEN** a developer runs the dedicated `PlotColorBars` demo
- **THEN** the demo SHALL render at least one vertical per-bar-color series and one horizontal edge-anchored series
- **AND** the demo SHALL make it possible to visually confirm that edge-anchored bars stay attached to the active plot edge during pan or zoom

#### Scenario: Demo may be derived from an existing TA proof of concept
- **WHEN** an existing demo from a related repository already provides suitable plot, interaction, or overlay structure
- **THEN** the implementation MAY adapt that demo as the starting point for the verification file
- **AND** the resulting demo SHALL be checked into this repository as part of the `PlotColorBars` change

