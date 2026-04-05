# Tasks: Add Multi-Controller Support

## Milestones Overview

| Milestone | Goal | Estimate |
|-----------|------|----------|
| **M1** | Basic polling: `viewport.gamepads[i].is_button_down()` works | 8-12 hrs |
| **M2** | Frame detection: `is_button_pressed()` / `is_button_released()` | 4-6 hrs |
| **M3** | Event handlers: `GamepadButtonHandler` with callbacks | 4-6 hrs |
| **M4** | Axis handlers: `GamepadAxisHandler` with deadzone | 4-6 hrs |

**Note:** For an RPG, Milestone 1 may be sufficient — you can poll button state each frame in your game loop.

---

## Milestone 1: Basic Polling Support

**Goal:** `viewport.gamepads[i].is_button_down(button)` and `get_axis(axis)` work for up to 8 controllers.

### 1.1 C++ Backend - Core Structure
- [ ] Define `GamepadState` struct in `sdl3_gl3_backend.cpp`
- [ ] Define gamepad array with 8 controller slots
- [ ] Implement SDL_JoystickID → slot mapping functions
- [ ] Handle `SDL_EVENT_GAMEPAD_ADDED` - assign to first empty slot, open handle
- [ ] Handle `SDL_EVENT_GAMEPAD_REMOVED` - clear slot, close handle

### 1.2 C++ Backend - State Tracking
- [ ] Handle `SDL_EVENT_GAMEPAD_BUTTON_DOWN/UP` - update button state
- [ ] Handle `SDL_EVENT_GAMEPAD_AXIS_MOTION` - update axis state
- [ ] Implement query functions: `dcg_gamepad_count()`, `dcg_gamepad_connected()`, `dcg_gamepad_name()`
- [ ] Implement `dcg_gamepad_button_down()`, `dcg_gamepad_axis()`

### 1.3 C API Declarations
- [ ] Add function declarations to `backend.h`
- [ ] Define constants: `DCG_MAX_GAMEPADS`, button/axis counts

### 1.4 Cython Declarations
- [ ] Add `cdef extern` declarations in `backend.pxd` for C functions
- [ ] Add SDL gamepad button/axis constant declarations

### 1.5 Python Enums
- [ ] Add `GamepadButton` enum to `types.pyx`
- [ ] Add `GamepadAxis` enum to `types.pyx`
- [ ] Add corresponding declarations to `types.pxd`
- [ ] Update `__init__.py` exports

### 1.6 Gamepad Class
- [ ] Implement `Gamepad` cdef class in `core.pyx`
- [ ] Add `slot`, `connected`, `name` properties
- [ ] Add `is_button_down(button)` method
- [ ] Add `get_axis(axis)` method
- [ ] Add declarations to `core.pxd`

### 1.7 Viewport Integration
- [ ] Add `gamepads` property to viewport returning list of 8 `Gamepad` objects

### 1.8 Milestone 1 Verification
- [ ] Build and install package
- [ ] Create test script that prints button state for 2+ controllers
- [ ] Verify connect/disconnect updates `connected` property

---

## Milestone 2: Frame Detection

**Goal:** `is_button_pressed()` returns True only on the frame the button was pressed; `is_button_released()` for release.

### 2.1 C++ Backend - Frame Tracking
- [ ] Add `buttons_pressed[]` and `buttons_released[]` arrays to GamepadState
- [ ] Implement `dcg_gamepad_begin_frame()` - clear pressed/released flags
- [ ] Update button event handling to set pressed/released flags
- [ ] Implement `dcg_gamepad_button_pressed()`, `dcg_gamepad_button_released()`

### 2.2 Cython/Python Updates
- [ ] Add `cdef extern` for new C functions in `backend.pxd`
- [ ] Add `is_button_pressed()`, `is_button_released()` methods to `Gamepad` class

### 2.3 Viewport Frame Hooks
- [ ] Call `dcg_gamepad_begin_frame()` at start of render frame

### 2.4 Milestone 2 Verification
- [ ] Test that `is_button_pressed()` fires exactly once per press
- [ ] Test that `is_button_released()` fires exactly once per release
- [ ] Test rapid button mashing doesn't miss events

---

## Milestone 3: Button Event Handlers

**Goal:** `GamepadButtonHandler` fires callbacks when buttons are pressed/released, with per-controller filtering.

### 3.1 Handler Implementation
- [ ] Implement `GamepadButtonHandler` cdef class in `handler.pyx`
- [ ] Support `controller` parameter (-1 for any, 0-7 for specific)
- [ ] Support `button` parameter (GamepadButton enum)
- [ ] Support `on_press` parameter (default True; False for release)
- [ ] Implement `check()` method following existing handler patterns
- [ ] Fire callback with controller slot info

### 3.2 Declarations and Exports
- [ ] Add declarations to `handler.pxd`
- [ ] Update `__init__.py` exports
- [ ] Add to type stubs

### 3.3 Milestone 3 Verification
- [ ] Test handler fires for specific controller only
- [ ] Test handler with `controller=None` fires for any controller
- [ ] Test callback receives correct controller slot

---

## Milestone 4: Axis Event Handlers

**Goal:** `GamepadAxisHandler` fires callbacks when analog values change, with deadzone filtering.

### 4.1 Handler Implementation
- [ ] Implement `GamepadAxisHandler` cdef class in `handler.pyx`
- [ ] Support `controller` parameter (-1 for any, 0-7 for specific)
- [ ] Support `axis` parameter (GamepadAxis enum)
- [ ] Support `deadzone` parameter (default 0.15)
- [ ] Track `_last_value` for change detection
- [ ] Implement `check()` method - fire callback when value changes beyond deadzone
- [ ] Fire callback with (controller_slot, axis_value)

### 4.2 Declarations and Exports
- [ ] Add declarations to `handler.pxd`
- [ ] Update `__init__.py` exports
- [ ] Add to type stubs

### 4.3 Milestone 4 Verification
- [ ] Test deadzone filtering prevents noise callbacks
- [ ] Test axis handler fires with correct values
- [ ] Test trigger axes (0.0 to 1.0 range)

---

## Post-Milestone Tasks

### Type Stubs
- [ ] Add `GamepadButton` and `GamepadAxis` to `types.pyi`
- [ ] Add `Gamepad` class to `core.pyi`
- [ ] Add `GamepadButtonHandler` and `GamepadAxisHandler` to handler stubs
- [ ] Update `viewport.gamepads` property in stubs

### Documentation
- [ ] Add gamepad section to `dearcygui/docs/` (new `gamepad.md` or in `basics.md`)
- [ ] Document migration from `KeyPressHandler` gamepad keys to new API
- [ ] Add code examples for common patterns (polling, handlers, "press start to join")

### Testing
- [ ] Create multi-controller demo showing all 8 slots with live input display
- [ ] Test with 0, 1, 2, and 8 controllers connected
- [ ] Test hot-plug: connect/disconnect during gameplay
