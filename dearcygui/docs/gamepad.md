# Gamepad / Game Controller Input

**DearCyGui** has first-class multi-controller support built on top of
SDL3's GameController API. Up to 8 controllers can be connected
simultaneously and addressed individually by slot index.

There are two complementary ways to consume gamepad input:

1. **Polling** — read the current state of any button or axis from your
   game loop / render callback (`viewport.gamepads[i]`).
2. **Handlers** — register a `GamepadButtonHandler` or
   `GamepadAxisHandler` and receive a callback only when the relevant
   event occurs.

Pick the polling style for tight game loops and the handler style for
event-driven UI or per-controller "press start to join" flows.

---

## Detecting and addressing controllers

`viewport.gamepads` returns a tuple of 8 `Gamepad` objects, one per
controller slot:

```python
import dearcygui as dcg

C = dcg.Context()
with dcg.Viewport(C, title="Gamepad demo") as V:
    pass

for pad in V.gamepads:
    if pad.connected:
        print(f"Slot {pad.slot}: {pad.name}")
```

Each `Gamepad` exposes:

| Attribute / method | Description |
| --- | --- |
| `slot` | Slot index (0-7). |
| `connected` | `True` while a physical controller occupies this slot. |
| `name` | Hardware controller name reported by SDL3 (e.g. `"Xbox Wireless Controller"`). Read-only; identifies the device, not the player. |
| `is_button_down(button)` | `True` while the button is held. |
| `is_button_pressed(button)` | `True` only on the frame the button transitioned from up to down. |
| `is_button_released(button)` | `True` only on the frame the button transitioned from down to up. |
| `get_axis(axis)` | Current axis value (sticks: `-1.0..+1.0`, triggers: `0.0..1.0`). |

Slots are stable once assigned. When a controller is unplugged its slot
becomes available again and the next plugged-in controller fills the
lowest empty slot.

The edge-detection state behind `is_button_pressed` / `is_button_released`
is cleared automatically at the start of every render frame, so each
press is reported for exactly one frame regardless of how many times you
poll within that frame.

---

## Polling pattern (typical game loop)

Polling is the simplest and lowest-overhead approach for player-controlled
games. Read what you need each frame:

```python
import dearcygui as dcg

C = dcg.Context()
with dcg.Viewport(C, title="Polling demo") as V:
    pass

player_x = 0.0
player_y = 0.0

def frame_callback():
    global player_x, player_y
    pad = V.gamepads[0]
    if pad.connected:
        # Movement from the left stick, deadzone applied manually.
        lx = pad.get_axis(dcg.GamepadAxis.LEFT_X)
        ly = pad.get_axis(dcg.GamepadAxis.LEFT_Y)
        if abs(lx) > 0.15:
            player_x += lx * 0.1
        if abs(ly) > 0.15:
            player_y += ly * 0.1
        # Edge-detected "jump" on A / Cross.
        if pad.is_button_pressed(dcg.GamepadButton.SOUTH):
            print("Jump!")

V.handlers = [dcg.RenderHandler(C, callback=frame_callback)]

while V.render_frame():
    pass
```

`is_button_down` is for continuous actions ("hold to run"),
`is_button_pressed` and `is_button_released` are for one-shot actions
("jump on press", "release to charge").

---

## Handlers: `GamepadButtonHandler`

`GamepadButtonHandler` fires a callback when a specific button is pressed
or released. It can listen to a single controller or to *any*
controller, which is the convenient pattern for "press any button to
start" / "press start to join" screens.

```python
import dearcygui as dcg

C = dcg.Context()
with dcg.Viewport(C, title="Handler demo") as V:
    pass

def on_press(sender, target, data):
    slot, button = data
    print(f"Slot {slot} pressed {button}")

# Listen for SOUTH (A / Cross) on *any* controller.
V.handlers = [
    dcg.GamepadButtonHandler(
        C,
        controller=-1,                       # -1 = any slot, 0..7 = specific
        button=dcg.GamepadButton.SOUTH,
        on_press=True,                       # False to fire on release
        callback=on_press,
    )
]
```

Constructor parameters:

- `controller` (int, default `-1`): `-1` to listen on any slot, otherwise
  `0..7`.
- `button` (`GamepadButton`, default `SOUTH`): which button to watch.
- `on_press` (bool, default `True`): fire on press; set `False` to fire
  on release instead. Create two handlers if you need both edges.

Callback `data` is a `(slot, GamepadButton)` tuple so a single
any-controller handler can identify which player triggered it.

---

## Handlers: `GamepadAxisHandler`

`GamepadAxisHandler` fires a callback whenever an analog axis changes
significantly. A built-in deadzone filter suppresses jitter from
controllers at rest.

