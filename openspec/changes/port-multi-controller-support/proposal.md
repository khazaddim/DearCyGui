## Why

The `Game_Controller_Build` fork added independent input for eight controller slots, but its disconnected Git history prevents a normal merge into Axel Davy's current DearCyGui. After the smaller `port-plot-color-bars` port, recreate this cross-layer feature on upstream history without undoing upstream's viewport, callback, or lifecycle improvements.

## What Changes

- Enable controller-capable SDL builds on Windows and initialize `SDL_INIT_GAMEPAD` in the native backend; verify both gates rather than assuming Python API availability proves input works.
- Port startup discovery, stable slots, hot-plug cleanup, button held/press/release state, and normalized stick/trigger values through the native backend and Cython bridge.
- Add `Gamepad`, a cached eight-element `viewport.gamepads` tuple, `viewport.gamepad_count`, and the implemented `GamepadButton` / `GamepadAxis` enums.
- Add `GamepadButtonHandler` and `GamepadAxisHandler` with slot filtering, the fork's tuple callback payloads, and per-slot deadzone/change tracking.
- Adapt frame-edge ownership to upstream event waiting and multiple viewports so neither early event processing nor another viewport clears unobserved input.
- Keep legacy `Key.GAMEPAD*` handlers and ImGui's AutoFirst gamepad path; do not enable UI navigation automatically or merge all devices into the new API.
- Bring over `Fancy_Demo.py` with an unchanged provenance copy followed by a separate upstream adaptation, and add focused automated regressions and gamepad documentation/stubs.

This is additive to upstream's Python API. The original proposal's **BREAKING** label is not carried forward: it contradicted its compatibility section and does not describe the intended port.

## Capabilities

### New Capabilities

- `gamepad-input`: Eight stable controller slots, discovery/hot-plug lifecycle, polling, frame-latched button edges, filtered axis/button handlers, legacy compatibility, native enablement, and cross-viewport/event-loop correctness.

### Modified Capabilities

None. No main gamepad spec exists in this worktree, and the separate plot-color-bars requirements are unchanged.

## Impact

- Build: `setup.py` Windows SDL options and native archive relink dependencies. Retain current dependency pins, other platform settings, and packaging policy unless a specific controller blocker is demonstrated.
- Native/Cython: `dearcygui/backends/backend.h`, `backend.pxd`, `sdl3_gl3_backend.cpp`, and the corresponding `core`, `handler`, and `types` `.pyx` / `.pxd` files. Audit the compiled local `imgui_impl_sdl3.cpp` / `.h` path; do not replace it with an older or vendored copy.
- Public surfaces: runtime exports, generated `dearcygui/core.pyi`, relevant `stubs/` inputs/generator support, and `dearcygui/docs/gamepad.md`.
- Validation: focused controller tests, upstream event/async/lifecycle regressions, `Fancy_Demo.py`, and separate physical-controller observations. The color-bar port remains a prerequisite for the planned integration order, not a controller implementation dependency.
- Provenance: [original change](https://github.com/khazaddim/DearCyGui/tree/Game_Controller_Build/openspec/changes/add-multi-controller-support), [implementation commit index](../../references/prior-integration-findings.md#multi-controller-implementation), and [validation demo notes](../../project.md#feature-validation-demos). Source is frozen at `9db7a6b5537fc194229fcc9f20e389959ee5ff30`; detailed patch dispositions and validation gates are in the design.
