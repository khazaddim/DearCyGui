# Design

> Source: openspec\changes\add-multi-controller-support\design.md

# Design: Multi-Controller Support

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Python Application                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  GamepadButtonHandler(controller=0, button=FACE_DOWN, ...)  │   │
│  │  GamepadAxisHandler(controller=1, axis=LEFT_X, ...)         │   │
│  │  viewport.gamepads → [Gamepad(id=0), Gamepad(id=1), ...]    │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Cython Binding Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  handler.pyx │  │   core.pyx   │  │       types.pyx          │  │
│  │  (handlers)  │  │  (Gamepad)   │  │  (GamepadButton/Axis)    │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    C++ Backend Layer                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              sdl3_gl3_backend.cpp                           │   │
│  │  • GamepadState struct per controller                       │   │
│  │  • SDL_EVENT_GAMEPAD_BUTTON_DOWN/UP capture                 │   │
│  │  • SDL_EVENT_GAMEPAD_AXIS_MOTION capture                    │   │
│  │  • SDL_EVENT_GAMEPAD_ADDED/REMOVED tracking                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           SDL3                                      │
│         (events include SDL_JoystickID for each controller)         │
└─────────────────────────────────────────────────────────────────────┘
```

## Key Design Decisions

### 1. Controller Identity via Slot Index (not SDL_JoystickID)

**Decision**: Expose controllers as slot indices 0-7 rather than raw SDL_JoystickID values.

**Rationale**:
- SDL_JoystickID values are not stable across reconnections
- Slot indices provide predictable "player 1", "player 2" semantics
- Internal mapping tracks SDL_JoystickID → slot assignment
- When controller disconnects, slot becomes empty but index preserved

### 2. Separate from ImGui Gamepad Abstraction

**Decision**: New gamepad API operates independently of ImGui's gamepad handling.

**Rationale**:
- ImGui merges all controllers into one virtual gamepad
- ImGui's gamepad is designed for UI navigation, not game input
- First controller continues to drive ImGui navigation (AutoFirst mode unchanged)
- Game logic uses new direct API for per-controller input

### 3. Event-Driven + Polling Hybrid

**Decision**: Support both callback-based handlers AND direct state queries.

**Rationale**:
- Callbacks (`GamepadButtonHandler`) for event-driven game logic
- Direct queries (`gamepad.is_button_pressed()`) for game loops polling state
- Both patterns are common in game development

### 4. Deadzone Handling in Handlers

**Decision**: `GamepadAxisHandler` includes configurable deadzone parameter.

**Rationale**:
- Analog sticks have drift near center position
- Without deadzone, callbacks fire constantly with noise
- Default deadzone of 0.15 (15%) eliminates most drift
- Can be set to 0.0 for raw values if needed

## C++ Data Structures

```cpp
// Maximum supported controllers (matches Windows XInput limit)
static constexpr int MAX_GAMEPADS = 8;

// Per-controller state
struct GamepadState {
    SDL_JoystickID sdl_id;           // SDL's internal ID (for event matching)
    SDL_Gamepad* handle;             // SDL gamepad handle
    char name[128];                  // Controller name
    
    // Button state
    bool buttons[SDL_GAMEPAD_BUTTON_COUNT];
    bool buttons_pressed[SDL_GAMEPAD_BUTTON_COUNT];   // "just pressed" this frame
    bool buttons_released[SDL_GAMEPAD_BUTTON_COUNT];  // "just released" this frame
    
    // Axis state (normalized -1.0 to 1.0, triggers 0.0 to 1.0)
    float axes[SDL_GAMEPAD_AXIS_COUNT];
    
    bool connected;
};

// Global state (owned by viewport or module-level)
struct GamepadManager {
    GamepadState gamepads[MAX_GAMEPADS];
    int gamepad_count;
    std::mutex mutex;  // Thread safety for connect/disconnect
};
```

## C API Functions (backend.h)

```cpp
// Query functions
int dcg_gamepad_count();
bool dcg_gamepad_connected(int slot);
const char* dcg_gamepad_name(int slot);

// Button state
bool dcg_gamepad_button_down(int slot, int button);
bool dcg_gamepad_button_pressed(int slot, int button);  // Just pressed this frame
bool dcg_gamepad_button_released(int slot, int button); // Just released this frame

// Axis state
float dcg_gamepad_axis(int slot, int axis);

// Frame management (called by viewport render loop)
void dcg_gamepad_begin_frame();  // Clear pressed/released flags
void dcg_gamepad_end_frame();
```

## Python API

### Enums (types.pyx)

```python
class GamepadButton(IntEnum):
    FACE_DOWN = 0       # A (Xbox) / Cross (PS)
    FACE_RIGHT = 1      # B (Xbox) / Circle (PS)
    FACE_LEFT = 2       # X (Xbox) / Square (PS)
    FACE_UP = 3         # Y (Xbox) / Triangle (PS)
    BACK = 4
    GUIDE = 5
    START = 6
    LEFT_STICK = 7
    RIGHT_STICK = 8
    LEFT_SHOULDER = 9
    RIGHT_SHOULDER = 10
    DPAD_UP = 11
    DPAD_DOWN = 12
    DPAD_LEFT = 13
    DPAD_RIGHT = 14
    MISC1 = 15
    PADDLE1 = 16
    PADDLE2 = 17
    PADDLE3 = 18
    PADDLE4 = 19
    TOUCHPAD = 20
    COUNT = 21

class GamepadAxis(IntEnum):
    LEFT_X = 0
    LEFT_Y = 1
    RIGHT_X = 2
    RIGHT_Y = 3
    LEFT_TRIGGER = 4
    RIGHT_TRIGGER = 5
    COUNT = 6
```

### Gamepad Class (core.pyx)

```python
cdef class Gamepad:
    cdef int _slot
    cdef Context _context
    
    @property
    def slot(self) -> int: ...
    
    @property
    def connected(self) -> bool: ...
    
    @property
    def name(self) -> str: ...
    
    def is_button_down(self, button: GamepadButton) -> bool: ...
    def is_button_pressed(self, button: GamepadButton) -> bool: ...
    def is_button_released(self, button: GamepadButton) -> bool: ...
    def get_axis(self, axis: GamepadAxis) -> float: ...
```

### Handlers (handler.pyx)

```python
cdef class GamepadButtonHandler(baseHandler):
    cdef int _controller      # -1 = any controller
    cdef int _button
    cdef bint _on_press       # True = fire on press, False = fire on release
    
    # callback receives (sender, controller_slot, button)

cdef class GamepadAxisHandler(baseHandler):
    cdef int _controller      # -1 = any controller
    cdef int _axis
    cdef float _deadzone
    cdef float _last_value    # For change detection
    
    # callback receives (sender, controller_slot, axis, value)
```

## Thread Safety Considerations

- Gamepad connect/disconnect events come from SDL event thread
- State queries may come from Python/render thread
- Use mutex around GamepadManager state modifications
- Copy state for queries to avoid holding lock during Python callbacks

## Testing Strategy

1. **Unit tests**: Mock SDL functions, verify state tracking
2. **Integration test**: Connect 2+ controllers, verify independent input
3. **Demo application**: Visual feedback showing all 8 controller slots with live input display
