# Tasks: Add Multi-Controller Support

## 1. C++ Backend Implementation

- [ ] Define `GamepadState` struct in `sdl3_gl3_backend.cpp`
- [ ] Define `GamepadManager` with array of 8 controller slots
- [ ] Implement SDL_JoystickID → slot mapping functions
- [ ] Handle `SDL_EVENT_GAMEPAD_ADDED` - assign to first empty slot
- [ ] Handle `SDL_EVENT_GAMEPAD_REMOVED` - clear slot, close handle
- [ ] Handle `SDL_EVENT_GAMEPAD_BUTTON_DOWN/UP` - update button state
- [ ] Handle `SDL_EVENT_GAMEPAD_AXIS_MOTION` - update axis state
- [ ] Implement `dcg_gamepad_begin_frame()` / `dcg_gamepad_end_frame()`
- [ ] Implement query functions (`dcg_gamepad_count`, `dcg_gamepad_button_down`, etc.)

## 2. C API Declarations

- [ ] Add function declarations to `backend.h`
- [ ] Add `GamepadState` struct to `backend.h` (or keep opaque)
- [ ] Define constants for MAX_GAMEPADS, button/axis counts

## 3. Cython Declarations

- [ ] Add `cdef extern` declarations in `backend.pxd` for all C functions
- [ ] Add enum declarations for SDL gamepad button/axis constants

## 4. Python Enums

- [ ] Add `GamepadButton` enum to `types.pyx`
- [ ] Add `GamepadAxis` enum to `types.pyx`
- [ ] Add corresponding declarations to `types.pxd`
- [ ] Update `__init__.py` exports

## 5. Gamepad Class

- [ ] Implement `Gamepad` cdef class in `core.pyx`
- [ ] Add `slot`, `connected`, `name` properties
- [ ] Add `is_button_down()`, `is_button_pressed()`, `is_button_released()` methods
- [ ] Add `get_axis()` method
- [ ] Add declarations to `core.pxd`

## 6. Viewport Integration

- [ ] Add `gamepads` property to viewport returning list of `Gamepad` objects
- [ ] Call `dcg_gamepad_begin_frame()` at start of frame
- [ ] Call `dcg_gamepad_end_frame()` at end of frame

## 7. Handler Classes

- [ ] Implement `GamepadButtonHandler` in `handler.pyx`
  - [ ] Support `controller` parameter (-1 for any)
  - [ ] Support `button` parameter
  - [ ] Support `on_press` parameter (default True)
  - [ ] Fire callback with controller slot info
- [ ] Implement `GamepadAxisHandler` in `handler.pyx`
  - [ ] Support `controller` parameter (-1 for any)
  - [ ] Support `axis` parameter
  - [ ] Support `deadzone` parameter (default 0.15)
  - [ ] Fire callback on value change beyond deadzone
- [ ] Add declarations to `handler.pxd`
- [ ] Update `__init__.py` exports

## 8. Type Stubs

- [ ] Add `GamepadButton` and `GamepadAxis` to `types.pyi` stub
- [ ] Add `Gamepad` class to `core.pyi` stub
- [ ] Add `GamepadButtonHandler` and `GamepadAxisHandler` to handler stubs
- [ ] Update `viewport.gamepads` property in stubs

## 9. Testing

- [ ] Create multi-controller demo showing all 8 slots
- [ ] Test connect/disconnect handling
- [ ] Test button press/release detection
- [ ] Test axis values and deadzone filtering
- [ ] Test "any controller" mode (`controller=-1`)

## 10. Documentation

- [ ] Add gamepad section to `dearcygui/docs/basics.md` or new `gamepad.md`
- [ ] Document migration from `KeyPressHandler` gamepad keys to new API
- [ ] Add code examples for common patterns
