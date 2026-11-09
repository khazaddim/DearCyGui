## 1. Baseline and source provenance

- [ ] 1.1 Follow the planned color-bars-first order, record the implementation HEAD and frozen controller source `9db7a6b5537fc194229fcc9f20e389959ee5ff30`, and confirm both histories remain inspectable without importing the disconnected branch.
- [ ] 1.2 Build and baseline the current worktree using the local `dearcygui-build` skill. Record installed package/extension paths and targeted viewport, async, shutdown/GC, and available color-bar test results; distinguish fresh baseline failures from historical reports.
- [ ] 1.3 Copy `Fancy_Demo.py` unchanged from the frozen feature tip into the repository root and commit it alone as provenance. Verify its Git blob matches the source; keep all upstream adaptations for a later commit.
- [ ] 1.4 Confirm the reviewed commit dispositions in the design against the implementation baseline, including M1's Windows C++ initialization hunk, the local compiled ImGui backend path, and relevant relink dependencies. Record any newly discovered port-specific differences.

## 2. Controller-capable SDL build and native startup

- [ ] 2.1 Remove Windows joystick/haptic disables in `setup.py`, retain `SDL_PRESEED=OFF` and existing platform/dependency settings, and add SDL/FreeType archive rebuild dependencies to the extension.
- [ ] 2.2 Adapt M1's C++ startup gate to initialize video plus gamepad on Windows, keeping explicit initialization-error reporting instead of its silent video-only fallback. Report SDL device-open errors through existing mechanisms.
- [ ] 2.3 Rebuild and inspect effective SDL CMake cache settings and the installed extension's native linkage. Verify a changed native archive causes extension relinking; record concrete evidence, not merely a successful pip exit.

## 3. Native device registry and polling bridge

- [ ] 3.1 Port bounded controller storage, SDL-ID-to-lowest-free-slot mapping, startup discovery, duplicate/overflow handling, and hot-plug open/close operations. Use SDL-derived or compile-time-checked button/axis bounds.
- [ ] 3.2 Initialize current button/axis levels on discovery without synthetic historical presses, and normalize sticks/triggers within their documented ranges, including SDL signed extrema.
- [ ] 3.3 Add manager synchronization and safe copied-name queries for queued readers. Integrate final-viewport cleanup/recreation while preserving surviving viewports and ImGui's own handle ownership.
- [ ] 3.4 Wire native query declarations through `backend.h` / `backend.pxd`, then port public `types.pxd` enums and shared `types.pyx` conversion helpers. Verify the 21 button/six axis numeric mappings against current SDL.
- [ ] 3.5 Port `Gamepad`, the cached eight-object `Viewport.gamepads` tuple, `gamepad_count`, and matching `core.pxd` fields. Validate public slot/enum inputs; preserve neutral disconnected queries and runtime exports.
- [ ] 3.6 Add focused no-device/API tests in `tests/test_gamepad_input.py` for tuple/object identity, count, read-only properties, disconnected defaults, conversion/invalid inputs, and enum mappings. Adapt only relevant old fork cases using current fixture cleanup.

## 4. Deterministic input and frame lifecycle

- [ ] 4.1 Establish virtual devices/event injection in the extension's statically linked SDL instance, using a minimal private test bridge only if needed. Prove input reaches production event processing; do not use a separate SDL DLL or a public simulator API.
- [ ] 4.2 Port M2 transition-based OR-latched edges and implement bounded per-viewport pending/published snapshots. Wire owning-consumer queries and publication into event/render boundaries without global begin-frame erasure.
- [ ] 4.3 Preserve pending input from `wait_events()` and another viewport's event pump; mark participating viewports for needed rendering under `wait_for_input=True`, keeping upstream window and upload-context event behavior intact.
- [ ] 4.4 Test actual native-to-Python held/press/release state, repeated queries, duplicate down events, simultaneous down/up, next-frame clearing, and signed stick/trigger output ranges using deterministic input.
- [ ] 4.5 Test direct rendering, `wait_events()` before rendering, `run_viewport_loop()`, and two alternately rendered viewports. Assert each consumer sees its next-frame edges once without erased or replayed input.
- [ ] 4.6 Test preconnected/non-neutral discovery, two independent controllers, eight-slot capacity/overflow, duplicate adds, disconnect/reuse, final teardown/recreation, and queued name/level reads during lifecycle changes.

