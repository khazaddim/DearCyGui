## Why

The `Game_Controller_Build` fork added a native `PlotColorBars` plot series, which supports per-bar colors, viewport-edge anchoring and a normalized length mode. That branch lost its shared Git history with upstream, so the feature cannot simply be merged. This worktree tracks Axel Davy's current `main`, and color bars are the smaller and more self-contained of the two fork features. Porting them first proves the adapt-and-validate workflow before the larger multi-controller port.

## What Changes

- Add a native `PlotColorBars` plot series (subclass of `plotElementXY`) to `dearcygui/plot.pxd` and `dearcygui/plot.pyx`. It is adapted to the current upstream code, not cherry-picked.
- Expose these properties: `X`, `Y`, `colors`, `line_colors`, `horizontal`, `anchor` (`baseline` | `axis_min` | `axis_max`), `anchor_value`, `weight`, `value_space` (`data` | `normalized`) and `normalized_max_fraction`. `ignore_fit` is inherited from the base class.
- Resolve edge-anchored geometry and normalized lengths inside the native draw pass, using the live plot limits, so there is no pan/zoom lag.
- Preserve exclusion from both continuous autofit and one-time axis fitting in every mode, even with `ignore_fit=False`. This avoids viewport-dependent fitting feedback and keeps parity with the fork.
- Validate the configuration and raise `ValueError` for:
  - mismatched `X`/`Y` lengths
  - bad color array lengths
  - a non-positive `weight`
  - an unknown `anchor` or `value_space`
  - a `normalized_max_fraction` outside (0, 1]
- Add `PlotColorBars` to the type stubs (`dearcygui/core.pyi`) and to the plot docs (`dearcygui/docs/plots.md`).
- Bring over `PlotColorBars_Demo.py` as the manual verification demo, and add automated configuration tests.
- Purely additive: existing `PlotBars` and other plot items are unchanged. No **BREAKING** changes.

Provenance (historical evidence only; it does not certify this port):

- Implementation commits on `Game_Controller_Build`:
  - [`9812864`](https://github.com/khazaddim/DearCyGui/commit/9812864a54be9b24349fdd54a76a7d9d4d7b9cb0) — initial PlotColorBars
  - [`4ac62eb`](https://github.com/khazaddim/DearCyGui/commit/4ac62eb670712f81a69d3ef5e54f34263041c43c) — demo live controls
  - [`b6f4aa1`](https://github.com/khazaddim/DearCyGui/commit/b6f4aa1c4b5554b05a1ba03caf5b5852c9b10492) — normalized mode
- Original specs: [plot-color-bars spec](https://github.com/khazaddim/DearCyGui/blob/Game_Controller_Build/openspec/specs/plot-color-bars/spec.md), [normalized-mode change](https://github.com/khazaddim/DearCyGui/tree/Game_Controller_Build/openspec/changes/add-plot-color-bars-normalized-mode)
- See also [prior-integration-findings.md](../../references/prior-integration-findings.md).

## Capabilities

### New Capabilities
- `plot-color-bars`: a native colored bar plot series. It covers per-bar fill and border colors, both orientations, baseline and viewport-edge anchoring, frame-synchronous geometry, normalized length mode, configuration validation, exclusion from axis fitting and demo coverage.

### Modified Capabilities

None. This repository has no existing specs.

## Impact

- **Code:**
  - `dearcygui/plot.pxd`: new class declaration
  - `dearcygui/plot.pyx`: new class, small inline helpers, and two `ImPlot::GetItemData()` accessors in the existing `cdef extern from *` block
- **Stubs/docs:** `dearcygui/core.pyi` and `dearcygui/docs/plots.md`
- **Tests/demos:** new `tests/test_plot_color_bars.py` and a top-level `PlotColorBars_Demo.py`
- **Build:** Cython rebuild of the `plot` extension. No new dependencies and no `setup.py` changes.
- **API:** adds the public `dearcygui.PlotColorBars`, which is exported automatically by `from dearcygui.plot import *` in `dearcygui/__init__.py`.
