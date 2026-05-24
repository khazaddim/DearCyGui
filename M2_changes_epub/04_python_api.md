# Layer 3: Python API

This chapter covers `core.pyx` — the only file that actually exposes M2 to Python users. Two new methods on `Gamepad` and one new line inside `Viewport.render_frame()`.

## File: `dearcygui/core.pyx`

### Changed: cimport list

```cython
from .backends.backend cimport (
    ...,
    dcg_gamepad_button_down,
    dcg_gamepad_button_pressed,    # NEW
    dcg_gamepad_button_released,   # NEW
    dcg_gamepad_begin_frame,       # NEW
    dcg_gamepad_axis,
    ...,
)
```

**Why explicit names instead of `cimport *`?** Cython's `cimport` is C-speed but bringing in unnamed symbols hurts both readability and incremental-rebuild stability. The pattern in this file is "list every C function we depend on by name", and M2 simply extends the list.

### Added: `Gamepad.is_button_pressed()` and `Gamepad.is_button_released()`

```cython
cdef class Gamepad:
    ...
    def is_button_down(self, button) -> bool:
        button = make_GamepadButton(button)
        return dcg_gamepad_button_down(self._slot, <int>button)

    def is_button_pressed(self, button) -> bool:
        """True for exactly one frame on the rising edge.

        The flag is cleared at the start of each ``render_frame()`` call,
        so this method must be polled *after* ``render_frame()`` has run.
        """
        button = make_GamepadButton(button)
        return dcg_gamepad_button_pressed(self._slot, <int>button)

    def is_button_released(self, button) -> bool:
        """True for exactly one frame on the falling edge.

        Same timing rule as ``is_button_pressed`` — poll after ``render_frame()``.
        """
        button = make_GamepadButton(button)
        return dcg_gamepad_button_released(self._slot, <int>button)
```

**Why exactly the same shape as `is_button_down`?** Three lines, no caching, no allocation. Each method:

1. Validates and normalizes the input (`make_GamepadButton` accepts the enum, a string, or an int).
2. Casts to `<int>` so the Python enum becomes a C int.
3. Calls the matching C function.

A user who is comfortable with `is_button_down` can read the new methods at a glance — same signature, same idioms, just a different question.

**Why does the docstring spell out the timing rule?** Edge flags are a stateful contract — they only mean what they say if the caller respects the "poll after `render_frame()`" rule. Putting the rule in the docstring makes it discoverable from `help(gp.is_button_pressed)` without forcing readers to dig through the design doc.

**Why no caching of `make_GamepadButton(button)`?** The cost is one isinstance check plus an enum lookup — well under a microsecond. Caching would force per-instance state and would not survive Python re-binding the input to a different value. The cost-vs-complexity trade is firmly on the side of "just call it".

**Why `def` and not `cpdef`?** `def` is fine here: the methods are meant to be called from Python game code, not from other Cython hot paths. If profiling later shows these are bottlenecks, switching to `cpdef` is a one-keyword change.

### Changed: `Viewport.render_frame()` calls `dcg_gamepad_begin_frame()` first

The body of `render_frame()` now begins with one extra line, inside the existing `try:` block, immediately before `processEvents`:

```cython
def render_frame(self, ...):
    ...
    try:
        ...
        dcg_gamepad_begin_frame()                              # NEW
        (<platformViewport*>self._platform).processEvents(<int>target_timeout_ms)
        ...
```

**Why this exact location?** The contract is "edges reflect events processed in this frame." `processEvents()` is what drains the SDL event queue and sets the edge flags. Clearing immediately before that call is the smallest possible window in which both:

1. The flags are guaranteed empty before any new events are consumed, and
2. No other code path could observe a stale flag in between (the line right before is just bookkeeping).

**Why inside the `try:` block?** Symmetry with `processEvents` — if either operation throws, the surrounding error handling runs. The clear itself cannot throw, but co-locating them keeps the frame contract atomic from the reader's perspective.

**Why is `wait_events()` (the separate blocking input path at line ~4642) *not* updated?** `wait_events()` is a different API — it blocks until input is available rather than driving a render loop. Its callers do not interact with the per-frame edge model and adding `begin_frame()` there would actually break the contract: a caller could clear edges, block on `wait_events`, return, and have no way to read them because the next `render_frame()` would clear them again. M2 keeps `wait_events()` strictly on the M1 (level-only) contract.

**Why no opt-out / no flag to disable edge clearing?** The edge model is cheap (16 × 26 bytes of `memset` per frame) and the clear is idempotent. There is no scenario where a caller benefits from skipping it, and skipping it would break the "cleared at start of every frame" invariant the docstrings promise. Less surface area = fewer bugs.
