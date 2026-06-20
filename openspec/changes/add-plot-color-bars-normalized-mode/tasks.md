# Tasks: Add Normalized Length Mode for PlotColorBars

## 1. Implementation
- [ ] 1.1 Add value-space and normalization fields to PlotColorBars declarations.
- [ ] 1.2 Implement value_space and normalized_max_fraction properties in plot implementation.
- [ ] 1.3 Update draw logic to convert length from normalized units to data units using live visible limits.
- [ ] 1.4 Keep existing data mode as default.

## 2. Validation
- [ ] 2.1 Validate allowed value_space values.
- [ ] 2.2 Validate normalized_max_fraction range.
- [ ] 2.3 Verify normalized mode works for horizontal and vertical bars under pan and zoom.
- [ ] 2.4 Verify anchor behavior remains correct in both data and normalized modes.

## 3. API and Documentation
- [ ] 3.1 Add public stubs and docs for value_space and normalized_max_fraction.
- [ ] 3.2 Update PlotColorBars demo with a normalized overlay example.
- [ ] 3.3 Add demo controls or presets that let users compare data mode and normalized mode side by side.
- [ ] 3.4 Document when to use normalized mode versus data mode.