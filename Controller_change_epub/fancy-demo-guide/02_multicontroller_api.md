# Multi-Controller API Summary

## Gamepad snapshot API

`viewport.gamepads` exposes 8 `Gamepad` objects, one per slot.

Each `Gamepad` provides:

- `slot`
- `connected`
- `name`
- `is_button_down(button)`
- `is_button_pressed(button)`
- `is_button_released(button)`
- `get_axis(axis)`

Polling still has value when you want a tight gameplay loop or when you need a snapshot of all current inputs every frame.

## GamepadButtonHandler

Use `GamepadButtonHandler` when you care about discrete button edges.

Constructor shape:

```python
handler = dcg.GamepadButtonHandler(
    C,
    controller=-1,
    button=dcg.GamepadButton.SOUTH,
    on_press=True,
    callback=on_button,
)
```

Important details:

- `controller=-1` means any connected controller
- `controller=0..7` binds to a specific slot
- `on_press=True` fires on press
- `on_press=False` fires on release
- callback `data` is `(slot, GamepadButton)`

This is the right tool for:

- press start to join
- face-button prompts
- menu navigation
- toggles
- join and ready flows

## GamepadAxisHandler

Use `GamepadAxisHandler` when you care about analog changes.

Constructor shape:

```python
handler = dcg.GamepadAxisHandler(
    C,
    controller=-1,
    axis=dcg.GamepadAxis.LEFT_X,
    deadzone=0.15,
    callback=on_axis,
)
```

Important details:

- callback `data` is `(slot, float)`
- `sender.axis` identifies which axis triggered the callback
- the value is already deadzone-filtered
- the callback fires only when the filtered value changes

This is the right tool for:

- live stick visualization
- trigger fill meters
- analog steering or cursor control
- low-noise telemetry for UI animation

## Practical split for future demos

A good working rule is:

- use handlers to maintain a per-slot state cache
- use rendering code to visualize that cache
- use `viewport.gamepads` only for connection snapshots unless the demo really needs continuous polling

That keeps the fancy demo stable as complexity grows.

## API gap that still exists

There is currently no dedicated controller-added or controller-removed handler.
Connection changes are still discovered by observing `viewport.gamepads[i].connected` over time.

If you want the API to support a fully event-driven controller-image demo, the missing primitive is a connection handler that reports slot add/remove transitions.