## 5. Button and axis handlers

- [ ] 5.1 Port M3 `GamepadButtonHandler` with existing handler locking/attachment/condition/enabled behavior, defaults, slot filtering, press/release selection, and exact `(int, GamepadButton)` callback data.
- [ ] 5.2 Port M4 `GamepadAxisHandler` with per-slot history, finite `[0,1]` deadzone validation, strict boundary/`1e-4` change semantics, selector/history resets, and exact `(int, float)` callback data.
- [ ] 5.3 Test callback sender/target/data types and counts for specific/any slots, simultaneous controllers, releases, held non-repeat, and disabled/conditional handlers. Verify non-mutating handler checks do not consume dispatch.
- [ ] 5.4 Test axis rest/noise, exact deadzone boundary, epsilon threshold, unchanged values, movement, return-to-zero, selector changes, disconnect neutralization, and clean slot reuse independently for multiple controllers.
- [ ] 5.5 Verify legacy `Key.GAMEPAD*` input through the existing local ImGui AutoFirst path, while direct input remains independent of navigation/capture settings. Confirm keyboard/mouse and existing typed callback formats are unchanged.

## 6. Demo, documentation, and public stubs

- [ ] 6.1 Adapt the provenance demo in a separate commit to confirmed upstream layout/viewport/queue differences. Preserve event-driven buttons/axes, eight slot/name/count/history displays, fullscreen controls, and the pannable/zoomable plot probe.
- [ ] 6.2 Keep the demo's direct async render loop and connection/name-only polling exception. Update its old lost-edge warning after helper-loop tests pass; surface failures and add orderly shutdown rather than masking missed input with polling.
- [ ] 6.3 Adapt `dearcygui/docs/gamepad.md` from the original guide, correcting enum names, tuple/count behavior, callback shapes, frame/loop semantics, deadzone/normalization, capacity/driver limits, and legacy navigation behavior. Link the supplied validation demo from project documentation.
- [ ] 6.4 Merge relevant `stubs/` inputs and generate public stubs from the rebuilt installed module. Make only necessary generator adjustments for `Gamepad(Context, slot)`; review and exclude unrelated churn.
- [ ] 6.5 Verify runtime exports, generated stubs, documentation examples, handler defaults, and callback tuple types agree, using existing checking tools and focused tests.

## 7. Final regression and interactive gates

- [ ] 7.1 Rebuild the final extension using the local skill and run focused controller tests plus related `test_viewport.py`, `test_asyncio.py`, `test_shutdown.py`, `test_gc.py`, and color-bar regressions. Escalate only when targeted results warrant it; record fresh failures and do not import old waivers.
- [ ] 7.2 Run the installed-package demo with zero/one/two physical controllers as available. Require the two-controller interactive gate for completion: verify slot separation, held/press/release counts, D-pad, sticks/triggers, deadzone/center return, startup-connected devices, and hot-plug/reuse.
- [ ] 7.3 During two-controller demo validation, pan/zoom the plot, resize/toggle fullscreen, and exercise async input/render coexistence. Confirm visible updates are callback-driven and there are no missed/duplicated button edges or shutdown errors.
- [ ] 7.4 Record reproducible commands, source/build/package identity, deterministic input mechanism, device/driver counts, callback shapes/counts, and manual observations in task evidence. Mark unavailable hardware/platform checks as unverified and keep required unfinished gates unchecked.
- [ ] 7.5 Review the final diff for unrelated upstream/fork/dependency/generated-code changes, ensure hand-written backend C++ stays tracked, validate this OpenSpec change, and archive only when required automated and interactive gates are complete.
