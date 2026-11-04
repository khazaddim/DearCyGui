# Tasks: Integrate upstream with multi-controller support

All implementation is pending approval. Each source entry requires the
disposition/result/verification record defined in [design.md](design.md).
Gate letters refer to its verification matrix. Preserve original source order;
atomic groups must record every member and why they are coupled.

## 0. Approval and baseline (before any source commit)

- [ ] 0.1 Review and approve proposal, scope, protected APIs, test gates, and permitted Git operations.
- [ ] 0.2 Verify integration and backup start at `9db7a6b5537fc194229fcc9f20e389959ee5ff30`; record clean status and frozen upstream `3d13328f3434db2ed9498831ce6fd2c5018ce430` (B).
- [ ] 0.3 Reconfirm content-equivalent January baseline and restored hand-written backend files; enumerate exactly 55 source commits with full SHAs (B).
- [ ] 0.4 Inventory working controller, bar-series, workflow, and dependency behavior; record discrepancies with the two pending related proposals without rewriting them (B, C, P, W).
- [ ] 0.5 Record installed-package provenance, baseline build/tests, known failures, and required native-toolchain settings (B).
- [ ] 0.6 Inventory hardware/virtual devices, external consumer availability, display requirements, CI/free-threaded environments, and approval for optional external runs. Add focused regression cases for protected behavior where missing (C, V, T).

## 1. Stage A: Initial upstream updates and dependencies

- [ ] 01 `bc00743` Bump version number: preserve fork-qualified version and account for its ImPlot pin change (S, P, W).
- [ ] 02 `80ca823` Viewport test check and async-helper TODO: inspect both changes; run affected viewport/async cases (A, V).
- [ ] 03 `19d2e43` Cross-thread AsyncThreadPool cancellation: verify cancellation and shutdown from another thread (A).
- [ ] 04 `a7ebaa8` Missing-loop detection: account for together with source revert 07; do not retain reverted behavior (A).
- [ ] 05 `c303fb8` Viewport-test atomic fix: verify test observes thread-safe state (V).
- [ ] 06 `4a4a621` SDL 3.4.4 pin: retain controller-capable configuration, rebuild and verify input (S, C, W).
- [ ] 07 `914dd01` Revert missing-loop detection: record final net behavior with 04 (A).
- [ ] 08 `012d18c` Disable new SDL requirements: preserve Linux workarounds and enabled joystick/gamepad support (S, W).
- [ ] A.gate Complete cumulative A/S/C/P/W checks relevant to this stage, record evidence, and establish approved checkpoint.

## 2. Stage B: Lifecycle, visibility, layouts, and widgets

- [ ] 09 `3ba4828` Plot-border DPI fix: check scaling and custom bar rendering (V, P).
- [ ] 10 `6a64692` Iterative delete_item: verify deep-tree deletion, table cleanup, GC and shutdown; no controller/context lifetime regression (C plus focused GC/shutdown tests).
- [ ] 11 `b27d524` DrawSVG path update: confirm changing path invalidates the cached texture (D).
- [ ] 12 `3c42032` Hidden initialization visibility: verify initial hidden/show transitions and backend/controller dispatch (L, V, C).
- [ ] 13 `fb79887` Visibility tests: run added cases; distinguish baseline failures from regressions (L).
- [ ] 14 `958e398` SDL/ImPlot pins: use source-recorded revisions, rebuild, and recheck controllers and native bars (S, C, P).
- [ ] 15 `a732e66` Additional visibility test: run the affected scenario (L).
- [ ] 16 `87759ab` Test improvements and widget change: inspect non-test hunk; run affected async/GC/shutdown/sizing/texture/viewport/widget selectors (A, L, V).
- [ ] 17 `ee3becd` Layout tests: record failures that intentionally require upcoming source 19; group 17-19 if needed and document (L).
- [ ] 18 `d4ce3c4` Spacer/ListBox/Separator traversed states: verify hidden and enabled behavior (L).
- [ ] 19 `0950ced` Layout rewrite: integrate with the older fork implementation, preserve custom callers, and verify nested geometry and reflow (L, V).
- [ ] 20 `b9e3967` MenuBar sizing: check dimensions and layout placement (L).
- [ ] 21 `0ccc7db` CollapsingHeader/TreeNode bounds: verify bounds, expansion and layout (L).
- [ ] 22 `cb6b054` ListBox enabled state: exercise disabled/re-enabled interaction (L).
- [ ] 23 `68c9546` Widget TODO handling: inspect real behavior changes and run affected widget selectors (L).
- [ ] 24 `4695fb0` Menu states: verify open/closed, focus and interaction state (L).
- [ ] 25 `c6b9225` Remove TODO: confirm comment-only scope; diff review unless patch proves otherwise.
- [ ] B.gate Pass cumulative lifecycle/layout/visibility checks and controller/plot smoke checks after dependency changes; record checkpoint.

## 3. Stage C: Frame scheduling and drawing-state prerequisites

- [ ] 26 `8777919` Viewport variable refactor: update all internal references consistently; preserve gamepad objects, begin-frame hook, public properties and custom plots (V, C, P).
- [ ] 27 `79a37dd` Presentation skip logic: reconcile backend/header/declaration changes with gamepad events and edge ordering; check idle/wake and two manual viewports (V, C).
- [ ] 28 `c9241e0` Layout redraw loop: test bounded settling and no redraw loop during input/resize (L, V).
- [ ] 29 `5252285` Layout content position: assert nested content origins and sizing results (L).
- [ ] 30 `6e7b9e6` DraggableBar initial position: verify starting value and first drag (L, P).
- [ ] 31 `3072d58` DrawInWindow draw-state restoration: verify nested draw state, subsequent siblings, and DrawingList swaps (D, V).
- [ ] C.gate Pass C/V/L/P and relevant D cases; record edge/callback counts, idle/wake behavior and checkpoint before October changes.

