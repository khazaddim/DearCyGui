# Layer 1: C++ Backend — Implementation

## File: `dearcygui/backends/sdl3_gl3_backend.cpp`

This is where the edge-detection logic actually lives.

### Changed: Connect / disconnect handlers clear the new arrays

```cpp
static void handle_gamepad_added(SDL_JoystickID id) {
    ...
    GamepadState& s = g_gamepads[slot];
    ...
    memset(s.buttons,          0, sizeof(s.buttons));
    memset(s.buttons_pressed,  0, sizeof(s.buttons_pressed));   // NEW
    memset(s.buttons_released, 0, sizeof(s.buttons_released));  // NEW
    memset(s.axes,             0, sizeof(s.axes));
    ...
}

static void handle_gamepad_removed(SDL_JoystickID id) {
    ...
    memset(s.buttons,          0, sizeof(s.buttons));
    memset(s.buttons_pressed,  0, sizeof(s.buttons_pressed));   // NEW
    memset(s.buttons_released, 0, sizeof(s.buttons_released));  // NEW
    ...
}
```

**Why clear them at hot-plug?** A disconnected slot must report a perfectly clean slate. Otherwise a stale `pressed` flag from an unplugged controller could "fire" on the next frame after a fresh controller takes its slot.

### Changed: Edge detection inside the BUTTON_DOWN / BUTTON_UP case

The M1 code unconditionally wrote `event.gbutton.down` into `buttons[]`. M2 keeps that, but first reads the **previous** value to detect the transition:

```cpp
case SDL_EVENT_GAMEPAD_BUTTON_DOWN:
case SDL_EVENT_GAMEPAD_BUTTON_UP:
{
    int slot = find_gamepad_slot(event.gbutton.which);
    if (slot >= 0 && event.gbutton.button < DCG_MAX_GAMEPAD_BUTTONS) {
        bool was_down = g_gamepads[slot].buttons[event.gbutton.button];
        bool now_down = event.gbutton.down;
        g_gamepads[slot].buttons[event.gbutton.button] = now_down;

        // Edge detection: latch the transition for this frame.
        // Using OR so multiple transitions within one frame still register as an event.
        if (now_down && !was_down) {
            g_gamepads[slot].buttons_pressed[event.gbutton.button] = true;
        } else if (!now_down && was_down) {
            g_gamepads[slot].buttons_released[event.gbutton.button] = true;
        }
    }
    needsRefresh.store(true);
    break;
}
```

**Why compare `was_down` and `now_down` instead of trusting the event type?** SDL can occasionally deliver a `BUTTON_DOWN` event for a button that the OS already considered held (driver quirks, focus changes, controllers that re-announce state on wake). We only want to fire `pressed` on a real `false → true` transition. The transition test is the source of truth; the event type is just a hint.

**Why `=` `true` (assign) and not `|=` (OR-assign)?** They are equivalent here — the right-hand side is `true` and the left-hand side is `bool`. The comment says "OR-latch" because the *semantic* effect is OR-latching: once a flag is set, it stays set until `begin_frame()` clears it, so a second transition in the same frame is harmless rather than overwriting.

**Why does this matter — the "tap so fast both edges land in one frame" case?** Imagine a 60 FPS frame (~16 ms). Inside one frame, SDL might deliver:

```
DOWN (was_down=false, now_down=true)  → pressed = true
UP   (was_down=true,  now_down=false) → released = true
```

Both flags are set. Both report `true` to the next poll. The held state ends the frame at `false`. The player's tap is faithfully reported even though it never appeared as "held" in any single frame.

The opposite order (UP arriving while we never saw the DOWN) cannot happen here because `was_down` would be `false` and `now_down` would be `false` — no transition, no flag set. That is correct: there was no real release, just a noise event.

### Added: Two query functions

```cpp
bool dcg_gamepad_button_pressed(int slot, int button) {
    if (slot < 0 || slot >= DCG_MAX_GAMEPADS) return false;
    if (button < 0 || button >= DCG_MAX_GAMEPAD_BUTTONS) return false;
    if (!g_gamepads[slot].connected) return false;
    return g_gamepads[slot].buttons_pressed[button];
}

bool dcg_gamepad_button_released(int slot, int button) {
    if (slot < 0 || slot >= DCG_MAX_GAMEPADS) return false;
    if (button < 0 || button >= DCG_MAX_GAMEPAD_BUTTONS) return false;
    if (!g_gamepads[slot].connected) return false;
    return g_gamepads[slot].buttons_released[button];
}
```

**Why exactly the same shape as `dcg_gamepad_button_down()` from M1?** Three guards (slot range, button range, connected) and one array read. The reader does not care which physical event flipped the bit — it just asks "is this set right now?". Bounds checks are mandatory because Python integers can be anything.

**Why `return false` for disconnected?** Same rationale as M1: a disconnected slot reports "nothing happening." A game loop never has to special-case empty slots.

### Added: `dcg_gamepad_begin_frame()`

```cpp
// Clear edge-detection flags at the start of each frame.
// Called by Viewport.render_frame() before SDL events are processed,
// so pressed/released flags reflect events that arrived during this frame.
void dcg_gamepad_begin_frame() {
    for (int i = 0; i < DCG_MAX_GAMEPADS; i++) {
        memset(g_gamepads[i].buttons_pressed,  0, sizeof(g_gamepads[i].buttons_pressed));
        memset(g_gamepads[i].buttons_released, 0, sizeof(g_gamepads[i].buttons_released));
    }
}
```

**Why clear at the *start* of the frame and not at the end?** Two reasons:

1. **Correctness with `wait_for_input=True`.** If we cleared at the end, then waited for input before the next frame, the flags would survive across an arbitrarily long sleep. By clearing at the start of `render_frame()` we guarantee the flags only ever describe the *just-processed* event batch.
2. **Ordering with the consumer.** The consumer reads edges *after* `render_frame()` returns. Clearing-at-start means: when the consumer reads, the only events that can be reflected are the ones SDL delivered during this very frame.

**Why iterate all 8 slots unconditionally instead of only connected ones?** A `memset` of 26 bytes is faster than the `if (connected)` branch that would skip it. There is no correctness difference (clearing an empty slot is a no-op semantically), and removing the branch keeps the function predictable.

**Why is this not in `processEvents()` itself?** Because the public contract for M2 is "clear at the start of `render_frame()`". Putting the clear inside `processEvents()` would couple it to a private helper. Exposing it as a top-level C function lets Cython call it explicitly and lets future code (e.g. headless tests) drive the edge model without going through SDL at all.
