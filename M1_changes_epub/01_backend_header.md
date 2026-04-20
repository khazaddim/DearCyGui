# Layer 1: C++ Backend — Header File

## File: `dearcygui/backends/backend.h`

This is the **header file** — it declares data structures and function signatures that other files can see.

### Added: `GamepadState` struct

```cpp
static constexpr int DCG_MAX_GAMEPADS = 8;
static constexpr int DCG_MAX_GAMEPAD_BUTTONS = 26;  // SDL_GAMEPAD_BUTTON_COUNT
static constexpr int DCG_MAX_GAMEPAD_AXES = 6;      // SDL_GAMEPAD_AXIS_COUNT

struct GamepadState {
    SDL_JoystickID sdl_id = 0;       // SDL's internal ID for matching events
    SDL_Gamepad* handle = nullptr;    // SDL handle for querying name, etc.
    char name[128] = {};              // Human-readable controller name
    bool buttons[26] = {};            // Current button held state
    float axes[6] = {};              // Current axis values
    bool connected = false;          // Is a controller in this slot?
};
```

**Why?** We need somewhere to store the state of each controller. SDL sends us events ("button 3 on joystick 7 was pressed"), but we need to remember that state so Python can ask "is button 3 down right now?" at any time. The struct holds one controller's complete state. We allocate 8 of these — one per player slot.

**Why 8?** Matches the XInput limit on Windows and is plenty for local multiplayer.

**Why `SDL_JoystickID`?** SDL assigns each physical controller a numeric ID. When we get a button event, it tells us which `SDL_JoystickID` generated it, so we look up which slot that maps to.

### Added: C API function declarations

```cpp
int  dcg_gamepad_count();
bool dcg_gamepad_connected(int slot);
const char* dcg_gamepad_name(int slot);
bool dcg_gamepad_button_down(int slot, int button);
float dcg_gamepad_axis(int slot, int axis);
```

**Why?** These are the **query functions** that Cython will call. They take simple types (int, bool, float, const char*) because Cython can only call C/C++ functions with known signatures. The functions are declared here so both the `.cpp` implementation and the `.pxd` Cython declaration can reference them.
