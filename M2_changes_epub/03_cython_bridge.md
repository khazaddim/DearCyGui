# Layer 2: Cython Bridge

For M2 the bridge changes are tiny. The enum machinery, the `make_GamepadButton()` helpers, and the slot/axis types from M1 are all reused unchanged. Only one file gains new declarations.

## File: `dearcygui/backends/backend.pxd`

Three new lines inside the existing `cdef extern from "backend.h" nogil:` block:

```cython
cdef extern from "backend.h" nogil:
    # ...M1 declarations...
    int  dcg_gamepad_count()
    bint dcg_gamepad_connected(int slot)
    const char* dcg_gamepad_name(int slot)
    bint dcg_gamepad_button_down(int slot, int button)
    float dcg_gamepad_axis(int slot, int axis)

    # M2: edge detection
    bint dcg_gamepad_button_pressed(int slot, int button)
    bint dcg_gamepad_button_released(int slot, int button)
    void dcg_gamepad_begin_frame()
```

**Why `bint` for the two queries?** Same rule as M1 — `bint` is Cython's "C bool that auto-converts to Python `True`/`False`". The C function returns C++ `bool`; Cython transparently handles the conversion at the call site.

**Why `void` for `begin_frame()`?** It has no return value — it is a side-effect-only operation that mutates the global `g_gamepads` array. Declaring it `void` means Cython will not try to materialize a Python return value on each call, keeping it free.

**Why `nogil` (inherited from the existing extern block)?** All three new functions only touch C arrays and never call back into Python. They are safe to call without holding the Global Interpreter Lock, which means future code could call them from a worker thread (e.g. an input thread) without GIL gymnastics. M2 itself does not exploit this, but the door is left open.

## What did *not* change

- **`dearcygui/types.pxd`** — `GamepadButton` and `GamepadAxis` enums are reused as-is. Edge detection asks the same question about the same buttons; there is no new enum to add.
- **`dearcygui/types.pyx`** — `make_GamepadButton()` and friends are reused as-is. They already validate any input the Python user can throw at the new methods.
- **`dearcygui/core.pxd`** — the `Gamepad` cdef class declaration only stores `_slot` and `_context`. Adding methods does not require declaring them in the .pxd unless they are `cdef`/`cpdef`. The two new methods are plain `def` methods, so they live entirely in `core.pyx`.

This minimalism is by design. M1 paid the structural cost (introducing `Gamepad`, the slot model, the enums); M2 is purely about adding two more questions Python can ask the same C++ state machine.