## 4. Stage D: Drawing, safety, and deliberate API removals

- [ ] 32 `ef1ac27` Pattern handling: verify affected solid/patterned primitives and record changed rendering/API semantics (D).
- [ ] 33 `f3ffcd1` DrawImage rotation: check asymmetric rotated images and explicit quad/UV paths used by 3D rendering (D).
- [ ] 34 `58794da` Angular vertex bounds: exercise affected shapes and boundary vertex counts (D).
- [ ] 35 `5d07590` Arrow rewrite: verify geometry, direction, outline/fill, thickness and migration notes (D).
- [ ] 36 `f617205` C++ set/map names: rebuild tables/image utilities and check no Python/C++ namespace collision.
- [ ] 37 `f5e55e7` Item non-initialization behavior: check lifecycle and error paths (L).
- [ ] 38 `95fdbc8` Valid items after errors: run added regressions and existing widget tests (L).
- [ ] 39 `38f73eb` Remove manual layout positioning: migrate affected in-repo callers and preserve custom enums while updating declarations (L, T).
- [ ] 40 `53877fd` Remove ChildWindow labels: migrate in-repo uses and document external DearCyFi change; verify expected AttributeError (L).
- [ ] 41 `eba42fe` Remove wrap_x: migrate affected callers and verify retained wrapping behavior (L).
- [ ] 42 `661d3e5` Remove no_saved_setting: update callers/docs and verify removal behavior (L).
- [ ] 43 `f84b678` Stub update: retain custom gamepad/bar declarations and synchronize layout API (T).
- [ ] D.gate Pass D/L/T and custom plot smoke checks; record API migration checklist and checkpoint.

## 5. Stage E: Typed callback migration and follow-ups

- [ ] 44 `5f50063` Typed callback values: integrate core/handler/declaration changes without altering existing gamepad tuple payloads or argument ordering; inspect removed helpers before adapting calls (T, C, A).
- [ ] 45 `89dea7f` Typing/export/build registration: include callback module in packaging, regenerate/merge stubs retaining custom exports, and verify plots (T, W, P).
- [ ] 46 `53668da` Exception handling: check ordinary errors remain visible and termination/cancellation exceptions propagate as intended (T, A).
- [ ] 47 `7b1ea05` uiItem callbacks: verify real value payloads and callback arities (T).
- [ ] 48 `ad138b0` Follow-up utilities/tables/stubs: inspect every consumer and run draggable/window/node/widget/table checks (T, L).
- [ ] 49 `691509c` Pattern cache and callback fixes: verify cache invalidation, texture behavior, handlers, plots, utilities and stubs (D, T, C, P).
- [ ] E.gate Build the complete callback migration; pass T/C/A/P, record exact gamepad payload types/counts and installed export/stub checks, then checkpoint.

## 6. Stage F: Font, sizing, wake, and release cleanup

- [ ] 50 `8a798fc` Reloaded font spacing: verify changed space advances/layout and markdown invalidation (D, L).
- [ ] 51 `6fcc659` Bold examples: inspect markdown implementation hunk as well as documentation; test behavior if executable changes are present (D).
- [ ] 52 `7546241` Negative widget/zero child sizing: assert layout geometry and distinguish negative DrawText screen-space sizing (L, D).
- [ ] 53 `866ecf4` Wake over-rendering: measure presented frames/settling behavior and repeat controller event-order/multi-viewport checks (V, C).
- [ ] 54 `3b2f645` Correct GPU-submission comment: confirm comment-only patch and accurate wording.
- [ ] 55 `3d13328` Release TODO cleanup: inspect all hunks and removed utils/layout.py; verify no import/caller regressions and do not assume title means documentation-only (D, L, T, A).
- [ ] F.gate Pass stage-specific and cumulative C/V/P tests, record final cleanup disposition and checkpoint.

## 7. Final validation and handoff

- [ ] 7.1 Audit all 55 entries for disposition, source/result mapping and required evidence; justify already-present/superseded entries and obtain approval for any deferral.
- [ ] 7.2 Compare final tree with frozen upstream and starting fork, explaining retained fork deltas and checking no custom APIs or restored backend files were lost.
- [ ] 7.3 Run cumulative in-scope pytest regression coverage against the rebuilt installed package; classify pre-existing failures with baseline evidence (E).
- [ ] 7.4 Complete manual controller/hot-plug/multi-viewport checks and eight-slot capacity evidence; explicitly record unavailable hardware/OS coverage as blocked (C, V).
- [ ] 7.5 Verify PlotColorBars data/normalized modes, edge anchoring and live pan/zoom; do not silently mark the independent normalized-bar proposal complete (P).
- [ ] 7.6 Verify wheel workflow/manual trigger and Linux/Windows/free-threaded targets in available real environments; no release/publishing runs without approval (W).
- [ ] 7.7 With permission, run bounded DearCyFi and DrawInWindow3D consumer checks after documented API migrations; record exact revision/environment or mark unavailable (E).
- [ ] 7.8 Update directly related migration, gamepad, build, and API docs/stubs with final behavior and known limitations.
- [ ] 7.9 Present validation evidence and unresolved items for approval before promoting integration to Game_Controller_Build; leave original and backup refs unchanged until explicitly authorized.
- [ ] 7.10 Archive this proposal only after acceptance/deployment; do not mark unchecked or blocked verification as passed.
