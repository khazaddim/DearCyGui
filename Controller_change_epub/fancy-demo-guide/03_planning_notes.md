# Planning Notes For A Controller-Image Demo

## Recommended architecture

Keep the demo in three layers.

### 1. Input state layer

A small per-slot state object should own:

- connected
- controller name
- held buttons
- latest axis values
- recent event history
- optional player metadata such as joined, color, or profile label

The current fancy demo already does most of this.

### 2. Presentation mapping layer

Add a mapping from enum values to art regions.

For buttons:

- `GamepadButton.SOUTH` -> A/Cross highlight region
- `GamepadButton.EAST` -> B/Circle highlight region
- shoulder, stick click, d-pad, paddles, touchpad -> overlay ids

For axes:

- `LEFT_X`, `LEFT_Y` -> left stick thumb offset
- `RIGHT_X`, `RIGHT_Y` -> right stick thumb offset
- `LEFT_TRIGGER`, `RIGHT_TRIGGER` -> fill bars or trigger glow intensity

This mapping should be data-first, not hard-coded into callbacks.

### 3. Render layer

Render code should read the state and the mapping, then update:

- controller image highlights
- stick positions
- trigger bars
- per-player labels
- join prompts and disconnected overlays

## Design choices worth making early

### Single generic controller image vs branded variants

A generic Xbox-shaped layout is easier because SDL button names already align well with the common south/east/west/north convention.
If later you want PlayStation-style art, keep the internal mapping enum-based and swap only the label art.

### Any-controller lobby vs per-slot panels

For the next fancy version, a strong layout is:

- top: one hero controller image showing the currently focused slot
- side or bottom: compact slot cards for all connected controllers

That gives you room to showcase one beautiful controller image without losing the multi-controller story.

### Join flow

A clean event-driven join model is:

- disconnected slot: show ghost card
- any `START` press on an unclaimed slot: mark joined
- `BACK` or disconnect: clear joined state

That flow maps naturally onto `GamepadButtonHandler` and does not require continuous button polling.

## Suggested next milestones

1. Extract the per-slot state into a dedicated class or dataclass-like object.
2. Add a view-model layer that translates buttons and axes into visual properties.
3. Build a text-plus-image demo for one controller first.
4. Expand to multiple slot cards once the single-controller rendering feels right.
5. Decide whether the API needs a real connection handler before polishing the public demo.

## Bottom line

You do not need to redesign the input path again before making the demo beautiful.
The current handler-driven state model is already a workable foundation for a Microsoft-style controller visualization.
