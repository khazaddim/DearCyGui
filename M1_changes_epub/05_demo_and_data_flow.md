# The Demo and Data Flow

## The Demo: `Small_Input_Demo.py`

```python
async def main_loop(viewport, demo):
    while viewport.context.running:
        demo.poll_gamepads()
        viewport.render_frame()
        await asyncio.sleep(1.0 / 60.0)
```

**Why `viewport.context.running` instead of `viewport.running`?** The `running` property lives on the `Context`, not the `Viewport`. This matches the pattern in `asyncio_helpers.py`.

**Why `asyncio.sleep(1/60)`?** Limits the poll rate to ~60 fps. Without it, the loop would spin as fast as possible, wasting CPU.

**Why a custom `main_loop` instead of `run_viewport_loop`?** We need to call `poll_gamepads()` each frame to update the display. The built-in `run_viewport_loop` doesn't have a hook for per-frame polling.

```python
def poll_gamepads(self):
    gamepads = self.C.viewport.gamepads
    for i, gp in enumerate(gamepads):
        if gp.connected:
            pressed = []
            for btn in BUTTON_NAMES:
                if gp.is_button_down(btn):
                    pressed.append(BUTTON_NAMES[btn])
            ...
```

**Why poll every frame?** M1 is polling-based — there are no callbacks/handlers yet (that's M3). The game loop asks "what's pressed right now?" every frame. This is a perfectly valid pattern for game development.

---

## Data Flow Summary

When you press the A button on controller 2:

```
 1. Hardware sends USB signal
 2. OS driver translates to SDL event
 3. SDL queues: SDL_EVENT_GAMEPAD_BUTTON_DOWN,
    which=<sdl_id>, button=0, down=true
 4. processEvents() reads event from queue
 5. find_gamepad_slot(<sdl_id>) → slot 1
 6. g_gamepads[1].buttons[0] = true
 7. needsRefresh = true (triggers redraw)
 8. Python: gp.is_button_down(GamepadButton.SOUTH)
 9. → dcg_gamepad_button_down(1, 0)
10. → g_gamepads[1].buttons[0] → true
11. Demo shows "A / Cross" in slot 1's button list
```

When you release:

```
1. SDL queues: SDL_EVENT_GAMEPAD_BUTTON_UP,
   button=0, down=false
2. g_gamepads[1].buttons[0] = false
3. Next poll: is_button_down returns false
4. "A / Cross" disappears from the display
```

This flow shows how a single button press traverses all four layers — from USB hardware through SDL, into C++ state, across the Cython bridge, and up to your Python code.
