# Layer 3: Python API

This chapter covers the two `core` files that expose gamepads to Python users.

## File: `dearcygui/core.pxd`

Added the `Gamepad` class declaration and a `_gamepads` field on `Viewport`:

```cython
cdef class Gamepad:
    cdef int _slot
    cdef Context _context
```

**Why `cdef class`?** A `cdef class` is a Cython extension type — it's a Python class whose internal fields are C-typed for speed. The `_slot` is a plain C `int` (no Python object overhead), making access fast.

**Why `_gamepads` on Viewport?** We cache the 8 Gamepad objects so `viewport.gamepads` returns the same tuple every time instead of creating new objects each call.

---

## File: `dearcygui/core.pyx`

The actual `Gamepad` class implementation:

```cython
cdef class Gamepad:
    def __cinit__(self, Context context, int slot):
        self._context = context
        self._slot = slot

    @property
    def connected(self) -> bool:
        return dcg_gamepad_connected(self._slot)

    def is_button_down(self, button) -> bool:
        button = make_GamepadButton(button)
        return dcg_gamepad_button_down(self._slot, <int>button)

    def get_axis(self, axis) -> float:
        axis = make_GamepadAxis(axis)
        return dcg_gamepad_axis(self._slot, <int>axis)
```

**Why `__cinit__` instead of `__init__`?** For `cdef class`, `__cinit__` runs before `__init__` and is guaranteed to execute even if there's an exception. It's the right place to set C-typed fields.

**Why `make_GamepadButton(button)` before the C call?** This validates and converts the input — you can pass `GamepadButton.SOUTH`, `"south"`, or `0` and they all work. If you pass garbage, you get a clear Python error instead of undefined behavior in C.

**Why `<int>button`?** This is a Cython cast — converts the Python enum to a plain C `int` for the C function call.

**Why does `connected` call C every time?** The `connected` property doesn't cache — it calls `dcg_gamepad_connected()` each time. This ensures you always get the current state (a controller could disconnect at any moment).

### Viewport additions

```cython
@property
def gamepads(self):
    if self._gamepads is None:
        self._gamepads = tuple(
            Gamepad(self.context, i) for i in range(DCG_MAX_GAMEPADS)
        )
    return self._gamepads
```

**Why a tuple?** Tuples are immutable — you can't accidentally do `viewport.gamepads[0] = something`. The slots are fixed at 0-7.

**Why lazy init (`if self._gamepads is None`)?** The Gamepad objects need a `Context`, which might not be fully ready at `Viewport.__cinit__` time. Creating them on first access avoids timing issues.
