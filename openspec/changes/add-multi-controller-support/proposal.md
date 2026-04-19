# Change: Add Multi-Controller Support

## Why
DearCyGui currently merges all gamepad input into a single virtual controller via ImGui's abstraction, making it impossible to distinguish which controller generated an input. This prevents development of local multiplayer games (up to 8 players) that require per-controller input handling.

## What Changes
- **BREAKING**: Gamepad input will no longer be exclusively routed through ImGui's `KeyPressHandler` for game logic (ImGui navigation still uses first controller)
- Add new `Gamepad` class exposing per-controller state (buttons, axes, name, connection status)
- Add `viewport.gamepads` property returning list of connected controllers
- Add `GamepadButtonHandler` for per-controller button events with controller filtering
- Add `GamepadAxisHandler` for per-controller analog input with deadzone support
- Add `GamepadButton` and `GamepadAxis` enums mapping to SDL3 gamepad constants
- Track gamepad connect/disconnect events via SDL3
- Update `Small_Input_Demo.py` milestone-by-milestone so it serves as a live validation harness during implementation

## Impact
- Affected specs: `gamepad-input` (new capability)
- Affected code:
  - `dearcygui/backends/sdl3_gl3_backend.cpp` - Gamepad state tracking, event capture
  - `dearcygui/backends/backend.h` - C API declarations
  - `dearcygui/backends/backend.pxd` - Cython declarations
  - `dearcygui/types.pyx` - New enums
  - `dearcygui/core.pyx` - Gamepad class, viewport.gamepads
  - `dearcygui/handler.pyx` - New handler classes
  - `Small_Input_Demo.py` - Incremental milestone validation and demo coverage
  - Corresponding `.pxd` files for all `.pyx` changes

## Compatibility
- Existing `KeyPressHandler` with `dcg.Key.GAMEPAD*` keys continues to work (uses first controller via ImGui)
- New API is additive; no existing code breaks unless relying on undocumented behavior
