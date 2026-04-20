# Layer 2: Cython Bridge

This chapter covers the three files that bridge C++ and Python: the backend declarations (`.pxd`), the type enums (`.pxd`), and the enum helper implementations (`.pyx`).

## File: `dearcygui/backends/backend.pxd`

A `.pxd` file is like a C header but for Cython. It tells Cython "these C functions exist and have these signatures."

```cython
cdef extern from "backend.h" nogil:
    # ...existing declarations...

    # Multi-controller query API
    const int DCG_MAX_GAMEPADS
    int  dcg_gamepad_count()
    bint dcg_gamepad_connected(int slot)
    const char* dcg_gamepad_name(int slot)
    bint dcg_gamepad_button_down(int slot, int button)
    float dcg_gamepad_axis(int slot, int axis)
```

**Why `cdef extern from "backend.h" nogil`?** This tells Cython:

- `cdef extern`: "These are defined in C/C++, not Python"
- `from "backend.h"`: "Their declarations are in this header"
- `nogil`: "They can be called without holding Python's Global Interpreter Lock"

**Why `bint` instead of `bool`?** In Cython, `bint` means "C bool that auto-converts to Python `True`/`False`". Using `bool` would create ambiguity between C++ `bool` and Python `bool`.

**Why declare `DCG_MAX_GAMEPADS`?** So Cython code can use the constant (e.g., `range(DCG_MAX_GAMEPADS)`) without hardcoding `8`.

---

## File: `dearcygui/types.pxd`

Declares the new enums so other `.pyx` files can import them.

```cython
cpdef enum class GamepadButton:
    SOUTH = 0,          # A (Xbox) / Cross (PS)
    EAST = 1,           # B (Xbox) / Circle (PS)
    ...

cpdef enum class GamepadAxis:
    LEFT_X = 0,
    LEFT_Y = 1,
    ...
```

**Why `cpdef enum class`?**

- `cpdef` = accessible from both C and Python (unlike `cdef` which is C-only, or `def` which is Python-only)
- `enum class` = becomes a proper Python `IntEnum` at runtime, so `dcg.GamepadButton.SOUTH` works in Python

**Why match SDL values exactly?** The enum values (0, 1, 2...) match `SDL_GAMEPAD_BUTTON_SOUTH`, `SDL_GAMEPAD_BUTTON_EAST`, etc. This means we can pass the Python enum value directly as the `int button` parameter to C functions without any translation.

**Why helper functions (`is_GamepadButton`, `make_GamepadButton`)?** Following the existing pattern used by `Key`, `MouseButton`, etc. They allow accepting strings (`"SOUTH"`) or ints in addition to enum values, providing a forgiving API.

---

## File: `dearcygui/types.pyx`

Implements the helper functions declared in the `.pxd`:

```cython
cdef object make_GamepadButton(value):
    if isinstance(value, GamepadButton):
        return value
    if isinstance(value, str):
        return GamepadButton[value.upper()]
    if isinstance(value, int):
        return GamepadButton(value)
    raise TypeError(...)
```

**Why a separate `.pyx`?** Cython splits declarations (`.pxd`) from implementations (`.pyx`). The `.pxd` is like a `.h` header — it defines "what exists." The `.pyx` is like a `.cpp` — it defines "how it works."

The `.pxd`/`.pyx` split is one of Cython's key patterns. Other `.pyx` files can `cimport` from the `.pxd` to use these types at C speed, while Python code gets the `IntEnum` interface automatically.
