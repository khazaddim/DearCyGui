# Layer 1: C++ Backend — Implementation

## File: `dearcygui/backends/sdl3_gl3_backend.cpp`

This is where the actual logic lives — event handling, state management, and the query function implementations.

### Added: Global gamepad state array

```cpp
static GamepadState g_gamepads[DCG_MAX_GAMEPADS];
```

**Why `static`?** This makes the array file-scoped (only visible inside this `.cpp` file). Other code accesses it through the query functions — not directly. This is encapsulation.

**Why global instead of per-viewport?** SDL gamepad events aren't window-specific — a button press doesn't "belong" to a particular window. Making it global means any viewport can read controller state, which matches how SDL works.

### Added: Slot mapping helper functions

```cpp
static int find_gamepad_slot(SDL_JoystickID id) {
    for (int i = 0; i < DCG_MAX_GAMEPADS; i++) {
        if (g_gamepads[i].connected && g_gamepads[i].sdl_id == id)
            return i;
    }
    return -1;
}

static int find_empty_slot() {
    for (int i = 0; i < DCG_MAX_GAMEPADS; i++) {
        if (!g_gamepads[i].connected)
            return i;
    }
    return -1;
}
```

**Why?** SDL identifies controllers by `SDL_JoystickID` (a number that can change between sessions). But our Python API uses slot indices 0-7 ("player 1", "player 2", etc.). These functions translate between the two systems:

- `find_gamepad_slot`: "Which slot has this SDL ID?" (used when processing events)
- `find_empty_slot`: "Where can I put a newly connected controller?"

### Added: Connect/disconnect handlers

```cpp
static void handle_gamepad_added(SDL_JoystickID id) { ... }
static void handle_gamepad_removed(SDL_JoystickID id) { ... }
```

**Why?** When you plug in a controller, SDL fires `SDL_EVENT_GAMEPAD_ADDED`. We need to:

1. Find an empty slot
2. Open an SDL handle to the controller (so we can read its name)
3. Store the mapping from SDL ID → slot
4. Mark the slot as connected

When you unplug, SDL fires `SDL_EVENT_GAMEPAD_REMOVED`. We:

1. Find which slot had that SDL ID
2. Close the SDL handle
3. Zero out the state
4. Mark disconnected

**Why `strncpy` for the name?** Safety — `SDL_GetGamepadName()` returns a pointer to SDL's internal buffer which could be any length. `strncpy` with a size limit prevents buffer overflow.

### Added: Query function implementations

```cpp
bool dcg_gamepad_button_down(int slot, int button) {
    if (slot < 0 || slot >= DCG_MAX_GAMEPADS) return false;
    if (button < 0 || button >= DCG_MAX_GAMEPAD_BUTTONS) return false;
    if (!g_gamepads[slot].connected) return false;
    return g_gamepads[slot].buttons[button];
}
```

**Why the bounds checks?** These functions are called from Python (through Cython). A Python user could pass any integer. Without bounds checking, `g_gamepads[-1]` or `g_gamepads[99]` would read random memory — crash or security vulnerability. We validate inputs and return safe defaults.

**Why return `false`/`0.0f` for disconnected?** Rather than throwing errors, disconnected controllers just report "nothing happening." This simplifies game loops — you don't need to check `connected` before every button query.

### Added: Event handling in `processEvents()`

```cpp
case SDL_EVENT_GAMEPAD_ADDED:
    handle_gamepad_added(event.gdevice.which);
    needsRefresh.store(true);
    break;
case SDL_EVENT_GAMEPAD_REMOVED:
    handle_gamepad_removed(event.gdevice.which);
    needsRefresh.store(true);
    break;
case SDL_EVENT_GAMEPAD_BUTTON_DOWN:
case SDL_EVENT_GAMEPAD_BUTTON_UP:
{
    int slot = find_gamepad_slot(event.gbutton.which);
    if (slot >= 0 && event.gbutton.button < DCG_MAX_GAMEPAD_BUTTONS) {
        g_gamepads[slot].buttons[event.gbutton.button] = event.gbutton.down;
    }
    needsRefresh.store(true);
    break;
}
case SDL_EVENT_GAMEPAD_AXIS_MOTION:
{
    int slot = find_gamepad_slot(event.gaxis.which);
    if (slot >= 0 && event.gaxis.axis < DCG_MAX_GAMEPAD_AXES) {
        float value = (float)event.gaxis.value / 32767.0f;
        g_gamepads[slot].axes[event.gaxis.axis] = value;
    }
    needsRefresh.store(true);
    break;
}
```

**Why in `processEvents()`?** This method is called every frame as part of `render_frame()`. It's where DearCyGui's existing event loop processes SDL events via a `switch` statement. We add new `case` branches for gamepad events, following the exact same pattern as keyboard/mouse.

**Why `needsRefresh.store(true)`?** This tells the rendering system "something changed, you need to actually draw." Without it, `wait_for_input=True` mode would never wake up for gamepad input.

**Why `event.gbutton.down` instead of checking `DOWN` vs `UP`?** SDL3's `gbutton.down` is already a bool — `true` for pressed, `false` for released. Cleaner than `event.type == SDL_EVENT_GAMEPAD_BUTTON_DOWN`.

**Why divide by 32767.0f for axes?** SDL reports axis values as `Sint16` (-32768 to 32767). Dividing normalizes to -1.0 to 1.0 for sticks, which is what game developers expect.

### Changed: SDL initialization

```cpp
// Before (Windows-only bug):
#ifdef _WIN32
    if (!SDL_Init(SDL_INIT_VIDEO)) {
#else
    if (!SDL_Init(SDL_INIT_VIDEO | SDL_INIT_GAMEPAD)) {
#endif

// After:
if (!SDL_Init(SDL_INIT_VIDEO | SDL_INIT_GAMEPAD)) {
    // Fallback: try without gamepad subsystem
    if (!SDL_Init(SDL_INIT_VIDEO)) {
        throw ...;
    }
}
```

**Why?** The original code skipped gamepad init on Windows entirely (`#ifdef _WIN32`). That meant SDL never set up the gamepad subsystem, so no gamepad events would fire. The new code always tries gamepad init, with a graceful fallback if it fails.

### Added: Startup detection

```cpp
int count = 0;
SDL_JoystickID* ids = SDL_GetGamepads(&count);
if (ids) {
    for (int i = 0; i < count && i < DCG_MAX_GAMEPADS; i++) {
        handle_gamepad_added(ids[i]);
    }
    SDL_free(ids);
}
```

**Why?** If a controller is already plugged in when the app starts, SDL won't fire `SDL_EVENT_GAMEPAD_ADDED` — that event only fires for new connections. So at init time, we explicitly query SDL for existing controllers and register them.

**Why `SDL_free(ids)`?** SDL allocated that array internally. We must free it with `SDL_free` (not C++ `delete` or `free`) to match SDL's allocator.
