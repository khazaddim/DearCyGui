---
name: secondary-viewport-game-loop
description: "Use when: adding a secondary viewport / second OS window / second physical screen to a DearCyGui game or tool that uses frame-based rendering and event-driven gamepad handlers. Covers why run_viewport_loop() conflicts with frame-latched GamepadButtonHandler edges, how to render multiple viewports from one manual loop, and how to place a hidden operator screen on another monitor in fullscreen."
---

# Secondary Viewport Game Loop

Use this skill when you want a DearCyGui app to open a second viewport on another physical monitor while keeping the main app on the existing frame-driven input model.

This is the recommended pattern for the game work built on `Fancy_Demo.py`: a player-facing viewport plus a second viewport for a hidden operator screen, debug map, GM tools, or off-screen controller diagnostics.

## When To Use

- "second viewport"
- "secondary window"
- "second monitor" / "second physical screen"
- "fullscreen operator screen"
- "fullscreen on monitor 2"
- "operator screen" / "GM screen" / "hidden map screen"
- Any multi-viewport DearCyGui workflow that also depends on `GamepadButtonHandler`
- Any task that mixes event-driven gamepad handlers with a second OS-level viewport

## Core Rule

If the app depends on `GamepadButtonHandler` edge events (`pressed this frame` / `released this frame`), do **not** drive the viewport with `run_viewport_loop()`.

Why:

- `GamepadButtonHandler` reads frame-latched button edge state.
- In DearCyGui, those edge flags are cleared at the start of `render_frame()` and then repopulated from events processed during that frame.
- `run_viewport_loop()` calls `wait_events()` before `render_frame()` when `wait_for_input=True`.
- That ordering can process SDL button events too early, so the button edge is gone before the handler reads it.
- Axis values usually still appear to work because they are persistent level state, but buttons and D-pad presses can be missed.

So the safe pattern is:

1. Create the second viewport/context.
2. Keep the custom frame loop.
3. Render every active viewport manually inside the same loop.

## Recommended Pattern

- Main gameplay / controller UI stays on the existing manual frame loop.
- Secondary viewport is created with its own `dcg.Context()`.
- The app keeps a reference to that extra context.
- One shared async loop renders all active viewports.
- The main viewport remains the source of gamepad handler logic.

## Minimal Example

```python
import asyncio
import dearcygui as dcg
from dearcygui.utils.asyncio_helpers import AsyncPoolExecutor


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


class MultiViewportDemo:
    def __init__(self):
        self.primary = dcg.Context()
        self.primary.queue = AsyncPoolExecutor()
        self.primary.viewport.wait_for_input = True
        self.primary.viewport.initialize(
            width=1280,
            height=920,
            title="Player View",
        )

        with dcg.Window(self.primary, primary=True):
            dcg.Text(self.primary, value="Main game / controller UI")

        self.secondary = None

    def open_secondary_viewport(self):
        if self.secondary is not None and self.secondary.running:
            return

        secondary = dcg.Context()
        secondary.queue = AsyncPoolExecutor()
        secondary.viewport.wait_for_input = True
        secondary.viewport.initialize(
            width=900,
            height=700,
            title="Operator View",
        )

        displays = secondary.viewport.displays
        if len(displays) > 1:
            operator_display = displays[1]
            secondary.viewport.x_pos = int(operator_display.bounds.x1)
            secondary.viewport.y_pos = int(operator_display.bounds.y1)
            secondary.viewport.fullscreen = True

        with dcg.Window(secondary, primary=True):
            dcg.Text(secondary, value="Hidden map / debug screen")
            with dcg.Plot(secondary, label="Map Probe", width=-1, height=-1):
                with dcg.DrawInPlot(secondary, no_legend=True):
                    dcg.DrawLine(secondary, p1=(-50, -50), p2=(50, 50), color=(80, 220, 160, 255), thickness=-2)
                    dcg.DrawCircle(secondary, center=(0, 0), radius=-6, fill=(240, 200, 80, 255), color=(20, 20, 20, 255), thickness=-1)

        self.secondary = secondary


async def main_loop(app, frame_rate=120.0):
    frame_time = 1.0 / frame_rate

    while app.primary.running:
        app.primary.viewport.render_frame()

        if app.secondary is not None and app.secondary.running:
            app.secondary.viewport.render_frame()

        await asyncio.sleep(frame_time)


if __name__ == "__main__":
    app = MultiViewportDemo()
    app.open_secondary_viewport()
    loop.run_until_complete(main_loop(app))
```

