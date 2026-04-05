# DearCyGui Study Guide: Multi-Controller Implementation

A guide to understanding DearCyGui's architecture for implementing multi-controller gamepad support.

---

## Table of Contents

1. [Cython Fundamentals](#1-cython-fundamentals)
2. [DearCyGui File Structure](#2-dearcygui-file-structure)
3. [Build System](#3-build-system)
4. [SDL3 Backend Architecture](#4-sdl3-backend-architecture)
5. [Handler System](#5-handler-system)
6. [Key Files to Study](#6-key-files-to-study)
7. [Implementation Path](#7-implementation-path)

---

## 1. Cython Fundamentals

### What is Cython?

Cython is a superset of Python that compiles to C/C++. It allows:
- Writing Python-like code that runs at C speed
- Directly calling C/C++ functions
- Defining C-level data types

### Cython File Types

| Extension | Purpose | Compiled To |
|-----------|---------|-------------|
| `.pyx` | Implementation file (like `.c` or `.cpp`) | `.cpp` then `.pyd`/`.so` |
| `.pxd` | Declaration file (like `.h` header) | Nothing (imported by `.pyx`) |
| `.pyi` | Type stub for IDE/mypy (Python only) | Nothing |

### Key Cython Syntax

```cython
# cdef = C-level declaration (not visible to Python)
cdef int my_c_variable = 42
cdef void my_c_function() nogil:
    pass

# cpdef = Both C and Python visible
cpdef int accessible_from_both():
    return 1

# def = Python-only (normal Python function)
def python_function():
    pass

# cdef class = Extension type (C-backed Python class)
cdef class MyClass:
    cdef int _private_c_field      # C-level field
    cdef readonly int public_field # Python-readable
    
    def __cinit__(self):           # C-level __init__ (runs first)
        self._private_c_field = 0
    
    def __init__(self):            # Python-level __init__
        pass

# Importing C functions
cdef extern from "backend.h" nogil:
    int dcg_gamepad_count()
```

### The `nogil` Keyword

```cython
# Python has a Global Interpreter Lock (GIL)
# nogil = this code doesn't need Python objects, can release GIL

cdef void fast_function() noexcept nogil:
    # Can't use Python objects here
    # Can call C functions freely
    pass

# Temporarily acquire GIL inside nogil block
cdef void mixed_function() noexcept nogil:
    cdef int result
    # ... C code ...
    with gil:
        # Can use Python objects here
        print(result)
```

---

## 2. DearCyGui File Structure

```
dearcygui/
├── __init__.py          # Python package init, exports public API
├── __init__.pxd         # Cython exports for other .pyx files
│
├── core.pyx             # Core classes: Context, Viewport, baseItem, baseHandler
├── core.pxd             # Declarations for core.pyx
├── core.pyi             # Type stubs for IDE
│
├── handler.pyx          # All handler classes (KeyPressHandler, etc.)
├── handler.pxd          # Handler declarations
│
├── types.pyx            # Enums (Key, MouseButton, etc.) and type helpers
├── types.pxd            # Type declarations
│
├── widget.pyx           # UI widgets (Button, Text, etc.)
├── widget.pxd
│
├── backends/
│   ├── backend.h        # C++ API declarations
│   ├── backend.pxd      # Cython declarations for C++ API
│   ├── sdl3_gl3_backend.cpp    # SDL3+OpenGL backend implementation
│   ├── imgui_impl_sdl3.cpp     # ImGui's SDL3 integration
│   └── imgui_impl_opengl3.cpp  # ImGui's OpenGL integration
│
└── wrapper/
    ├── imgui.pxd        # Cython bindings for Dear ImGui
    └── implot.pxd       # Cython bindings for ImPlot
```

### How Files Relate

```
┌──────────────────────────────────────────────────────────────────┐
│                     Python User Code                              │
│  import dearcygui as dcg                                         │
│  handler = dcg.KeyPressHandler(C, key=dcg.Key.SPACE, ...)       │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    __init__.py                                    │
│  Imports and re-exports from compiled .pyx modules               │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                 .pyx Implementation Files                         │
│  handler.pyx → KeyPressHandler class                             │
│  types.pyx   → Key enum                                          │
│  core.pyx    → Context, Viewport, baseHandler                    │
└──────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        ▼                                           ▼
┌───────────────────┐                    ┌──────────────────────────┐
│   .pxd Headers    │                    │   C++ Backend            │
│   (declarations)  │                    │   backend.h              │
│   core.pxd        │◄───────────────────│   sdl3_gl3_backend.cpp   │
│   backend.pxd     │                    │   imgui_impl_sdl3.cpp    │
└───────────────────┘                    └──────────────────────────┘
                                                    │
                                                    ▼
                                         ┌──────────────────────────┐
                                         │   SDL3 + ImGui + OpenGL  │
                                         │   (thirdparty libraries) │
                                         └──────────────────────────┘
```

---

## 3. Build System

### Build Flow

```
Source Files                    Intermediate                    Output
────────────────────────────────────────────────────────────────────────

.pyx files ──────────► Cython ──────────► .cpp files ──────┐
                                                           │
.cpp files (backend) ──────────────────────────────────────┼──► MSVC/GCC
                                                           │      │
thirdparty/*.cpp ──────────────────────────────────────────┘      │
                                                                  ▼
                                                           .pyd (Windows)
                                                           .so (Linux/Mac)
```

### setup.py Key Sections

**Location:** `setup.py` (root)

```python
# 1. Build SDL3 as static library
def build_SDL3():
    # cmake builds thirdparty/SDL → build_SDL/Release/SDL3-static.lib

# 2. Define Cython source files (lines 271-286)
cython_sources = [
    "dearcygui/core.pyx",
    "dearcygui/handler.pyx",
    "dearcygui/types.pyx",
    # ... etc
]

# 3. Define C++ sources linked with Cython (lines 204-219)
cpp_sources = [
    "dearcygui/backends/sdl3_gl3_backend.cpp",
    "dearcygui/backends/imgui_impl_sdl3.cpp",
    # ... imgui, implot sources
]

# 4. Single extension combining everything (lines 289-300)
Extension(
    "dearcygui.dearcygui",
    ["dearcygui/dearcygui.pyx"] + cython_sources + cpp_sources,
    extra_objects=[sdl3_lib, freetype_lib]  # Static libs
)
```

### Build Commands

```powershell
# Full rebuild
python -m pip install --no-build-isolation . --force-reinstall --no-cache-dir

# Just rebuild (faster, if dependencies unchanged)
python setup.py build_ext --inplace
```

### Build Output

The build has two stages:

1. **Cython transpiles** `.pyx` → `.cpp`
   - `core.pyx` → `core.cpp`
   - `handler.pyx` → `handler.cpp`
   - etc.

2. **C++ compiler (MSVC)** compiles all `.cpp` → single `.pyd`
   - The generated `.cpp` files from step 1
   - Plus manually-written `.cpp` files (like `sdl3_gl3_backend.cpp`)
   - All linked together into `dearcygui.cp314-win_amd64.pyd`

After build, these files appear:
```
dearcygui/
├── core.cpp          # Generated by Cython from core.pyx (intermediate)
├── handler.cpp       # Generated by Cython from handler.pyx (intermediate)
├── types.cpp         # Generated by Cython from types.pyx (intermediate)
└── ...               # These are typically in .gitignore

.venv/Lib/site-packages/dearcygui/
├── dearcygui.cp314-win_amd64.pyd   # Final compiled extension (THE binary)
└── ...
```

The generated `.cpp` files contain the C/C++ translation of your Cython code, including all the Python C API calls needed to make Python objects work.

---

## 4. SDL3 Backend Architecture

### File: `dearcygui/backends/sdl3_gl3_backend.cpp`

This is the C++ layer between SDL3 and Python/Cython.

> **Important:** This file is **hand-written C++**, NOT generated by Cython. Unlike `core.cpp` 
> (which is auto-generated from `core.pyx`), `sdl3_gl3_backend.cpp` was written manually and 
> is compiled directly by MSVC/GCC alongside the Cython-generated code.

### Backend Directory Structure

```
dearcygui/backends/
├── sdl3_gl3_backend.cpp    # Hand-written C++ (main backend implementation)
├── backend.h               # C++ header declarations
├── backend.pxd             # Cython declaration file - BRIDGE to Python
├── imgui_impl_sdl3.cpp/h   # ImGui's official SDL3 backend (hand-written)
├── imgui_impl_opengl3.cpp/h # ImGui's official OpenGL3 backend (hand-written)
└── time.pxd                # Time-related Cython declarations
```

### How Cython Calls the C++ Backend

The `.pxd` file (`backend.pxd`) acts as the bridge:

1. **`backend.pxd`** declares "these C++ classes/functions exist" using Cython syntax
2. **Cython `.pyx` files** (like `core.pyx`) import these declarations
3. **Cython generates** Python C API code that calls the hand-written C++
4. **MSVC links** everything together into the final `.pyd`

```
┌─────────────────────┐     ┌──────────────────────┐     ┌────────────────────────┐
│  sdl3_gl3_backend.cpp│     │     backend.pxd      │     │      core.pyx          │
│  (hand-written C++) │◄────│  (Cython declarations)│────►│  (Cython code)         │
│                     │     │  "these exist..."     │     │  uses declarations     │
└─────────────────────┘     └──────────────────────┘     └────────────────────────┘
```

### SDL Initialization (lines 667-685)

```cpp
if (!sdlInitialized) {
    if (!SDL_Init(SDL_INIT_VIDEO | SDL_INIT_GAMEPAD)) {
        // Fallback without gamepad...
    }
    sdlInitialized = true;
}
```

### Event Processing (lines ~1080-1290)

```cpp
bool SDLViewport::processEvents(int timeout_ms) {
    SDL_Event event;
    while (SDL_PollEvent(&event)) {
        // Pass to ImGui first
        ImGui_ImplSDL3_ProcessEvent(&event);
        
        switch (event.type) {
            case SDL_EVENT_KEY_DOWN:
            case SDL_EVENT_KEY_UP:
                needsRefresh.store(true);
                break;
                
            // NEW: Gamepad events (we added these)
            case SDL_EVENT_GAMEPAD_BUTTON_DOWN:
            case SDL_EVENT_GAMEPAD_BUTTON_UP:
            case SDL_EVENT_GAMEPAD_AXIS_MOTION:
                needsRefresh.store(true);
                break;
                
            // ... other events
        }
    }
}
```

### Current Gamepad Flow

```
┌─────────────────┐
│     SDL3        │  SDL_EVENT_GAMEPAD_BUTTON_DOWN
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  sdl3_gl3_backend.cpp::processEvents()  │
│  - Sets needsRefresh flag               │
│  - Passes event to ImGui                │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  imgui_impl_sdl3.cpp                    │
│  - Updates ImGui's internal gamepad     │
│  - Merges ALL controllers into ONE      │  ◄── THIS IS THE PROBLEM
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  ImGui::IsKeyPressed(ImGuiKey_Gamepad*) │
│  - Returns true/false for virtual pad   │
│  - No controller ID information         │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  handler.pyx::KeyPressHandler           │
│  - Calls imgui.IsKeyPressed()           │
│  - Fires callback if True               │
└─────────────────────────────────────────┘
```

### Do We Need to Disable ImGui's Gamepad Handling?

**Short answer: No.** The multi-controller API is designed to **coexist** with ImGui's built-in gamepad support.

#### How ImGui's Gamepad Works

ImGui has three gamepad modes (defined in `imgui_impl_sdl3.h`):

```cpp
enum ImGui_ImplSDL3_GamepadMode { 
    ImGui_ImplSDL3_GamepadMode_AutoFirst,  // Default: first controller only
    ImGui_ImplSDL3_GamepadMode_AutoAll,    // Merge ALL controllers into one virtual pad
    ImGui_ImplSDL3_GamepadMode_Manual      // Use specific gamepads you provide
};
```

The default is `AutoFirst` - only the first connected controller drives ImGui's UI navigation.

#### Enabling/Disabling ImGui Gamepad Navigation

ImGui's gamepad navigation is controlled by a config flag:

```cpp
// Enable (allows gamepad to navigate UI)
io.ConfigFlags |= ImGuiConfigFlags_NavEnableGamepad;

// Disable (gamepad won't navigate UI)
io.ConfigFlags &= ~ImGuiConfigFlags_NavEnableGamepad;
```

**Note:** In recent ImGui versions (2025+), gamepad state is always read regardless of this flag - it just controls whether the state affects UI navigation.

#### Why We Don't Disable It

Per the design decision in `openspec/changes/add-multi-controller-support/design.md`:

> **Decision**: New gamepad API operates independently of ImGui's gamepad handling.
>
> **Rationale**:
> - ImGui merges all controllers into one virtual gamepad
> - ImGui's gamepad is designed for UI navigation, not game input  
> - First controller continues to drive ImGui navigation (AutoFirst mode unchanged)
> - Game logic uses new direct API for per-controller input

The two systems serve different purposes:
- **ImGui's gamepad**: UI navigation (menus, focus, etc.) - single virtual controller is fine
- **Our gamepad API**: Per-controller game input - needs individual controller identity

They read from the same SDL events but interpret them differently.

### M1 Target: Bypass ImGui for Per-Controller State

```
┌─────────────────┐
│     SDL3        │  SDL_EVENT_GAMEPAD_BUTTON_DOWN
└────────┬────────┘   with event.gbutton.which = controller_id
         │
         ├──────────────────────────────┐
         │                              │
         ▼                              ▼
┌─────────────────────────┐    ┌──────────────────────────────┐
│  imgui_impl_sdl3.cpp    │    │  NEW: GamepadState tracking  │
│  (still works for UI)   │    │  in sdl3_gl3_backend.cpp     │
└─────────────────────────┘    │  - Per-controller buttons[]  │
                               │  - Per-controller axes[]     │
                               │  - dcg_gamepad_button_down() │
                               └────────────┬─────────────────┘
                                            │
                                            ▼
                               ┌──────────────────────────────┐
                               │  NEW: Gamepad class          │
                               │  in core.pyx                 │
                               │  - viewport.gamepads[i]      │
                               │  - .is_button_down(btn)      │
                               └──────────────────────────────┘
```

---

## 5. Handler System

### Base Class: `baseHandler`

**File:** `dearcygui/core.pxd` (lines 625-641)

```cython
cdef class baseHandler(baseItem):
    cdef bint _enabled
    cdef Callback _callback
    
    # Called once when handler is attached to an item
    cdef void check_bind(self, baseItem)
    
    # Called every frame - returns True if condition is met
    cdef bint check_state(self, baseItem) noexcept nogil
    
    # Called when check_state returns True - runs callback
    cdef void run_handler(self, baseItem) noexcept nogil
```

### Example: KeyPressHandler

**File:** `dearcygui/handler.pyx` (lines 1222-1290)

```cython
cdef class KeyPressHandler(baseHandler):
    def __cinit__(self):
        self._key = imgui.ImGuiKey_Enter
        self._repeat = True

    @property
    def key(self):
        cdef unique_lock[DCGMutex] m
        lock_gil_friendly(m, self.mutex)
        return make_Key(self._key)
    
    @key.setter
    def key(self, value):
        cdef unique_lock[DCGMutex] m
        lock_gil_friendly(m, self.mutex)
        self._key = <int>make_Key(value)

    # THE KEY METHOD: Called every frame during rendering
    cdef bint check_state(self, baseItem item) noexcept nogil:
        # Calls imgui's C++ function directly
        return imgui.IsKeyPressed(<imgui.ImGuiKey>self._key, self._repeat)

    cdef void run_handler(self, baseItem item) noexcept nogil:
        # ... locking ...
        if imgui.IsKeyPressed(<imgui.ImGuiKey>self._key, self._repeat):
            with gil:
                # Queue callback for execution
                self.context.queue_callback(self._callback, self, item, make_Key(self._key))
```

### Handler Pattern Summary

```cython
cdef class MyNewHandler(baseHandler):
    # 1. C-level fields
    cdef int _some_setting
    
    # 2. __cinit__ for C-level init
    def __cinit__(self):
        self._some_setting = 0
    
    # 3. Properties with mutex locking
    @property
    def some_setting(self):
        cdef unique_lock[DCGMutex] m
        lock_gil_friendly(m, self.mutex)
        return self._some_setting
    
    # 4. check_state: return True when condition is met
    cdef bint check_state(self, baseItem item) noexcept nogil:
        return some_c_function()  # Call C/C++ directly
    
    # 5. run_handler: execute callback when check_state was True
    cdef void run_handler(self, baseItem item) noexcept nogil:
        # ... with gil: queue callback ...
```

---

## 6. Key Files to Study

### Priority 1: Understanding the Pattern

| File | What to Look For |
|------|------------------|
| `handler.pyx` lines 1222-1290 | `KeyPressHandler` - the pattern for M3 |
| `handler.pxd` lines 1-50 | How handlers are declared |
| `core.pxd` lines 625-670 | `baseHandler` and `baseItem` base classes |

### Priority 2: C++ Backend

| File | What to Look For |
|------|------------------|
| `backends/sdl3_gl3_backend.cpp` lines 667-700 | SDL initialization with gamepad |
| `backends/sdl3_gl3_backend.cpp` lines 1130-1180 | Event processing switch statement |
| `backends/backend.h` | C++ class and function declarations |
| `backends/backend.pxd` | How C++ is exposed to Cython |

### Priority 3: Types and Enums

| File | What to Look For |
|------|------------------|
| `types.pyx` search for "class Key" | How enums are defined |
| `types.pxd` | Enum declarations |

### Priority 4: Build Understanding

| File | What to Look For |
|------|------------------|
| `setup.py` lines 180-350 | How extensions are defined |

---

## 7. Implementation Path

### M1 Implementation Steps

#### Step 1: C++ (sdl3_gl3_backend.cpp)

Add near top of file:
```cpp
// Gamepad state tracking
static constexpr int MAX_GAMEPADS = 8;

struct GamepadState {
    SDL_JoystickID sdl_id;
    SDL_Gamepad* handle;
    char name[128];
    bool buttons[SDL_GAMEPAD_BUTTON_COUNT];
    float axes[SDL_GAMEPAD_AXIS_COUNT];
    bool connected;
};

static GamepadState g_gamepads[MAX_GAMEPADS];
static int g_gamepad_count = 0;
```

Add event handling in `processEvents()`:
```cpp
case SDL_EVENT_GAMEPAD_ADDED: {
    // Find empty slot, open gamepad, store handle
    break;
}
case SDL_EVENT_GAMEPAD_REMOVED: {
    // Find slot by SDL_JoystickID, close, mark disconnected
    break;
}
case SDL_EVENT_GAMEPAD_BUTTON_DOWN:
case SDL_EVENT_GAMEPAD_BUTTON_UP: {
    int slot = find_slot_by_id(event.gbutton.which);
    if (slot >= 0) {
        g_gamepads[slot].buttons[event.gbutton.button] = event.gbutton.down;
    }
    needsRefresh.store(true);
    break;
}
```

Add query functions:
```cpp
extern "C" {
    int dcg_gamepad_count() { return g_gamepad_count; }
    bool dcg_gamepad_connected(int slot) { return g_gamepads[slot].connected; }
    bool dcg_gamepad_button_down(int slot, int button) {
        return g_gamepads[slot].buttons[button];
    }
    // ... etc
}
```

#### Step 2: backend.h

```cpp
// Gamepad API
extern "C" {
    int dcg_gamepad_count();
    bool dcg_gamepad_connected(int slot);
    const char* dcg_gamepad_name(int slot);
    bool dcg_gamepad_button_down(int slot, int button);
    float dcg_gamepad_axis(int slot, int axis);
}
```

#### Step 3: backend.pxd

```cython
cdef extern from "backend.h" nogil:
    # ... existing declarations ...
    
    # Gamepad functions
    int dcg_gamepad_count()
    bint dcg_gamepad_connected(int slot)
    const char* dcg_gamepad_name(int slot)
    bint dcg_gamepad_button_down(int slot, int button)
    float dcg_gamepad_axis(int slot, int axis)
```

#### Step 4: types.pyx

```cython
from enum import IntEnum

class GamepadButton(IntEnum):
    FACE_DOWN = 0       # SDL_GAMEPAD_BUTTON_SOUTH
    FACE_RIGHT = 1      # SDL_GAMEPAD_BUTTON_EAST
    FACE_LEFT = 2       # SDL_GAMEPAD_BUTTON_WEST
    FACE_UP = 3         # SDL_GAMEPAD_BUTTON_NORTH
    BACK = 4
    GUIDE = 5
    START = 6
    # ... etc

class GamepadAxis(IntEnum):
    LEFT_X = 0
    LEFT_Y = 1
    RIGHT_X = 2
    RIGHT_Y = 3
    LEFT_TRIGGER = 4
    RIGHT_TRIGGER = 5
```

#### Step 5: core.pyx

```cython
from .backends.backend cimport dcg_gamepad_count, dcg_gamepad_connected, \
    dcg_gamepad_name, dcg_gamepad_button_down, dcg_gamepad_axis

cdef class Gamepad:
    cdef int _slot
    cdef Context _context
    
    @staticmethod
    cdef Gamepad create(Context ctx, int slot):
        cdef Gamepad gp = Gamepad.__new__(Gamepad)
        gp._context = ctx
        gp._slot = slot
        return gp
    
    @property
    def slot(self):
        return self._slot
    
    @property
    def connected(self):
        return dcg_gamepad_connected(self._slot)
    
    @property
    def name(self):
        cdef const char* n = dcg_gamepad_name(self._slot)
        return n.decode('utf-8') if n else ""
    
    def is_button_down(self, button):
        return dcg_gamepad_button_down(self._slot, int(button))
    
    def get_axis(self, axis):
        return dcg_gamepad_axis(self._slot, int(axis))
```

Add to Viewport class:
```cython
@property
def gamepads(self):
    return [Gamepad.create(self.context, i) for i in range(8)]
```

---

## Quick Reference

### Cython Cheat Sheet

```cython
# Import C function
cdef extern from "header.h":
    int c_function(int arg)

# Call C function (no GIL needed)
cdef int result = c_function(42)

# Call C function from Python property
@property
def my_prop(self):
    return c_function(self._value)

# Thread-safe property access
@property
def safe_prop(self):
    cdef unique_lock[DCGMutex] m
    lock_gil_friendly(m, self.mutex)
    return self._value
```

### SDL3 Gamepad Constants

```cpp
// Buttons (SDL_GamepadButton enum)
SDL_GAMEPAD_BUTTON_SOUTH  // A / Cross
SDL_GAMEPAD_BUTTON_EAST   // B / Circle
SDL_GAMEPAD_BUTTON_WEST   // X / Square
SDL_GAMEPAD_BUTTON_NORTH  // Y / Triangle

// Axes (SDL_GamepadAxis enum)
SDL_GAMEPAD_AXIS_LEFTX         // -1.0 to 1.0
SDL_GAMEPAD_AXIS_LEFTY         // -1.0 to 1.0
SDL_GAMEPAD_AXIS_LEFT_TRIGGER  // 0.0 to 1.0
```

### Build Commands

```powershell
# Activate venv + MSVC
Import-Module "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\Tools\Microsoft.VisualStudio.DevShell.dll"
Enter-VsDevShell -VsInstallPath "C:\Program Files\Microsoft Visual Studio\2022\Community" -SkipAutomaticLocation -DevCmdArguments "-arch=x64 -host_arch=x64"
C:\Chris\DearCyGui\.venv\Scripts\Activate.ps1

# Rebuild
python -m pip install --no-build-isolation . --force-reinstall --no-cache-dir
```

---

Enjoy your vacation! This guide should give you a solid foundation to understand the codebase when you return.
