# The Demo and Data Flow

## The Demo: `Small_Input_Demo.py`

The demo is the **verification harness** for M2. Its job is not to be pretty — it is to make the three M2 invariants visible at a glance:

1. **Exactly-once**: every press increments the press counter by 1, every release increments the release counter by 1.
2. **No missed events**: rapid mashing keeps the counts accurate.
3. **No drift**: the held label keeps working alongside the edges.

### The flipped main loop

```python
async def main_loop(viewport, demo):
    while viewport.context.running:
        viewport.render_frame()    # 1. Clear edges, process SDL events, draw
        demo.poll_gamepads()       # 2. Read edges and held state
        await asyncio.sleep(1.0 / 60.0)
```

**Why is this order reversed from M1?** In M1 the order did not matter — `is_button_down` is a level signal that survives across frames. In M2, edges are cleared at the start of `render_frame()`. Polling *before* `render_frame()` would read flags from the *previous* frame's events, but they would be cleared one nanosecond later by the next `render_frame()`. Polling *after* reads exactly the events that were processed during the just-completed frame.

This is the single most important pattern change for M2 users. The docs and docstrings repeat it for a reason.

### Per-slot display state

```python
EDGE_LATCH_FRAMES = 30
HISTORY_SIZE = 6

class InputDemo:
    def __init__(self):
        ...
        self.press_counts   = [{} for _ in range(8)]   # {label: int}
        self.release_counts = [{} for _ in range(8)]   # {label: int}
        self.history        = [[] for _ in range(8)]   # ["+A", "-A", "+B", ...]
        self.pressed_latch  = [{} for _ in range(8)]   # {label: frames_remaining}
        self.released_latch = [{} for _ in range(8)]   # {label: frames_remaining}
```

**Why counts?** Counts are the cheapest possible test of "exactly once". If you press A 10 times and the counter reads 10, edge detection is correct. If it reads 9 or 11, something is broken.

**Why a rolling history?** Counts say *what* fired but not *when*. The history gives temporal context: `+A  -A  +A  -A` shows alternation; `+A  +A` without an `-A` between would prove the released edge was missed.

**Why a separate `pressed_latch` / `released_latch`?** The C API's edge flag is true for exactly one frame (~16 ms). At 60 FPS the human eye literally cannot see a single-frame UI label. The latch is a *display-only* timer that keeps the label visible for `EDGE_LATCH_FRAMES` (~0.5 s). It does **not** affect the counts or the history — those operate on the raw one-frame edge.

This is an important separation: the underlying invariant (one-frame edge) is preserved exactly. The latch only changes what the human sees.

### The polling routine

```python
def poll_gamepads(self):
    gamepads = self.C.viewport.gamepads
    for i, gp in enumerate(gamepads):
        if not gp.connected:
            self._reset_slot(i)
            continue
        ...
        for btn, label in BUTTON_NAMES.items():
            if gp.is_button_pressed(btn):
                self.press_counts[i][label] = self.press_counts[i].get(label, 0) + 1
                self.pressed_latch[i][label] = EDGE_LATCH_FRAMES
                self.history[i].append(f"+{label}")
            if gp.is_button_released(btn):
                self.release_counts[i][label] = self.release_counts[i].get(label, 0) + 1
                self.released_latch[i][label] = EDGE_LATCH_FRAMES
                self.history[i].append(f"-{label}")
        ...
```

**Why query both edges per button per frame?** Because both can fire in the same frame (the rapid-tap case from chapter 2). Treating them as independent flags exactly mirrors the C-level model and avoids a class of "I only checked one and missed the other" bugs.

**Why does disconnect call `_reset_slot(i)`?** A controller hot-unplug must zero out the entire UI for that slot — counts, latches, history — so that when a new controller takes the slot it starts from a clean state. The C side already clears its edge arrays in `handle_gamepad_removed` (chapter 2); the demo does the same on the Python side for visual consistency.

---

## Data Flow Summary (M2)

When you tap and quickly release the A button on controller 2 inside a single frame:

```
 1. SDL_EVENT_GAMEPAD_BUTTON_DOWN  (which=<sdl_id>, button=0, down=true)
 2. SDL_EVENT_GAMEPAD_BUTTON_UP    (which=<sdl_id>, button=0, down=false)

 3. render_frame() runs:
    a. dcg_gamepad_begin_frame()
       → buttons_pressed[1][0]  = false
       → buttons_released[1][0] = false
    b. processEvents() drains the queue:
       - DOWN arrives:
         was_down=false, now_down=true
         buttons[1][0]         = true
         buttons_pressed[1][0] = true     ← rising edge latched
       - UP arrives:
         was_down=true,  now_down=false
         buttons[1][0]          = false
         buttons_released[1][0] = true    ← falling edge latched
    c. ImGui draws the frame using whatever state existed mid-frame.
       (For this demo the labels are written by poll_gamepads on the *next*
        cycle, which is fine — the latched flags survive until the next
        begin_frame.)

 4. Demo: poll_gamepads()
    → gp.is_button_down(SOUTH)     → false   (held state already settled)
    → gp.is_button_pressed(SOUTH)  → true    (rising edge)
    → gp.is_button_released(SOUTH) → true    (falling edge)
    Counts: press[A] = 1, release[A] = 1
    History: [..., "+A", "-A"]

 5. Next render_frame():
    a. dcg_gamepad_begin_frame()
       → buttons_pressed[1][0]  = false
       → buttons_released[1][0] = false
    b. processEvents() — no new events for this button.

 6. Next poll_gamepads():
    → gp.is_button_pressed(SOUTH)  → false  ← strictly one frame
    → gp.is_button_released(SOUTH) → false  ← strictly one frame
```

This trace shows the three invariants playing out simultaneously: both edges fire even when down+up land in one frame, each fires exactly once, and they are gone the very next frame.

## What M2 explicitly does *not* solve

- **No callbacks / handlers yet.** All M2 input is still poll-driven. Callback delivery and handler integration is M3.
- **No axis edge events.** "Trigger pulled past 0.5 this frame" is a useful event but is not part of M2's scope. The model could be extended to axes later by storing `axes_prev[]` alongside `axes[]` and computing thresholds at `begin_frame()` time.
- **No deadzone / curve shaping.** Axes are still raw normalized SDL values. M4 will own input shaping.

M2's contribution is small and surgical: two new questions Python can ask, one new line in `render_frame()` to anchor the timing, and a verifiable invariant that you can press a button "exactly once" and the engine will agree with you exactly once.
