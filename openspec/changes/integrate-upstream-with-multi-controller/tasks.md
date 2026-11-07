# Tasks: Integrate upstream with multi-controller support

Implementation from `5213cc71d80b890ee1115cd0b47974724c6e91cd` was approved by
the user on 2026-11-06. Required baseline and stage gates remain mandatory;
Scoped local integration commits, cherry-picks/adapted ports, submodule updates,
and checkpoint branches are authorized. Recorded baseline failures are accepted
for comparison; unavailable hardware/visual/external checks may be deferred
while automated integration proceeds, but remain unchecked. No push, promotion,
reset, publication, external runs, or archive is authorized.
Each source entry requires the
disposition/result/verification record defined in [design.md](design.md).
Gate letters refer to its verification matrix. Preserve original source order;
atomic groups must record every member and why they are coupled.
Suggested models below are implementation aids, not approval to execute tasks
or to claim runtime and hardware verification.

## 0. Approval and baseline (before any source commit)

Suggested model: Claude Opus 5.5 — reconstruct provenance and review the cross-cutting
baseline; approval and environment-dependent observations remain human-owned.

- [x] 0.1 Review and approve proposal, scope, protected APIs, test gates, and permitted Git operations.
  Approval: User authorized the updated starting point and implementation on
  2026-11-06. User accepted recorded baseline failures and authorized deferring
  unavailable hardware/visual/external checks while continuing automated
  integration, plus scoped local commits, cherry-picks/adapted ports, submodule
  updates, and checkpoint branches. Deferred gates stay unchecked and new
  regressions still block. Push, promotion, reset, publication, external runs,
  and archive are excluded.
- [x] 0.2 Verify approved integration start `5213cc71d80b890ee1115cd0b47974724c6e91cd` and original/backup `9db7a6b5537fc194229fcc9f20e389959ee5ff30`; record clean status and frozen upstream `3d13328f3434db2ed9498831ce6fd2c5018ce430` (B).
  Verification: On 2026-11-06, `git status --short` was empty before recording
  approval. `git branch --show-current` returned
  `integrate/game-controller-upstream-2026-11-03`; `git rev-parse HEAD
  Game_Controller_Build backup/game-controller-build-pre-upstream-2026-11-03
  3d13328f3434db2ed9498831ce6fd2c5018ce430` confirmed the hashes above.
  `git diff --stat 9db7a6b HEAD` showed only proposal, design, tasks, and delta
  spec documents (472 inserted lines across four files).
