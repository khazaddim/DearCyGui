# Fancy_Demo.py Walkthrough

## Bootstrap

The first lines rewrite `sys.path` so the demo imports the installed DearCyGui package from the active virtual environment instead of the local source tree. That is important in this repository because the runtime extension module lives in site-packages, not in the source folder.

## Static lookup tables

Two tables define the displayed names:

- `BUTTON_NAMES` maps `GamepadButton` enum values to readable labels
- `AXIS_NAMES` maps `GamepadAxis` values to short axis labels

Those tables are already a useful seam for a visual controller layout. Later, the same enum values can map to image hotspots instead of text labels.

## State model

The demo keeps minimal per-slot state:

- `held[slot]`: set of currently held buttons
- `press_counts[slot]`: total button press callbacks seen for the slot
- `release_counts[slot]`: total release callbacks seen for the slot
- `axis_event_counts[slot]`: total axis callbacks seen for the slot
- `axis_values[slot]`: latest filtered axis value for each axis
- `history[slot]`: newest-first event log
- `connected[slot]` and `names[slot]`: cached connection snapshot

This is the right shape for a future view-model. The UI is already downstream of a compact state object rather than directly querying SDL every frame.

## Handler wiring

The window attaches:

- one press handler per named button
- one release handler per named button
- one axis handler per axis
- one render handler for connection refresh

That means the demo listens for semantic events, not raw SDL packets. The callbacks already arrive normalized to `(slot, button)` or `(slot, value)`.

## Update flow

### Button press

`_on_button_press`:

- adds the button to the held set
- increments the press count
- appends a `+Label` entry to history
- refreshes the slot UI

### Button release

`_on_button_release`:

- removes the button from the held set
- increments the release count
- appends a `-Label` entry to history
- refreshes the slot UI

### Axis change

`_on_axis`:

- writes the latest filtered value for `sender.axis`
- increments the axis callback count
- refreshes the slot UI

### Connection refresh

`_on_render`:

- checks `viewport.gamepads`
- compares `connected` and `name` against cached values
- clears stale held, axis, and history state on disconnect
- refreshes only when the snapshot changes

This is the only polling-like part left, and it is limited to connection metadata.

## Why this is a good base for a controller-image demo

A picture-driven demo usually needs three layers:

- static art
- a state model describing what is active
- a renderer that highlights active controls

The current fancy demo already has the second layer. The next version mostly needs a different renderer.