```python
import dearcygui as dcg

C = dcg.Context()
with dcg.Viewport(C, title="Axis demo") as V:
    pass

def on_axis(sender, target, data):
    slot, value = data
    print(f"Slot {slot} LEFT_X = {value:+.3f}")

V.handlers = [
    dcg.GamepadAxisHandler(
        C,
        controller=-1,
        axis=dcg.GamepadAxis.LEFT_X,
        deadzone=0.15,                       # |raw| < deadzone -> reported as 0.0
        callback=on_axis,
    )
]
```

Behaviour:

- Raw values within the deadzone are clamped to exactly `0.0` before
  being compared and reported.
- The callback fires only when the filtered value *changes* (per slot in
  any-controller mode). Holding the stick still produces no callbacks.
- Crossing back into the deadzone produces a single callback with
  `value=0.0`, which is the natural place to apply a "return to center"
  action.
- Setting `deadzone=0.0` disables the filter but you will then receive
  callbacks for every micro-movement, including controller noise.

Constructor parameters:

- `controller` (int, default `-1`): `-1` for any slot, otherwise `0..7`.
- `axis` (`GamepadAxis`, default `LEFT_X`): which axis to watch.
- `deadzone` (float, default `0.15`): magnitude below which raw values
  are treated as zero. Must be in `[0, 1]`.

---

## Enums

### `GamepadButton`

SDL3 GameController button mapping. Cross-vendor aliases for the face
buttons:

| Enum | Xbox | PlayStation |
| --- | --- | --- |
| `SOUTH` | A | Cross |
| `EAST`  | B | Circle |
| `WEST`  | X | Square |
| `NORTH` | Y | Triangle |

Other buttons: `BACK`, `GUIDE`, `START`, `LEFT_STICK`, `RIGHT_STICK`,
`LEFT_SHOULDER`, `RIGHT_SHOULDER`, `DPAD_UP`, `DPAD_DOWN`, `DPAD_LEFT`,
`DPAD_RIGHT`, `MISC1`, `RIGHT_PADDLE1`, `LEFT_PADDLE1`, `RIGHT_PADDLE2`,
`LEFT_PADDLE2`, `TOUCHPAD`.

### `GamepadAxis`

| Enum | Range | Notes |
| --- | --- | --- |
| `LEFT_X`, `LEFT_Y` | `-1.0 .. +1.0` | Left stick. `+Y` is down. |
| `RIGHT_X`, `RIGHT_Y` | `-1.0 .. +1.0` | Right stick. `+Y` is down. |
| `LEFT_TRIGGER`, `RIGHT_TRIGGER` | `0.0 .. 1.0` | Triggers idle at `0.0`. |

---

## Migration from `KeyPressHandler` GAMEPAD\* keys

Earlier versions of **DearCyGui** routed gamepad buttons through the
ImGui keyboard layer as members of the `Key` enum (`GAMEPADFACEDOWN`,
`GAMEPADSTART`, `GAMEPADLSTICKLEFT`, etc.) and exposed them via
`KeyPressHandler`. That path is still available for backwards
compatibility but has three significant limitations:

1. **It cannot distinguish between controllers.** All buttons from all
   plugged-in controllers are merged into a single virtual keyboard.
2. **Stick directions are quantised to booleans.** `GAMEPADLSTICKLEFT`
   only tells you "the stick is pushed left past ImGui's internal
   threshold" — there is no analog value.
3. **The trigger axes are not exposed at all.**

The new API solves all three.

| Old code | New code |
| --- | --- |
| `KeyPressHandler(C, key=Key.GAMEPADFACEDOWN, callback=cb)` | `GamepadButtonHandler(C, controller=-1, button=GamepadButton.SOUTH, callback=cb)` |
| `KeyPressHandler(C, key=Key.GAMEPADSTART, callback=cb)` | `GamepadButtonHandler(C, controller=-1, button=GamepadButton.START, callback=cb)` |
| `KeyPressHandler(C, key=Key.GAMEPADLSTICKLEFT, callback=cb)` | `GamepadAxisHandler(C, controller=-1, axis=GamepadAxis.LEFT_X, deadzone=0.5, callback=lambda s,t,d: cb() if d[1] < -0.5 else None)` |
| (no equivalent) | `viewport.gamepads[i].get_axis(GamepadAxis.LEFT_TRIGGER)` |

If you only need a single player and don't care which controller acted,
the migration is purely a name swap. If you want per-player input,
filter on the `slot` value passed to your callback (or instantiate one
handler per `controller=i`).

The legacy `Key.GAMEPAD*` constants remain for compatibility but new
code should prefer `GamepadButton` / `GamepadAxis`.