- [x] 0.3 Reconfirm content-equivalent January baseline and restored hand-written backend files; enumerate exactly 55 source commits with full SHAs (B).
  Verification: `git diff --quiet f0948a0 01d2ce7 -- .` excluding only the
  three hand-written backend `.cpp` paths returned 0. The complete diff contains
  exactly those three additions (3,817 lines). `git diff --stat 01d2ce7 d4ef4a7
  -- dearcygui/backends` was empty, confirming restoration content matches
  upstream's January baseline. `git ls-files dearcygui/backends` confirms all
  three remain tracked; later controller modifications are retained.
  `git rev-list --count 01d2ce7..3d13328` returned 55.
  `git rev-list --reverse 01d2ce7..3d13328` produced this ordered inventory:

  ```text
  01 bc00743005e8621c69c76fe6f936d0eea7f1f082
  02 80ca82311e18c18fe9b01fd4633f5bf337a87755
  03 19d2e43934788719ade8705524131c56a1600e4d
  04 a7ebaa88dad4df9d0f678d1fbb5cfb2580f5acba
  05 c303fb8d088e4434f8cc5cc4ad902cef08c7240c
  06 4a4a621d2d2495eb4cd07d66a7f5eb70e753771f
  07 914dd015ebc61128db817e7aface6765c36b5bf3
  08 012d18ca1e732040f03cb2a478475b5e4de144df
  09 3ba482820569b7bceca460e981fd0f2eb2778782
  10 6a64692f0709d6135f2121b1c1f53cfe1516ae5c
  11 b27d524fc9ef693ca38856ca87629cf56e078c1c
  12 3c42032353c9a7edcce7ea26f55f3e5dc1a58983
  13 fb79887b059d62232fcc0e34f0ee4dd545e1552c
  14 958e398cf20d55ba7622b52b4c53fd8a5ce4f34d
  15 a732e662dea260fde679e341ffd20d83bbc6f770
  16 87759abf1e879d35cee1fb818bf3258b7e027ee9
  17 ee3becddcb14fa1713b493cce27545e0c10286f9
  18 d4ce3c483fb9df427af2818dd30a087bdb1444ea
  19 0950ced44254520af2c93e6e4d751a673176f395
  20 b9e3967e874c1bacb74b3ca2e5bfa0c6da2892c3
  21 0ccc7db71cab78fc2b9145434cc0dc8caa4806ca
  22 cb6b0542f7a373d60cfb81c523694fc04a1b8b58
  23 68c9546b60f1e1eb4db2c0d6029ae88b775e0a4d
  24 4695fb0a5162f2746cfea560055d99b0a6ca808b
  25 c6b92257784ee76b37149e48fee83115daa6dcc9
  26 87779190beedbf8907fe5fb7b85a1294381c5555
  27 79a37ddf9b2a70e0614ac275cf04697f198f8742
  28 c9241e03f1d76e50ee17eabc7be88d8b59289382
  29 5252285482e11446fbe9df13701c02f0a2e17ca7
  30 6e7b9e619a03c65ae34f4637e761e8c4c1b3ce41
  31 3072d58c7651a8b28fb3581f021f73915198bb4c
  32 ef1ac278e2624d87af5247f0832d493a0c92430e
  33 f3ffcd1047e50a34d1fc614c81a3e7abc81c3f88
  34 58794da3685228966d72888f26fb28b1869461f8
  35 5d075909e71bca140fa406dbcf8b47d749ec4a34
  36 f61720517464201b658debc4c8e631b1caaac27d
  37 f5e55e7802e7edaca1df9225b562cd62f6373496
  38 95fdbc8c7df7bed5313a4ab427596a519f3d36aa
  39 38f73eb05de06cff0f05aa2aca425adba8601f73
  40 53877fd30a0ea6651f1f5b65a0e9834c7c9e21bb
  41 eba42fea177ad17a5edc3e093944ac8efd2da30b
  42 661d3e51e42e28ce9d47b24e60735a477394916a
  43 f84b67835be7f71ffbae430ef2768ae4937736ed
  44 5f5006368096537ee6fe6643f9fa8d5e1f577063
  45 89dea7f77cc2613638a891d7981a9a1f480bcc48
  46 53668da64cd99b736ce24b20e8677e220e240f87
  47 7b1ea05cb9f17aa7bc87fc2ea33666d61bc63ad7
  48 ad138b03a4ad2f78dd95dc5457e751e48f61f206
  49 691509c4459d109845889b3edd0215ef33425fe8
  50 8a798fc0eafdbc7cce23d2dd4ccc9e3e3975e1cd
  51 6fcc659da94ecf07191e985c623495f262e58a4d
  52 7546241e7acb1b68c929c69c9b34f3df72744106
  53 866ecf4ec1ce42bb6fa7b9128097797cf5df7d66
  54 3b2f6459f9eca190a6e67a81cf901170113aa63f
  55 3d13328f3434db2ed9498831ce6fd2c5018ce430
  ```

- [ ] 0.4 Inventory working controller, bar-series, workflow, and dependency behavior; record discrepancies with the two pending related proposals without rewriting them (B, C, P, W).
  Partial verification: Rebuilt installed runtime exposes eight stable Gamepad
  objects, slots 0-7, `GamepadButton.SOUTH`, both gamepad handlers, controller
  filtering configuration, and default axis deadzone approximately 0.15.
  The pending controller proposal still leaves M1/M2 unchecked and describes
  older names; do not infer missing runtime APIs from its status.
  PlotColorBars exposes `value_space="data"|"normalized"` and
  `normalized_max_fraction`, despite the independent normalized proposal's
  unchecked implementation tasks. Its draw loop resolves attached-axis limits
  during drawing; live pan/zoom correctness is not yet measured.
  `tests/test_fork_regressions.py` adds 25 passing runtime API/configuration
  cases for stable slots, empty disconnected state, handler defaults/filter
  validation, both bar orientations, all anchors, both value spaces, colors,
  borders, fit control, and invalid configuration. No input dispatch, rendered
  geometry, pan/zoom, or physical device coverage is claimed by these cases.
  `.github/workflows/build.yml` retains `workflow_dispatch`, Linux and Windows
  jobs, CPython free-threaded and PyPy targets, and Linux dependency packages.
  SDL pin is `c9a6709bd21750f1ad9597be21abace78c6378c9` (3.2.16); ImPlot pin
  is `78ca3a52915f74394b8f710ffde40a55efe760e6`.
  `build_SDL/CMakeCache.txt` confirms `SDL_JOYSTICK=ON`, `SDL_HAPTIC=ON`,
  `SDL_PRESEED=OFF`. Backend initializes SDL video and gamepad subsystems.
  Existing Linux optional-dependency disables in setup.py remain unchanged.
  Connected input, callback payloads/counts, and rendered bars remain unchecked.
