# Tasks: Add PlotColorBars Native Plot Series

## 1. Implementation
- [ ] 1.1 Add `PlotColorBars` declarations to `dearcygui/plot.pxd`
- [ ] 1.2 Implement `PlotColorBars` state, validation, and draw loop in `dearcygui/plot.pyx`
- [ ] 1.3 Expose the public constructor and properties in `dearcygui/core.pyi`
- [ ] 1.4 Reuse or add a packed-color storage path that avoids per-frame Python color conversion

## 2. Behavior Validation
- [ ] 2.1 Verify vertical bars render correctly with baseline anchoring
- [ ] 2.2 Verify horizontal bars render correctly with `axis_max` anchoring while panning
- [ ] 2.3 Verify `axis_min` and `axis_max` anchors resolve from the current visible limits during each draw
- [ ] 2.4 Verify invalid array lengths, invalid anchor names, and non-positive weight fail fast during configuration
- [ ] 2.5 Verify `ignore_fit=True` prevents viewport-edge bars from expanding autofit ranges

## 3. Documentation and Examples
- [ ] 3.1 Document the `PlotColorBars` API and anchor semantics
- [ ] 3.2 Create a dedicated demo file that verifies vertical per-bar colors, right-anchored horizontal bars, and live pan behavior
- [ ] 3.3 Use `TA_PoC_Invis_Btns.py` from the related DearCyFi example set as a starting point if its plot/demo structure is useful: https://github.com/khazaddim/DearCyFi/tree/main/examples
- [ ] 3.4 Add a vertical per-bar-color example to docs or inline demo comments
- [ ] 3.5 Add a right-anchored horizontal example suitable for liquidity or price-volume overlays
- [ ] 3.6 Document the recommended fixed-secondary-axis pattern for bottom-band candle volume