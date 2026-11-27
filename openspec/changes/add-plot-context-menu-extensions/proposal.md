# Change: Extend the Native Plot Context Menu

## Why

DearCyFi needs application actions in the same right-click plot menu as the
existing ImPlot axis, legend, and settings options. A separate popup would
require a different interaction or compete with the native menu.

## What Changes

- Investigate whether DearCyGui can append to the existing plot popup using
  Cython and existing ImGui APIs, without modifying vendored ImPlot or ImGui.
- First prove the approach with a narrowly scoped local prototype and the
  accompanying Python probes. The prototype is not a commitment to a public
  API before the rendering approach is validated.
- If the prototype succeeds, allow `Plot` to own existing `Menu` and `MenuItem`
  widgets that render inside the native plot-canvas popup.
- Preserve native menu contents, popup behavior, per-plot isolation, and normal
  DearCyGui callback queueing.
- Run integration and full-rebuild validation after the initial experiment.

## Impact

- Affected spec: new `plot-context-menu` capability.
- Likely code: `dearcygui/plot.pyx`, `dearcygui/plot.pxd`, and
  `dearcygui/wrapper/imgui.pxd`; public docs and stubs as appropriate.
- The Python probes in this change are explicitly invoked, not part of the
  default test suite.
- No DearCyFi changes or vendored C++ changes are included. If the experiment
  demonstrates that C++ changes are needed, stop and revisit the design.

## Compatibility

Plots without custom menu children retain their existing behavior. Custom
entries use the native menu button and do not replace the native menu.
