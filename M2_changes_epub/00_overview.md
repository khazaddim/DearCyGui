# Milestone 2 Changes Walkthrough

This document explains every change made for M2 (frame-edge button detection), file by file, bottom-up from C++ to Python. Each section shows what was added and **why**.

## What M2 Adds

M1 answered the question **"is this button down right now?"** — a continuous (level) signal. That is great for movement and for "hold to charge" mechanics, but it cannot answer two equally common questions:

- **"Was this button just pressed this frame?"** (e.g. fire weapon, jump, confirm menu)
- **"Was this button just released this frame?"** (e.g. release charged shot, cancel hold)

M2 adds these **edge** signals via two new methods:

```python
gp.is_button_pressed(GamepadButton.SOUTH)   # True for exactly one frame
gp.is_button_released(GamepadButton.SOUTH)  # True for exactly one frame
```

The key invariants:

1. **Exactly-once**: every physical press fires `is_button_pressed` for exactly one frame.
2. **No missed events**: even if a player taps a button so fast that down + up land in the same frame, both edges still register.
3. **No drift**: edge flags are cleared at the start of every frame — they cannot leak into the next one.

## The Big Picture

The architecture from M1 is unchanged:

```
Python app  ←  you write this
    ↓
Cython (.pyx/.pxd)  ←  bridge between Python and C++
    ↓
C++ backend (.h/.cpp)  ←  talks directly to SDL3 and OpenGL
    ↓
SDL3  ←  cross-platform library that talks to your OS and hardware
```

M2 is a strictly additive change at every layer:

1. **C++** stores two new boolean arrays per controller (`buttons_pressed[]`, `buttons_released[]`) and gains a `dcg_gamepad_begin_frame()` function to clear them.
2. **Cython** declares the three new C functions and adds two new methods on the `Gamepad` class.
3. **`Viewport.render_frame()`** calls `dcg_gamepad_begin_frame()` before processing SDL events, so edge flags reflect *this* frame's events only.
4. **The demo** is restructured to verify the invariants: it counts presses/releases per button and renders a rolling event history.

The ordering rule is the most important new concept. Read on.

## The New Frame Contract

```
render_frame() {
    dcg_gamepad_begin_frame();     // 1. Clear edge flags
    processEvents();               // 2. Drain SDL queue, set edges on transitions
    ... draw frame ...             // 3. Edges reflect events that arrived this frame
}                                  // 4. Caller polls AFTER render_frame()
```

Because of this contract, the demo loop is **flipped** from M1:

```python
# M1 (level-only, order didn't matter much):
demo.poll_gamepads()
viewport.render_frame()

# M2 (edges must be polled AFTER processEvents has run):
viewport.render_frame()
demo.poll_gamepads()
```

The chapters that follow walk through each layer from bottom (C++) to top (Python).
