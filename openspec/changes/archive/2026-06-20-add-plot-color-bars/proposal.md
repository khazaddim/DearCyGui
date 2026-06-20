# Change: Add PlotColorBars Native Plot Series

## Why
DearCyGui currently covers edge-anchored bar overlays most naturally through `DrawInPlot` children or custom draw-item helpers. That approach makes viewport-anchored bars depend on Python-side geometry updates after axis changes, which can produce visible lag while panning or zooming and scales poorly when each bar needs its own fill color.

## What Changes
- Add a new native `PlotColorBars` plot series for horizontal or vertical bar rendering
- Support per-bar fill colors and optional per-bar border colors in a single series
- Support three anchor modes: fixed baseline, current visible axis minimum, and current visible axis maximum
- Resolve viewport-edge anchors during native plot rendering so bars stay visually locked to the active plot edge while the plot is moving
- Add validation rules for array lengths, color broadcasting, supported anchor values, and positive bar weight
- Add API documentation and a dedicated verification demo file that exercises per-bar colors and edge-anchored bars
- Use the existing `TA_PoC_Invis_Btns.py` example from the related DearCyFi repo as a starting point for the demo structure if it reduces demo authoring time

## Impact
- Affected specs: `plot-color-bars` (new capability)
- Affected code:
  - `dearcygui/plot.pyx` - new `PlotColorBars` implementation and rendering path
  - `dearcygui/plot.pxd` - Cython declarations for the new series
  - `dearcygui/core.pyi` - public Python signature and property surface
  - `dearcygui/docs/plots.md` and/or a new plot-focused documentation page
  - a dedicated demo file for manual verification of vertical, horizontal, and edge-anchored usage

## Compatibility
- Existing `PlotBars` behavior remains unchanged
- Existing `DrawInPlot` workflows remain available for fully custom rendering
- The new API is additive and intended as the native replacement for Python-managed bar overlay helpers