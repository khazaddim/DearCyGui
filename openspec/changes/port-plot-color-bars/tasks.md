## 1. Setup and Provenance

- [ ] 1.1 Create the venv at `.venv` and build the unmodified upstream baseline using the [dearcygui-build skill](../../../.github/skills/dearcygui-build/SKILL.md). Record the baseline pytest results, including pre-existing failures.
- [ ] 1.2 Copy `PlotColorBars_Demo.py` unchanged from `Game_Controller_Build` (`9db7a6b`) into the repo root, and commit it on its own as provenance.

## 2. Cython Implementation

- [ ] 2.1 Add the `PlotColorBars(plotElementXY)` declaration to `dearcygui/plot.pxd` after `PlotBars`, with these fields:
  - `_colors`, `_line_colors`
  - `_weight`, `_horizontal`
  - `_anchor_mode`, `_anchor_value`
  - `_value_space`, `_normalized_max_fraction`
  - `_validate_configuration`, `draw_element`
- [ ] 2.2 In `dearcygui/plot.pyx`, add the `GetCurrentItemColorU32` / `GetCurrentItemLineWeight` helpers to the existing extern block, and the `uint32_t` cimport.
- [ ] 2.3 Add the inline helpers `get_1d_plot_value`, `get_vector_color`, `resolve_anchor_value` and `reset_color_vector`.
- [ ] 2.4 Implement the `PlotColorBars` class. Include:
  - `__cinit__` defaults
  - `_validate_configuration`
  - all property getters and setters, with upstream-style docstrings
  - the draw loop using `BeginItem`, `GetPlotLimits`, the plot clip rect and `EndItem`
  - normalized scaling
  - no contribution to axis fitting in any mode, preserving the inherited `ignore_fit` defaults and getter/setter behavior
- [ ] 2.5 Build. Verify an isolated import (`python -I -c "import dearcygui as dcg; dcg.PlotColorBars"`), and confirm that no generated `.cpp` files are staged.

## 3. Stubs and Docs

- [ ] 3.1 Regenerate `dearcygui/core.pyi` with `stubs/stub_generator.py`. Review the diff to confirm it contains only `PlotColorBars` changes; if not, use the hand-insert fallback described in the design.
- [ ] 3.2 Add a `PlotColorBars` section to `dearcygui/docs/plots.md` covering:
  - orientation
  - colors
  - anchors
  - normalized mode (linear axes only)
  - exclusion from both continuous autofit and one-time fitting in every mode, including with `ignore_fit=False`
  - using other fitting-enabled series or explicit axis limits when baseline/data-mode bars would otherwise be clipped

## 4. Automated Tests

- [ ] 4.1 Create `tests/test_plot_color_bars.py`, adapting the PlotColorBars cases from `471ba7d:tests/test_fork_regressions.py`, with this repo's fixture cleanup.
- [ ] 4.2 Cover:
  - defaults (`value_space == "data"`, `anchor == "baseline"`, `normalized_max_fraction == 1.0`)
  - property round-trips
  - broadcast and per-bar colors
  - both orientations × both value spaces × all anchors
  - each `ValueError` case in the spec
- [ ] 4.3 Add a render smoke test: create a plot with several `PlotColorBars` configurations, then render a few frames without errors (follow the existing plot tests' pattern for rendering, if available).
- [ ] 4.4 Add fitting regression tests for both orientations, all anchors, both value spaces, and both `ignore_fit` values. Compare both axis ranges against an equivalent plot without bars, for one-time fitting and continuous autofit across multiple frames. Use bar positions and extents outside the reference data range to prove exclusion, and verify `ignore_fit` property round-trips.
- [ ] 4.5 Run the new tests and the full suite. Confirm there are no regressions against the 1.1 baseline.

## 5. Demo Validation

- [ ] 5.1 Run `PlotColorBars_Demo.py`. If it is broken by upstream API changes (for example, the Viewport refactor `8777919`), adapt it in a separate commit with minimal changes.
- [ ] 5.2 Manually verify:
  - vertical per-bar colors
  - horizontal `axis_max` bars staying locked to the right edge during pan and zoom
  - `axis_min` anchoring
  - the normalized vs. data comparison during zoom
  - borders on and off
- [ ] 5.3 Record the validation results and any behavioral differences from the fork in this change. Then mark the change ready for archive.