- [x] 0.5 Record installed-package provenance, baseline build/tests, known failures, and required native-toolchain settings (B).
  Build verification (Windows, 2026-11-06): Before rebuilding, the installed
  package reported version `0.1.8`; this was stale and not used as baseline
  verification. From the repository root, ran
  `C:\Chris\DearCyGui\.venv\Scripts\python.exe -m pip install
  --no-build-isolation . --force-reinstall --no-cache-dir`: exit 0.
  Installed wheel `dearcygui-0.1.8+multicontroller.1-cp314-cp314-win_amd64.whl`,
  SHA256 `bad349dbd87651b5351b02f6dd6a22932ec2ee253f42945bd072ddb8b239121c`,
  built from approved implementation tree `5213cc7` (only approval docs edited).
  Outside source root (`C:\Chris`), `dearcygui.__file__` resolves to
  `C:\Chris\DearCyGui\.venv\Lib\site-packages\dearcygui\__init__.py`;
  distribution version is `0.1.8+multicontroller.1`; direct_url.json points to
  this repository. Interpreter is CPython 3.14.0, MSC v.1944, AMD64, GIL enabled.
  Effective environment: Cython 3.2.4, setuptools 82.0.1, wheel 0.46.3;
  click/cmake have no venv distribution metadata, but the canonical build
  succeeded with system CMake at `C:\Program Files\CMake\bin\cmake.exe`.
  This differs from the documented Cython 3.1.6 pin; no dependencies changed.
  CMake selected Visual Studio 17 2022 at
  `C:\Program Files\Microsoft Visual Studio\2022\Community`.

  Baseline tests: From `C:\Chris`, using the absolute venv interpreter, ran
  `-m pytest -q --maxfail=3 --import-mode=importlib` with absolute paths to
  `test_asyncio.py test_viewport.py test_gc.py test_shutdown.py`:
  **57 passed, 6 skipped, 3 failed** in 10.36s; early-stop means this did not
  exercise all four files. Failures:
  - `TestAsyncThreadPoolExecutor::test_graceful_cancellation`: task did not
    receive cancellation. Source 03 replaces cancelling-thread loop lookup
    with `task.get_loop().call_soon_threadsafe(task.cancel)`, directly addressing
    this observed baseline failure; the patch has not been applied.
  - `TestMultipleViewports::test_multiple_viewports_contexts`: requested second
    width 550 observed as 549, with display scaling 1.25.
  - `test_viewport_singlethreaded_wake`: fifty 0.01s delays took approximately
    0.070s rather than the required >0.4s.

  Separately ran `-m pytest -q --import-mode=importlib` with absolute paths to
  `test_gc.py test_shutdown.py test_sizing.py test_widgets.py`:
  **86 passed, 2 skipped, 5 xfailed, 1 failed** in 22.82s.
  `test_hanging_scenario_detection` failed because Windows subprocess termination
  returned code 1, while the test accepts only 0 or POSIX -15.
  New protected cases: same command with `tests/test_fork_regressions.py`:
  **25 passed** in 2.88s.
  Baseline warnings include cross-thread viewport deallocation; the standalone
  display smoke also reported an AutoFont callback attempting to schedule work
  during interpreter shutdown. These predate upstream integration.

  Evidence: session `files/baseline-build.log`, `files/baseline-pytest.log`,
  `files/baseline-lifecycle-pytest.log`.   User accepted these pre-existing failures as the comparison baseline on
  2026-11-06. No source commit has been applied at baseline recording.
- [ ] 0.6 Inventory hardware/virtual devices, external consumer availability, display requirements, CI/free-threaded environments, and approval for optional external runs. Add focused regression cases for protected behavior where missing (C, V, T).
  Partial inventory: One SDL display is reported; hidden viewport initialization
  and one render frame succeeded. No connected controllers were discovered
  before or after initialization. Physical 1/2/8-device, hot-plug, background
  input, edge timing, axis ranges, and callback payload checks remain unavailable.
  SDL is statically linked; no existing Python virtual-controller injection
  harness was found. A separate SDL DLL would not prove input in this installed
  extension's SDL instance. Same-instance virtual-device testing remains pending.
  The inspected venv interpreter is GIL-enabled, not a free-threaded test.
  No Linux or remote CI run has been performed or authorized. Directory listing
  confirms `C:\Chris\DearCyFi_Demo` exists; its revision/content was not inspected
  or run. DrawInWindow3D consumer availability is not established. External
  consumer runs, visual checks, and unresolved C/V/T gates remain unchecked.

