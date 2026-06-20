## ADDED Requirements

### Requirement: Normalized Length Mode
The system SHALL provide an opt-in normalized length mode for PlotColorBars that keeps bar occupancy proportional to the visible value-axis span during zoom.

#### Scenario: Enable normalized mode for vertical bars
- **WHEN** a PlotColorBars series is configured with value_space set to normalized and vertical orientation
- **THEN** DearCyGui SHALL compute bar length from the current visible Y-axis span during draw
- **AND** the bars SHALL maintain approximately consistent viewport proportion as Y-axis zoom changes

#### Scenario: Enable normalized mode for horizontal bars
- **WHEN** a PlotColorBars series is configured with value_space set to normalized and horizontal orientation
- **THEN** DearCyGui SHALL compute bar length from the current visible X-axis span during draw
- **AND** the bars SHALL maintain approximately consistent viewport proportion as X-axis zoom changes

### Requirement: Normalized Occupancy Fraction Control
The system SHALL allow callers to cap normalized bar occupancy using a configurable fraction of the visible primary value-axis span.

#### Scenario: Apply normalized occupancy fraction
- **WHEN** normalized_max_fraction is configured for a normalized PlotColorBars series
- **THEN** DearCyGui SHALL scale effective bar lengths by normalized_max_fraction relative to the current visible span

#### Scenario: Reject invalid occupancy fraction
- **WHEN** normalized_max_fraction is set outside the allowed range
- **THEN** DearCyGui SHALL raise a configuration error

### Requirement: Backward-Compatible Default Mode
The system SHALL preserve existing PlotColorBars data-unit behavior unless normalized mode is explicitly enabled.

#### Scenario: Default mode remains data units
- **WHEN** a PlotColorBars series is created without a value_space override
- **THEN** DearCyGui SHALL interpret bar lengths in data units exactly as before

### Requirement: Anchor Semantics in Normalized Mode
The system SHALL apply existing anchor semantics identically in data mode and normalized mode.

#### Scenario: axis_max anchor with normalized mode
- **WHEN** a normalized PlotColorBars series uses anchor set to axis_max
- **THEN** DearCyGui SHALL resolve bar start from the visible axis maximum during draw
- **AND** apply normalized length conversion before computing the opposite edge

#### Scenario: axis_min anchor with normalized mode
- **WHEN** a normalized PlotColorBars series uses anchor set to axis_min
- **THEN** DearCyGui SHALL resolve bar start from the visible axis minimum during draw
- **AND** apply normalized length conversion before computing the opposite edge

### Requirement: Normalized Mode Demo Coverage
The system SHALL include demo coverage that makes normalized scaling behavior easy to verify manually.

#### Scenario: Compare normalized and data modes in demo
- **WHEN** a developer runs the PlotColorBars demo for this change
- **THEN** the demo SHALL include at least one normalized PlotColorBars example for volume-style overlays
- **AND** the demo SHALL provide a clear way to compare normalized mode against data mode behavior during zoom