## Fancy_Demo Direction

For the current gamepad demo architecture, the expected next step is:

- Keep `Fancy_Demo.py`'s custom loop.
- Add a second `dcg.Context()` for the hidden screen.
- Put the pannable map or director/debug information in that second viewport.
- Continue letting button/axis handlers update shared app state from the main loop.
- Render both viewports each frame.

A good mental model is:

- **main viewport** = player-facing controller/game UI
- **secondary viewport** = hidden map, referee tools, encounter controls, telemetry, debug overlays

## Scheduling Notes

If a UI callback needs to open the second viewport, schedule the operation on the active asyncio loop instead of returning a bare coroutine object.

Good:

```python
callback=lambda: loop.create_task(self.open_secondary_async())
```

Also acceptable when already inside async-aware code:

```python
asyncio.get_running_loop().create_task(self.open_secondary_async())
```

Avoid this pattern by itself:

```python
callback=lambda: self.open_secondary_async()
```

That only creates a coroutine object; it does not actually run it.

If viewport construction does not need `await`, a normal synchronous method is even simpler and is often the cleanest choice.

## Physical Monitor Notes

DearCyGui already exposes what you need for the common second-screen case:

- `viewport.displays` to inspect available monitors
- `viewport.x_pos` / `viewport.y_pos` to move the viewport
- `viewport.fullscreen = True` to make the operator screen fill the monitor

The usual pattern is:

1. initialize the secondary viewport
2. query `displays`
3. move the viewport to the target display's `bounds.x1` / `bounds.y1`
4. set `fullscreen = True`

That is usually a better fit for a hidden operator screen than `maximized`, because fullscreen removes normal OS chrome and fills the entire display.

That monitor-placement concern is separate from the gamepad-input concern:

- monitor placement = where the second viewport appears
- fullscreen = whether it occupies the whole target monitor
- shared manual render loop = how button handlers remain reliable

Treat them as two separate implementation steps.

## Fullscreen Example

```python
secondary = dcg.Context()
secondary.queue = AsyncPoolExecutor()
secondary.viewport.wait_for_input = True
secondary.viewport.initialize(
    width=900,
    height=700,
    title="Operator View",
)

displays = secondary.viewport.displays
if len(displays) > 1:
    screen2 = displays[1]
    secondary.viewport.x_pos = int(screen2.bounds.x1)
    secondary.viewport.y_pos = int(screen2.bounds.y1)
    secondary.viewport.fullscreen = True
```

If there is only one display, you can skip fullscreen or choose to fullscreen on the primary display instead.

## Pitfalls

- Do not switch the main gamepad demo back to `run_viewport_loop()` just because a second viewport exists.
- Do not assume button handlers are equivalent to axis handlers; button edges are more sensitive to event ordering.
- Do not create a second viewport and forget to render it every frame.
- Do not return unscheduled coroutine objects from button callbacks.
- Do not assume monitor selection happens automatically when you set fullscreen; place the viewport on the intended display first when deterministic screen choice matters.
- Do not overcomplicate the first spike: start with a text label or simple plot before building the full hidden map UI.

## Recommended First Spike

Build the smallest proof first:

1. Main viewport with the current `Fancy_Demo.py` handler model.
2. Secondary viewport with one text label or one simple plot.
3. One shared manual loop that renders both.
4. Verify buttons, sticks, and mouse interaction still feel correct.
5. Only then move the map/debug tools into the second screen.
