# Change: Integrate upstream while preserving the controller fork

## Why

`Game_Controller_Build` has a rewritten history and custom multi-controller,
PlotColorBars, and wheel-build behavior. The fork's `main` comparison only showed
24 new upstream commits; the active branch also lacks earlier prerequisite
updates. Applying the last 24 alone would omit the layout and viewport changes
they build upon.

The integration needs an ordered, reviewable record of every upstream commit,
explicit resolutions for custom-code overlaps, and test gates before proceeding.

## What Changes

- Account for the 55 commits after upstream baseline
  `01d2ce70f00658f4119a86c34a915e53d3775b88` through frozen target
  `3d13328f3434db2ed9498831ce6fd2c5018ce430`, oldest first.
- Work only on `integrate/game-controller-upstream-2026-11-03`, initially
  `9db7a6b5537fc194229fcc9f20e389959ee5ff30`; preserve the original branch and
  `backup/game-controller-build-pre-upstream-2026-11-03` at that starting point.
- Permit cherry-picks, adapted ports, and evidence-backed no-ops, recording
  provenance and verification for every source commit.
- Preserve the fork's controller APIs, event ordering, tuple callback payloads,
  custom plot bars, SDL controller build support, and customized wheel workflow.
- **BREAKING:** deliberately adopt upstream's documented draw/API changes,
  including removal of child-window labels, deprecated manual layout positioning,
  `wrap_x`, and `no_saved_setting`; document caller migrations.
- Add focused regressions and stage gates for SDL, asynchronous execution,
  layouts, rendering, typed callbacks, drawing, and custom fork functionality.
- Require explicit approval and a clean baseline before implementation. This
  proposal does not apply upstream patches or certify runtime compatibility.

## Impact

- New capability: `upstream-integration`.
- Related proposals: [multi-controller support](../add-multi-controller-support/proposal.md)
  and [normalized bars](../add-plot-color-bars-normalized-mode/proposal.md).
  Their checklist status is not proof of the running implementation; record
  observed baseline behavior before integration. Do not silently rewrite or
  archive either proposal as part of this work.
- Preserved specification: [plot-color-bars](../../specs/plot-color-bars/spec.md).
- Affected implementation: SDL backend/submodules, Cython core and declarations,
  handlers, layouts, widgets, drawing, fonts, callbacks, plots, utilities, stubs,
  tests, packaging, and directly related documentation.
- External consumer checks: DearCyFi demo and DrawInWindow3D framework, with
  permission to run them separately; no automatic edits to other repositories.
- See [design](design.md) for invariants, verification gates, rollback, and
  recording conventions; see [tasks](tasks.md) for all 55 source commits.
