# Change: Add Normalized Length Mode for PlotColorBars

## Why
Volume overlays for candles often need stable on-screen size while users zoom the value axis. In the current PlotColorBars behavior, bar length is interpreted in plot data units, so zooming changes the visual height or width of bars. For side-volume and bottom-volume displays, users need a normalized mode where bars occupy a consistent fraction of the visible plot span.

## What Changes
- Add a normalized bar-length option to PlotColorBars that scales bar length by the current visible axis span during draw.
- Add a percentage control to define the maximum viewport fraction bars may occupy on the primary value axis.
- Keep existing data-unit behavior as the default mode for backward compatibility.
- Define validation and clamping rules for normalized settings.
- Extend docs and demo to show normalized side-volume and bottom-volume style usage.

## Impact
- Affected specs: plot-color-bars (modified capability)
- Affected code:
  - dearcygui/plot.pyx
  - dearcygui/plot.pxd
  - dearcygui/core.pyi
  - PlotColorBars_Demo.py
  - plot documentation pages

## Compatibility
- Existing PlotColorBars usage remains unchanged by default.
- Normalized behavior is opt-in via new properties.