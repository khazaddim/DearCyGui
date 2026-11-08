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
