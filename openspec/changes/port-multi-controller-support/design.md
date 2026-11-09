## Context

This is an upstream-first feature port, not a merge of the abandoned integration branch. The planning baseline is `d741df95b502818dee9932ba101b1263e435fee1`; the original feature source is `Game_Controller_Build` at `9db7a6b5537fc194229fcc9f20e389959ee5ff30`. Both histories are locally available without switching worktrees. Re-record the implementation baseline after the separate color-bar port lands.

Read the [original proposal/design/spec/tasks](https://github.com/khazaddim/DearCyGui/tree/Game_Controller_Build/openspec/changes/add-multi-controller-support), but use implemented code to resolve stale wording:

| Original wording | Implemented contract to port |
|------------------|------------------------------|
| List of connected controllers / up to eight objects | Cached tuple of exactly eight stable objects, including disconnected slots; separate `gamepad_count` |
| `FACE_DOWN/RIGHT/LEFT/UP`, `PADDLE1..4` | `SOUTH/EAST/WEST/NORTH`, `RIGHT_PADDLE1`, `LEFT_PADDLE1`, `RIGHT_PADDLE2`, `LEFT_PADDLE2` |
| Enums described as Python definitions in `types.pyx` | Public `cpdef enum class` definitions in `types.pxd`, with conversion helpers in `types.pyx` |
| Button callback contains only a slot | Third callback argument is `(int slot, GamepadButton button)` |
| Axis callback fires beyond deadzone | Per-slot filtered-value changes greater than `1e-4`, including one return-to-zero callback |
| Global manager or viewport ownership left undecided | Source uses unsynchronized process-global state; per-viewport edge ownership must be adapted |
| `dcg_gamepad_end_frame()` and connection callback ideas | Not implemented public APIs; do not introduce them as port features |
| Eight slots equated to Windows XInput capacity | Eight is the library capacity, not a promise that every driver supports eight physical devices |

### Reviewed patch provenance and dispositions

All original commits below are reachable from the frozen feature tip. Adapt the relevant hunks, not whole commits or old source files.

| Commit | Disposition |
|--------|-------------|
| [`976e6bb`](https://github.com/khazaddim/DearCyGui/commit/976e6bbc7f86b6deab977eb4eb6d90c8b2ed62ec) | Port Windows SDL joystick/haptic enablement in `setup.py`; retain `SDL_PRESEED=OFF`. Replace the commented-out disable with a clear effective configuration. |
| [`14642b4` M1](https://github.com/khazaddim/DearCyGui/commit/14642b4e0ff2fd7c3d33f238b8a01d2498794ff2) | Port native slots, queries, discovery/events, bridge, enums, and polling. Crucially removes the Windows video-only `SDL_Init` branch in C++; do not omit that hunk. Adapt its silent video-only fallback, global storage, and axis division. |
| [`ae4d433` M2](https://github.com/khazaddim/DearCyGui/commit/ae4d433a48d0c10698a638276a771612d9b30a24) | Port transition-based, OR-latched press/release flags. Adapt global begin-frame clearing to pending/per-viewport snapshots. Exclude EPUB/study material. |
| [`a738e29` M3](https://github.com/khazaddim/DearCyGui/commit/a738e2935bdf7a5c05b46cf0dc30fc09c9d35882) | Port button handlers, filtering, defaults, and enum tuple payloads. Do not copy generated-C++ deletions. |
| [`34fdc1e` M4](https://github.com/khazaddim/DearCyGui/commit/34fdc1e215612b2c91daa4846fe8cd9149bb8f80) | Port axis handlers, per-slot history, deadzone and epsilon semantics. Validate non-finite configuration and lifecycle/reset behavior. |
| [`8b82b57`](https://github.com/khazaddim/DearCyGui/commit/8b82b57d2336ad31795d934a9b0ca304cd8031c0) | Adapt gamepad documentation and stub inputs. Do not replace upstream's generated `core.pyi` wholesale. |
| [`111dfb0`](https://github.com/khazaddim/DearCyGui/commit/111dfb0dbe9ed21e62f306e0f20ae01311af9404) and later demo-only commits | Use the final frozen-tip `Fancy_Demo.py`, including plot probe, fullscreen controls and side-by-side panes, as the provenance copy. |

`3aac4c5` ("Game Controller build 1") changes fonts/ignore rules, not the required native enablement. `62c8ecf` adds ImGui study notes, not an ImGui C++ implementation patch. `d4ef4a7` restored hand-written backend files lost during old history cleanup; current upstream already tracks them. No subsequent original feature edits to the local `imgui_impl_sdl3.cpp` were found after that restoration. Audit its existing AutoFirst behavior, but do not invent a required wholesale ImGui backend patch.

The earlier local integration's [`c14bfc1`](../../references/prior-integration-findings.md#concrete-build-hazards-to-revisit) contains a relevant `Extension.depends=[sdl3_lib, FT_lib]` relink correction. It is separate provenance from the original feature and is not a reason to copy dependency pins, wheel changes, fork versioning, or the old 55-commit integration plan.

### Current upstream integration points

- `setup.py` still disables Windows joystick/haptic support. `SDLViewport::create()` still initializes video only under `_WIN32`; both must change.
- The compiled local `dearcygui/backends/imgui_impl_sdl3.cpp` already discovers gamepads in AutoFirst mode and updates ImGui gamepad keys. Preserve that path and window-event routing.
- `Viewport.render_frame()` and `Viewport.wait_events()` both call native `processEvents()`. `run_viewport_loop()` can call `wait_events()` before rendering, explaining the lost-button warning in the source demo.
- `Context.queue_callback(..., object data)` and `Callback.__call__` still accept arbitrary objects. Existing upstream handlers now construct typed callback values, but controller tuples can be preserved without weakening or replacing those types.
- SDL initialization/event pumping is process-shared and main-thread constrained. Python callbacks run on a queue and can query state from another thread. The source's raw global arrays and borrowed name pointers are not a sufficient synchronization model.

## Goals / Non-Goals

**Goals:**

- Preserve the implemented Python controller API and its callback shapes on upstream history.
- Support eight independent stable slots, startup discovery, hot-plug, polling, and handlers.
- Make native enablement, normalized output ranges, frame consumption, resource lifetime, and concurrent reads demonstrably correct.
- Keep existing input/render/async behavior and the separately ported color bars intact.
- Produce reviewable feature commits, aligned docs/stubs, and reproducible automated/manual evidence.

**Non-Goals:**

- New player-assignment policy, raw joystick APIs, rumble/haptics APIs, controller connection handlers, or more than eight slots.
- A persistent event stream reporting every transition independently. Frame edges remain boolean latches.
- New typed controller callback-value classes or renaming implemented enums to match the stale proposal.
- Re-enabling UI navigation by default, changing ImGui's AutoFirst policy, or rewriting unrelated SDL window-event routing.
- Dependency upgrades, wheel/platform policy changes, free-threading certification, or upstream PR submission.

## Decisions

### 1. Enable the full native path and make failures visible

Remove Windows joystick/haptic disables and keep the preseed workaround. Confirm effective SDL CMake cache settings and the extension's linked native archive, not just the command line. Register SDL/FreeType archives as extension rebuild dependencies so changing the SDL build cannot silently leave the old extension installed.

Initialize video plus gamepad on Windows as on other supported platforms, with startup discovery before controller use. Preserve upstream's explicit native initialization error reporting; do not copy M1's silent fallback to video-only success. An SDL gamepad initialization or device-open failure must retain/report the SDL error through existing error mechanisms. Zero connected devices and exceeding eight tracked slots are normal states, not initialization failures.

Alternative: copy only the Python API or only `setup.py`. Rejected because controller input remains disabled at the other gate. Changing vendored ImGui/SDL files or dependency pins without a reproduced blocker is also rejected.

### 2. Shared device manager, stable Python handles, bounded storage

Maintain one native device registry for the extension's SDL instance, mapping SDL joystick instance IDs to the lowest free slot. Open tracked devices once for this manager, close them on removal, and close/reset remaining devices when the last participating viewport is destroyed. ImGui retains its own existing handle ownership; do not close its handles from the new manager.

Create the eight Python `Gamepad` objects lazily once per viewport, retaining their identity across discovery/removal. They identify slots, not permanent physical devices. New occupants start without the previous occupant's name, levels, edges, or handler history. Discovery must initialize current button/axis levels without synthesizing historical presses, including devices already held at startup.

Use SDL button/axis counts for internal bounds (or checked compile-time equivalents), not the source's unexplained hard-coded 26/6. Preserve the public 21 named button values and six axes, verifying their numeric SDL mappings. Keep overflow bounded and documented; it does not reorder existing slots or guarantee driver capacity.

Alternative: compact connected-only objects or one separately opened registry per viewport. Rejected because these break slot identity or duplicate native ownership.

### 3. Protect reads and publish per-viewport frame edges

Device levels/identity are shared; each live viewport owns pending edge latches and its published frame snapshot. Process a native gamepad event once, updating the manager and OR-latching its transitions into pending state for participating viewports. At a viewport's input/render boundary:

1. Retire that viewport's previous published edges, never another viewport's pending input.
2. Preserve pending edges collected by `wait_events()` or another viewport's event pump.
3. Process SDL events and then publish the viewport's pending edges for polling/handlers in this frame.
4. Consume those pending edges only for that viewport; further frames without transitions publish no edges.

A down/up within one frame sets both latches and leaves the held state false. Repeated down events do not create extra rising edges. This is intentionally frame aggregation, not an event-count queue. A newly created viewport does not replay historical edges.

Use manager synchronization for cross-thread level/name reads and snapshot publication, respecting upstream main-thread and lock ordering. Copy names while protected before UTF-8 decoding; do not expose a pointer into mutable native storage to queued callbacks. Native queries/declarations can gain an owning viewport/consumer parameter where needed; the original internal context-free C API is not a public compatibility constraint.

Alternative: copy `dcg_gamepad_begin_frame()` unchanged. Rejected because it clears all controllers before handlers can observe input pumped by `wait_events()` or another viewport. Fix the lifecycle rather than requiring all users to bypass the async helper.

### 4. Preserve public behavior and tighten coupled invalid-input handling

Port enum conversion helpers using repository patterns: polling accepts enum values, case-insensitive valid names, and valid numeric enum values; handler button/axis setters accept enum values or valid names as in the source. Preserve handler defaults (`controller=-1`, button `SOUTH`, `on_press=True`, axis `LEFT_X`, deadzone `0.15`). `controller=None` normalizes to `-1`.

Use existing handlers' locking, enabled checks, attachment/condition semantics, and queue submission. Button data is exactly `(slot, GamepadButton)` and axis data exactly `(slot, float)`, with handler as sender and attached item as target. Keep upstream typed payloads for existing handlers unchanged.

Validate public slots and enum inputs explicitly; disconnected valid slots still return neutral state. Deadzone must be finite and in `[0, 1]`. Preserve `abs(raw) < deadzone` filtering (the boundary is outside), followed by a strict filtered-value change threshold of `1e-4`. Normalize signed stick endpoints without `-32768 / 32767` escaping `[-1, 1]`; clamp/normalize triggers to `[0, 1]`.

Axis history is independent per slot and reset when controller/axis selection changes. Disconnecting a nonzero reported axis emits at most one neutral callback; reuse starts cleanly. Repeated non-mutating `check_state()` calls must not consume an event before `run_handler()`.

Alternative: new typed controller payloads. Rejected for this port because tuple unpacking is used throughout the final validation demo and the current queue already supports it. Reject silently accepting NaN or out-of-range public inputs despite the source's gaps.

### 5. Preserve legacy and upstream behavior

Continue passing relevant events to the local ImGui SDL backend and keep AutoFirst. The new per-slot data must not be gated by ImGui navigation/capture settings. Existing gamepad key handlers continue to receive the first ImGui controller, while other controllers stay distinguishable only through the new API. Do not turn on navigation flags globally.

Mark participating viewports for input-driven rendering when needed so `wait_for_input` does not suppress controller callbacks. Keep unrelated window/upload-context routing and viewport refactors intact.

Alternative: use ImGui's merged keys for the new API. Rejected because controller identity is lost.

### 6. Demo provenance and layered validation

First copy the final `Fancy_Demo.py` unchanged from the frozen feature tip in its own implementation commit. Adapt upstream-incompatible `HorizontalLayout(no_wrap=...)` / `ChildWindow(resizable_x=...)` and any other confirmed API differences in a separate commit. Preserve its event-driven button/axis display, all eight slots, SDL names, counts/history, fullscreen control, and interactive plot probe.

The original `C:\Chris\DearCyGui\Fancy_Demo.py` matches that feature-tip version at planning review. It uses `AsyncPoolExecutor`, a direct `render_frame()` loop with `asyncio.sleep(1/120)`, and `wait_for_input=True`. Keep this mode, but update its obsolete lost-edge warning only after the `wait_events()`/helper tests pass. Connection/name polling via `RenderHandler` remains the sole polling exception; do not hide missed button callbacks by polling levels. Surface demo startup/callback failures and use orderly shutdown rather than presenting an exception as a successful validation.

Use focused `tests/test_gamepad_input.py`, adapting only useful controller cases from local `471ba7d:tests/test_fork_regressions.py`. Follow this worktree's queue/viewport/GC cleanup. Configuration tests without devices do not prove connected input.

Deterministic input tests must attach/inject through the same statically linked SDL instance as the extension. Prefer SDL virtual devices with a minimal private test bridge if required; do not add a public simulator API or depend on a separately loaded SDL DLL. Test the actual event-to-native-to-Cython-to-handler path, including two viewports and asynchronous queued reads. Model eight slots using virtual devices even if hardware/driver capacity is lower.

Generate public stubs using upstream's generator and relevant `stubs/` inputs, making a narrow generator adaptation if the non-item `Gamepad(Context, slot)` constructor needs it. Review the output and keep unrelated generated churn out. Merge relevant documentation from the original gamepad guide and correct names, tuple/frame semantics, normalization, supported loops, capacity limits, and navigation caveats.

Alternative: validate only imports or manual demo startup. Rejected because it misses disabled native support, lost edges, incorrect callback shapes, and stale linkage.

## Risks / Trade-offs

- **Shared SDL event pumping and lock order** -> Use bounded pending snapshots, respect the main-thread contract, and test alternating viewports, queued readers, and teardown without another viewport losing state.
- **Correctness adaptations exceed a mechanical replay** -> Isolate native lifetime/frame/normalization changes in reviewable commits and document differences from the original source.
- **Frame latches coalesce repeated transitions** -> Test simultaneous press/release visibility and exactly one callback per selected edge per handler/slot/frame; do not claim every physical transition is individually counted.
- **Static linkage hides stale SDL or external injection mistakes** -> Inspect effective cache/archive/extension evidence and exercise the extension's own SDL instance.
- **Disconnected or unrendered consumers retain stale edges** -> Clear disconnect/reuse state and unregister consumers on destruction; bound pending storage to eight slots rather than buffering events indefinitely.
- **Eight physical devices unavailable** -> Require deterministic capacity tests; separately record physical device counts/drivers and mark unperformed hardware/platform checks as unverified, not passed.
- **Old demo layout arguments and stub-generation assumptions** -> Adapt to upstream APIs rather than restoring old layout/core files, and test stub/runtime shape alignment.
- **Historical baseline failures** -> Establish a fresh baseline. Earlier integration approvals, skips, and successes are not waivers for this port.

## Migration Plan

1. Follow the planned color-bars-first order; record the new implementation baseline and focused upstream tests.
2. Commit the unchanged demo provenance copy, then port build/native support, polling/frame lifecycle, and handlers in coherent layers with tests.
3. Adapt the demo and documentation, regenerate stubs, and validate the installed extension, not source-shadowed imports.
4. Run deterministic connected-input tests, related upstream/color-bar regressions, and the manual demo matrix. Record commands, source/build identity, devices, output shapes/counts, and unverified gates in task evidence.
5. Archive only after required automated and interactive gates pass; do not promote/import the disconnected feature history. Roll back by reverting feature commits, rebuilding SDL/extension, and confirming upstream behavior. No existing Python caller migration is required.

## Open Questions

- Which physical controllers/drivers are available for the two-controller interactive gate? Confirm during implementation and arrange user-assisted validation if needed.
- Does the current build environment expose the statically linked SDL symbols for virtual-device tests, or require the minimal private bridge described above? Resolve before claiming connected-input coverage.
- Do any non-Windows controller builds need an additional narrowly justified build adaptation? Current Linux settings and platform policy must remain intact; cross-platform certification is not implied by Windows results.
