# Layer 1: C++ Backend — Header File

## File: `dearcygui/backends/backend.h`

The header now declares two extra per-controller arrays and three new C functions.

### Changed: `GamepadState` struct gains edge arrays

```cpp
struct GamepadState {
    SDL_JoystickID sdl_id = 0;
    SDL_Gamepad* handle = nullptr;
    char name[128] = {};
    bool buttons[DCG_MAX_GAMEPAD_BUTTONS]          = {};   // M1: held state (level)
    bool buttons_pressed[DCG_MAX_GAMEPAD_BUTTONS]  = {};   // M2: rising edge this frame
    bool buttons_released[DCG_MAX_GAMEPAD_BUTTONS] = {};   // M2: falling edge this frame
    float axes[DCG_MAX_GAMEPAD_AXES] = {};
    bool connected = false;
};
```

**Why two more arrays instead of reusing `buttons[]`?** The held array stores the *current* state continuously. Edge flags are a *delta* — they are true only on the frame the transition happened. They must be independently writable and clearable without disturbing the held state.

**Why `bool[]` instead of a bitmask or a single `int` of flags?** Three reasons:

1. The held array is already `bool[]`, so the layout is consistent and the indexing is identical.
2. The arrays are tiny (26 bytes each — controllers do not have 64 buttons).
3. A `memset(..., 0, ...)` on a `bool[]` of 26 bytes is a single inlined SIMD store on every modern CPU. It is essentially free per frame.

**Why latch flags instead of a per-frame event queue?** A queue would be more general, but it forces the consumer to do queue draining and would change the API shape. A latched flag matches the existing pattern (`buttons[]` is already a latched-state model) and answers the "did this happen?" question in O(1). It is also lock-free — readers just read a `bool`.

**Why `= {}` initialization?** Same reason as M1: zero-initializes the arrays at construction so an "unconnected" slot reports clean defaults if anything reads it before a controller arrives.

### Added: Three new C API function declarations

```cpp
bool dcg_gamepad_button_pressed(int slot, int button);
bool dcg_gamepad_button_released(int slot, int button);
void dcg_gamepad_begin_frame();
```

**Why three functions and not, say, one batch query?** Symmetry with `dcg_gamepad_button_down()` from M1 — Python users already know the pattern. A single per-button query also keeps the Cython bridge trivial: one C call per question, no allocation, no array marshalling.

**Why declare `dcg_gamepad_begin_frame()` here and not keep it private to the .cpp?** Cython needs to call it from `Viewport.render_frame()`. That requires it to appear in the header so `backend.pxd` can `cdef extern` it.

**Why one global `begin_frame()` instead of a per-slot version?** The render frame is a global concept — all 8 slots advance their "frame edges" together. A single call keeps the contract simple: one render frame = one edge clear, regardless of how many controllers are plugged in.