## 1. Stage A: Initial upstream updates and dependencies

Suggested model: GPT-5.3-Codex — focused version, async, and native-build changes
with targeted verification.

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

Suggested model: Claude Opus 5.5 — reason across lifecycle, layout, and widget
dependencies while adapting upstream changes to the older fork implementation.

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

Suggested model: Claude Opus 5.5 — trace frame/event ordering across backend,
viewport, and drawing state, then drive the focused regression gates.

- [ ] 26 `8777919` Viewport variable refactor: update all internal references consistently; preserve gamepad objects, begin-frame hook, public properties and custom plots (V, C, P).
- [ ] 27 `79a37dd` Presentation skip logic: reconcile backend/header/declaration changes with gamepad events and edge ordering; check idle/wake and two manual viewports (V, C).
- [ ] 28 `c9241e0` Layout redraw loop: test bounded settling and no redraw loop during input/resize (L, V).
- [ ] 29 `5252285` Layout content position: assert nested content origins and sizing results (L).
- [ ] 30 `6e7b9e6` DraggableBar initial position: verify starting value and first drag (L, P).
- [ ] 31 `3072d58` DrawInWindow draw-state restoration: verify nested draw state, subsequent siblings, and DrawingList swaps (D, V).
- [ ] C.gate Pass C/V/L/P and relevant D cases; record edge/callback counts, idle/wake behavior and checkpoint before October changes.

## 4. Stage D: Drawing, safety, and deliberate API removals

Suggested model: Claude Opus 5.5 — coordinate rendering semantics, Cython/API
removals, caller migrations, and declarations without losing fork behavior.

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

Suggested model: Claude Opus 5.5 — reconcile callback types, dispatch behavior,
exceptions, exports, and generated stubs across the package.

- [ ] 44 `5f50063` Typed callback values: integrate core/handler/declaration changes without altering existing gamepad tuple payloads or argument ordering; inspect removed helpers before adapting calls (T, C, A).
- [ ] 45 `89dea7f` Typing/export/build registration: include callback module in packaging, regenerate/merge stubs retaining custom exports, and verify plots (T, W, P).
- [ ] 46 `53668da` Exception handling: check ordinary errors remain visible and termination/cancellation exceptions propagate as intended (T, A).
- [ ] 47 `7b1ea05` uiItem callbacks: verify real value payloads and callback arities (T).
- [ ] 48 `ad138b0` Follow-up utilities/tables/stubs: inspect every consumer and run draggable/window/node/widget/table checks (T, L).
- [ ] 49 `691509c` Pattern cache and callback fixes: verify cache invalidation, texture behavior, handlers, plots, utilities and stubs (D, T, C, P).
- [ ] E.gate Build the complete callback migration; pass T/C/A/P, record exact gamepad payload types/counts and installed export/stub checks, then checkpoint.

## 6. Stage F: Font, sizing, wake, and release cleanup

Suggested model: GPT-5.3-Codex — implement the bounded fixes and tests; use
measured frame and geometry evidence rather than source inspection alone.

- [ ] 50 `8a798fc` Reloaded font spacing: verify changed space advances/layout and markdown invalidation (D, L).
- [ ] 51 `6fcc659` Bold examples: inspect markdown implementation hunk as well as documentation; test behavior if executable changes are present (D).
- [ ] 52 `7546241` Negative widget/zero child sizing: assert layout geometry and distinguish negative DrawText screen-space sizing (L, D).
- [ ] 53 `866ecf4` Wake over-rendering: measure presented frames/settling behavior and repeat controller event-order/multi-viewport checks (V, C).
- [ ] 54 `3b2f645` Correct GPU-submission comment: confirm comment-only patch and accurate wording.
- [ ] 55 `3d13328` Release TODO cleanup: inspect all hunks and removed utils/layout.py; verify no import/caller regressions and do not assume title means documentation-only (D, L, T, A).
- [ ] F.gate Pass stage-specific and cumulative C/V/P tests, record final cleanup disposition and checkpoint.

## 7. Final validation and handoff

Suggested model: Claude Opus 5.5 — audit the source-to-result records and
verification evidence; do not substitute model review for required builds,
hardware checks, or user approval.

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
