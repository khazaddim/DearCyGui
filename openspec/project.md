# Project Context

## Purpose

DearCyGui is a Python GUI library that combines Dear ImGui with Cython bindings
to provide performant graphical interfaces, widgets, and data visualization.

## Tech Stack

- Python package with Cython `.pyx` and `.pxd` sources
- C++ native code and vendored dependencies, including Dear ImGui, ImPlot, and
  SDL
- Setuptools and CMake-based build configuration
- Pytest tests

## Project Conventions

### Architecture

- Public Python APIs are implemented primarily in `dearcygui/`.
- Native and third-party integrations live in `dearcygui/backends/` and
  `thirdparty/`.
- User-facing documentation is in `dearcygui/docs/`.

### Testing

- Tests are in `tests/` and use pytest.
- Changes to Cython or native code may require building the extension before
  runtime tests can be run.

## Important Constraints

- Preserve the existing Python API unless a proposal explicitly covers an API
  change.
- Treat vendored third-party code as external; avoid unrelated edits there.

## Integration Reference

For the upstream-first multi-controller and color-bar ports, read
[prior integration findings](references/prior-integration-findings.md).
These summarize the earlier branch's compatibility targets, build hazards, and
historical baselines. They are not an active change proposal or proof of current
behavior; establish a fresh baseline in this worktree.

### Original Feature Proposals

The source branch's
[OpenSpec changes](https://github.com/khazaddim/DearCyGui/tree/Game_Controller_Build/openspec/changes)
document the features being ported:

- [Multi-controller support](https://github.com/khazaddim/DearCyGui/tree/Game_Controller_Build/openspec/changes/add-multi-controller-support):
  per-controller state, enums, handlers, filtering, and hot-plug handling.
- [Original PlotColorBars feature (archived)](https://github.com/khazaddim/DearCyGui/tree/Game_Controller_Build/openspec/changes/archive/2026-06-20-add-plot-color-bars):
  native colored bars, borders, orientations, and render-time edge anchoring.
- [Normalized color-bar mode](https://github.com/khazaddim/DearCyGui/tree/Game_Controller_Build/openspec/changes/add-plot-color-bars-normalized-mode):
  opt-in lengths relative to the visible axis span, retaining data-unit defaults.
- [Consolidated plot-color-bars spec](https://github.com/khazaddim/DearCyGui/blob/Game_Controller_Build/openspec/specs/plot-color-bars/spec.md):
  the source branch's recorded capability specification.

Each change directory includes its proposal, design, tasks, and delta spec.
Read these alongside source code and the prior integration findings: some
controller wording and task status lag the implemented APIs. These references
do not approve or certify feature ports in this worktree.

For implementation diffs and supporting build changes, use the
[original implementation commit index](references/prior-integration-findings.md#original-implementation-commit-index).
It distinguishes feature code, proposal/demo changes, and packaging decisions;
the linked commits are references to adapt, not an automatic cherry-pick list.

### Feature Validation Demos

- [Fancy_Demo.py](https://github.com/khazaddim/DearCyGui/blob/Game_Controller_Build/Fancy_Demo.py):
  event-driven multi-controller demo with per-slot button/axis state, connection
  tracking, and an interactive plot for checking input/rendering coexistence.
- [PlotColorBars_Demo.py](https://github.com/khazaddim/DearCyGui/blob/Game_Controller_Build/PlotColorBars_Demo.py):
  color-bar demo with live controls for orientations, anchors, and data/
  normalized modes.

These are source-branch validation harnesses, not runnable demos supplied by
this worktree yet. Bring them over and adapt them alongside the feature ports,
using the local build skill to test the freshly installed extension. Manual
demo observations complement, but do not replace, automated regression tests.

### Active Feature Port Plans

- [Plot color bars](changes/port-plot-color-bars/proposal.md): the smaller,
  first port in the integration sequence.
- [Multi-controller support](changes/port-multi-controller-support/proposal.md):
  the subsequent cross-layer controller port. Its
  [design](changes/port-multi-controller-support/design.md) records reviewed
  implementation commits, both Windows native enablement gates, frame/lifetime
  adaptations, and the unchanged-copy-then-adapt plan for `Fancy_Demo.py`.
  Its [tasks](changes/port-multi-controller-support/tasks.md) separate
  deterministic connected-input tests from physical demo validation.

These are planning artifacts, not claims that either feature is implemented or
validated in this worktree.
