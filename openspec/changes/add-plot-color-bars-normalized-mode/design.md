# Design: Normalized Length Mode for PlotColorBars

## Context
PlotColorBars currently interprets lengths directly in data units. This is ideal for ordinary bars but not for viewport-style overlays such as candle volume strips on the side or bottom. Those overlays should maintain near-constant screen proportion while users zoom.

## Goals
- Add an opt-in normalized length mode for PlotColorBars.
- Support a clear percentage-based control of visible-axis occupancy.
- Preserve frame-synchronous rendering and existing anchor semantics.
- Keep default behavior unchanged.

## Non-Goals
- Replacing PlotDigital behavior wholesale.
- Introducing a generic pixel-space renderer for all plot elements.
- Changing existing baseline data-unit semantics.

## Proposed API
- value_space: "data" | "normalized"
- normalized_max_fraction: float (for example 0.0 to 1.0)

Default values:
- value_space = "data"
- normalized_max_fraction = 1.0

## Rendering Semantics
In normalized mode, bar length is interpreted as a normalized scalar and converted during draw using the current visible span of the primary value axis.

For vertical bars:
- visible_span = limits.Y.Max - limits.Y.Min
- effective_length = raw_length * normalized_max_fraction * visible_span

For horizontal bars:
- visible_span = limits.X.Max - limits.X.Min
- effective_length = raw_length * normalized_max_fraction * visible_span

Anchor behavior remains unchanged:
- baseline starts at anchor_value
- axis_min starts at current visible minimum
- axis_max starts at current visible maximum

The only difference is how length is converted before rectangle endpoints are computed.

## Validation
- value_space must be one of data or normalized.
- normalized_max_fraction must be > 0 and <= 1.
- Existing PlotColorBars validation remains in force.

## Trade-offs
- Module-level implementation is more code than a Python zoom handler.
- Native mode avoids callback lag and repeated Python-side geometry rewrites.
- Opt-in mode avoids breaking users who rely on data-unit lengths.

## Migration Notes
- Existing code requires no changes.
- Side-volume and bottom-volume overlays can switch to normalized mode with:
  - value_space="normalized"
  - normalized_max_fraction set to the desired occupancy fraction.