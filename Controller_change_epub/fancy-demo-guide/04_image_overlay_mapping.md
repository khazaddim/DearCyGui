# Image Overlay Mapping

## Goal

The next fancy demo should separate controller art from controller state.
The input system should continue producing clean per-slot state, while a mapping layer decides how that state affects the visual presentation.

That keeps the rendering code replaceable. You can swap from a text panel to a Microsoft-style controller image without changing the handler logic.

## Recommended data model

Use a table that maps API enums to visual targets.

For buttons, each entry should describe:

- the `GamepadButton` enum value
- a stable visual id
- the kind of overlay to drive
- optional label text
- optional styling such as color, glow, or pressed depth

Example shape:

```python
BUTTON_OVERLAYS = {
    dcg.GamepadButton.SOUTH: {
        "overlay_id": "face_south",
        "label": "A / Cross",
        "effect": "glow",
    },
    dcg.GamepadButton.EAST: {
        "overlay_id": "face_east",
        "label": "B / Circle",
        "effect": "glow",
    },
    dcg.GamepadButton.START: {
        "overlay_id": "start",
        "label": "Start",
        "effect": "pulse",
    },
}
```

For axes, each entry should describe:

- the `GamepadAxis` enum value
- the visual element id
- whether it is a 2D stick, 1D trigger, or scalar bar
- the coordinate transform or fill transform

Example shape:

```python
AXIS_OVERLAYS = {
    dcg.GamepadAxis.LEFT_X: {
        "overlay_id": "left_stick_thumb",
        "group": "left_stick",
        "role": "x",
        "max_offset": 18,
    },
    dcg.GamepadAxis.LEFT_Y: {
        "overlay_id": "left_stick_thumb",
        "group": "left_stick",
        "role": "y",
        "max_offset": 18,
        "invert": False,
    },
    dcg.GamepadAxis.LEFT_TRIGGER: {
        "overlay_id": "left_trigger_fill",
        "role": "fill",
        "max_fill": 1.0,
    },
}
```

## Button mapping strategy

A strong first version is to split buttons into three render behaviors.

### 1. Binary glow overlays

Use for:

- face buttons
- d-pad buttons
- shoulder buttons
- stick clicks
- start/back/guide
- paddles and touchpad

The logic is simple: if the button is in `held[slot]`, enable the overlay; otherwise disable it.

### 2. Edge-triggered flash overlays

Use for:

- join prompts
- confirm pulses
- menu feedback

These should be driven from the history or press event path, not just the held set. A short-lived animation token is often better than checking current held state.

### 3. State badges

Use for:

- connected/disconnected
- player joined
- active/focused slot

These are not button overlays, but they belong in the same presentation mapping layer.

## Axis mapping strategy

Axes need two different treatments.

### Sticks

For left and right sticks, combine X and Y into one thumb position:

- `LEFT_X` and `LEFT_Y` drive one left-stick overlay
- `RIGHT_X` and `RIGHT_Y` drive one right-stick overlay

A good transform is:

```python
pixel_x = axis_x * max_offset
pixel_y = axis_y * max_offset
```

Because the API already reports filtered values, the stick thumb can return cleanly to center when the handler emits `0.0`.

### Triggers

For triggers, use a fill or intensity transform:

```python
fill_amount = trigger_value
opacity = 0.25 + 0.75 * trigger_value
```

That usually reads better than physically moving a trigger image.

## Suggested render objects

If you build this in DearCyGui, the controller art can be layered like this:

1. Base controller image
2. Button glow overlays
3. Stick thumb overlays
4. Trigger fill bars or masks
5. Text labels for the slot and controller name
6. Optional event callouts or recent button chips

That layering works whether you use one hero controller image or one controller image per slot.

## One-controller hero layout

For the first visual pass, build only one hero controller panel.
Tie it to a selected slot, then show the selected slot's state on the image.
Keep the other slots as simpler cards.

That gives you:

- one image asset to tune
- a clear place to test glow and stick motion
- a way to keep the multi-controller story without drawing eight large controllers

## Slot focus rules

A practical focus policy is:

- if only one controller is connected, focus that slot
- if a slot receives the newest button press, focus that slot
- if the focused slot disconnects, choose the lowest connected slot

That policy works well for a demo because the image naturally follows whoever is interacting.

## Asset planning advice

Do not start with branded Microsoft artwork if distribution or licensing is unclear.
Start with either:

- your own simplified controller silhouette
- a neutral controller illustration
- a layered SVG or PNG set you fully control

The mapping system should not care which art pack is active.

## Minimal implementation path

A good order of work is:

1. Keep the current handler-driven state cache.
2. Add a `focused_slot` variable.
3. Add a data mapping from enums to overlay ids.
4. Render one controller image with highlight layers.
5. Drive binary button glows from `held[focused_slot]`.
6. Drive stick thumb position from `axis_values[focused_slot]`.
7. Drive trigger fills from trigger axis values.
8. Only after that, add polish such as animations and per-slot cards.

## Bottom line

The important design move is to avoid wiring button callbacks directly to drawing primitives.
Instead, handlers should update state, and the image renderer should read state through a stable mapping table.

That is the cleanest path from the current text-based fancy demo to a controller-image demo that is still maintainable.
