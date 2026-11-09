## ADDED Requirements

### Requirement: Controller-capable native initialization

The system SHALL build SDL with joystick/gamepad support on Windows, initialize the video and gamepad subsystems, and link the extension against the updated native archive. Initialization and device-open errors SHALL be reported explicitly through existing error mechanisms rather than silently succeeding in a controller-disabled mode. Zero devices SHALL be a valid successful initialization.

#### Scenario: Windows controller path is enabled
- **WHEN** the Windows extension is built and initialized for controller use
- **THEN** the effective SDL build settings enable joystick support
- **AND** its SDL instance initializes the gamepad subsystem and discovers a connected supported device
- **AND** rebuilding a changed SDL archive causes the consuming extension to relink

#### Scenario: Gamepad initialization fails
- **WHEN** SDL gamepad initialization fails
- **THEN** the SDL error is surfaced explicitly
- **AND** initialization does not silently report controller-capable success using video-only fallback

### Requirement: Stable controller enumeration

`viewport.gamepads` SHALL return a cached tuple of exactly eight `Gamepad` objects for slots `0..7`, regardless of connection count. `viewport.gamepad_count` SHALL return the number of tracked connected slots. Each object SHALL retain its identity across property access and connection changes.

#### Scenario: No controllers are connected
- **WHEN** an application accesses `viewport.gamepads` without controllers
- **THEN** it receives eight objects whose slots are `0..7` and whose connection states are false
- **AND** `viewport.gamepad_count` is zero
- **AND** repeated access returns the same tuple and same slot objects

#### Scenario: Two controllers occupy independent slots
- **WHEN** two controllers are connected and discovered
- **THEN** two distinct slots report connected and the count is two
- **AND** the tuple still has eight elements
- **AND** connecting or removing another controller does not renumber an existing occupant

### Requirement: Controller properties and neutral disconnected state

Each `Gamepad` SHALL expose read-only `slot`, `connected`, and `name` properties. `name` SHALL be the SDL hardware name when available, not an application player label, and SHALL be empty when disconnected. Valid disconnected slots SHALL return false for all button queries and `0.0` for all axis queries.

#### Scenario: Query hardware identity
- **WHEN** an application reads a connected slot's properties
- **THEN** its slot is within `0..7`, its connection state is true, and its available SDL hardware name is returned as a string

#### Scenario: Query an empty slot
- **WHEN** an application queries a disconnected valid slot
- **THEN** its name is empty, button down/pressed/released are false, and axes are `0.0`

### Requirement: Public gamepad enums and input validation

The system SHALL expose `GamepadButton` names `SOUTH`, `EAST`, `WEST`, `NORTH`, `BACK`, `GUIDE`, `START`, `LEFT_STICK`, `RIGHT_STICK`, `LEFT_SHOULDER`, `RIGHT_SHOULDER`, `DPAD_UP`, `DPAD_DOWN`, `DPAD_LEFT`, `DPAD_RIGHT`, `MISC1`, `RIGHT_PADDLE1`, `LEFT_PADDLE1`, `RIGHT_PADDLE2`, `LEFT_PADDLE2`, and `TOUCHPAD`, matching SDL values `0..20`. It SHALL expose `GamepadAxis` names `LEFT_X`, `LEFT_Y`, `RIGHT_X`, `RIGHT_Y`, `LEFT_TRIGGER`, and `RIGHT_TRIGGER`, matching SDL values `0..5`.

Polling SHALL accept valid enum members, case-insensitive names, and valid numeric enum values through shared conversion helpers. Handler button/axis setters SHALL accept valid enum members or names. Invalid public slot, button, axis, or deadzone inputs SHALL raise explicit type/value errors rather than masquerading as disconnected neutral input.

#### Scenario: Runtime mappings match SDL
- **WHEN** the public enums are inspected and used for native input queries
- **THEN** each listed name maps to its corresponding SDL button or axis
- **AND** polling a member, its lowercase name, or its numeric value addresses the same input

#### Scenario: Invalid input is rejected
- **WHEN** callers supply an out-of-range slot, unknown button/axis name, invalid numeric polling value, or unsupported handler button/axis type
- **THEN** an appropriate type/value error is raised before native querying

### Requirement: Button polling and frame latches

`Gamepad` SHALL provide `is_button_down`, `is_button_pressed`, and `is_button_released`. Down SHALL reflect current held state. Pressed/released SHALL latch real up-to-down/down-to-up transitions for one consuming viewport frame, not repeat while held, and not consume state when queried.

#### Scenario: Press, hold, and release
- **WHEN** a connected controller presses a button, holds it over subsequent frames, and releases it
- **THEN** pressed is true for the press frame only, down stays true while held, and released is true for the release frame only
- **AND** repeated queries within a frame return the same result

#### Scenario: Multiple transitions within a frame
- **WHEN** a button transitions down and up before the frame's input snapshot is published
- **THEN** both pressed and released are true in that frame and down is false
- **AND** each latch is false in the next frame without further transitions

#### Scenario: Duplicate down events
- **WHEN** an already-held button receives another down event without an intervening release
- **THEN** no new pressed edge is generated

### Requirement: Axis polling normalization

`Gamepad.get_axis` SHALL expose current raw normalized values without handler deadzone filtering. Stick axes SHALL stay in `[-1.0, 1.0]` and triggers in `[0.0, 1.0]`, including exact native extrema.

#### Scenario: Signed stick extrema
- **WHEN** a stick axis receives SDL values `-32768`, `0`, and `32767`
- **THEN** its normalized outputs are `-1.0`, `0.0`, and `1.0` within floating-point tolerance
- **AND** no output escapes the specified range

#### Scenario: Trigger normalization
- **WHEN** a trigger is released, partially pressed, and fully pressed
- **THEN** its outputs stay in `[0.0, 1.0]` with released `0.0` and fully pressed `1.0`

### Requirement: Button handlers and callback contract

`GamepadButtonHandler` SHALL default to `controller=-1`, `button=GamepadButton.SOUTH`, and `on_press=True`. `controller=None` SHALL normalize to `-1` (any slot); specific selectors SHALL be `0..7`. `on_press=False` SHALL monitor releases. Enabled handlers SHALL queue one callback per selected slot with the corresponding edge in a frame, using sender=handler, target=attached item, and data exactly `(int slot, GamepadButton button)`.

#### Scenario: Specific slot filtering
- **WHEN** a handler selecting slot zero observes matching input on slots zero and one
- **THEN** only slot zero queues its callback, with the selected button as an enum member rather than a bare integer

#### Scenario: Any-slot simultaneous dispatch
- **WHEN** two slots press the selected button in one frame with `controller=None`
- **THEN** the handler's controller property reads `-1`
- **AND** two callbacks carry the respective slots with no duplicate callbacks on subsequent held frames

#### Scenario: Release and disabled behavior
- **WHEN** a release handler observes a release and the same handler is subsequently disabled
- **THEN** it queues one release callback while enabled and none while disabled
- **AND** sender, target, and tuple shape remain consistent with normal dispatch

### Requirement: Axis handlers and deadzone changes

`GamepadAxisHandler` SHALL default to `controller=-1`, `axis=GamepadAxis.LEFT_X`, and deadzone `0.15`, with the same slot-selector behavior as button handlers. Deadzone SHALL be finite and within `[0.0, 1.0]`. Values with absolute magnitude strictly below deadzone SHALL filter to `0.0`; values at the boundary SHALL retain their normalized magnitude. A callback SHALL be queued only when the filtered value differs from that slot's last reported value by more than `1e-4`, with sender=handler, target=attached item, and data exactly `(int slot, float filtered_value)`.

#### Scenario: Noise, movement, and return to center
- **WHEN** an axis moves inside the deadzone, moves to `0.5`, stays there, and returns inside the deadzone
- **THEN** rest/noise queues no callback, movement queues `(slot, 0.5)`, the unchanged value does not repeat, and return queues one `(slot, 0.0)`

#### Scenario: Boundary and change threshold
- **WHEN** a filtered value reaches the configured deadzone boundary or changes by at most `1e-4`
- **THEN** the boundary is not filtered away
- **AND** a change at or below the epsilon does not queue a new callback

#### Scenario: Independent history and non-consuming checks
- **WHEN** two selected slots change axes and the handler's state is checked repeatedly before dispatch
- **THEN** history remains independent per slot and checks do not consume callbacks
- **AND** dispatch queues each changed slot once

#### Scenario: Invalid deadzone and selector reset
- **WHEN** a deadzone is NaN, infinite, or outside `[0, 1]`
- **THEN** assignment raises a value error
- **AND** changing a valid controller or axis selection resets its prior per-slot history

### Requirement: Discovery, hot-plug, and resource lifetime

The native manager SHALL discover supported devices present at startup and assign new devices to the lowest free slot without duplicate assignment. It SHALL initialize current levels without fabricating historical button edges, clear occupant state on disconnect/reuse, and keep storage bounded to eight slots. Tracked handles SHALL be closed on removal or final participating-viewport teardown without disrupting another live viewport or ImGui's separately owned handles.

#### Scenario: Device already connected at startup
- **WHEN** a supported controller is held or deflected before viewport initialization
- **THEN** discovery exposes its connection/name and current button/axis levels
- **AND** it does not fabricate a press that occurred before tracking began

#### Scenario: Disconnect and slot reuse
- **WHEN** a non-neutral controller disconnects and another controller occupies its freed slot
- **THEN** old button/axis/name/edge state is cleared and the stable slot object reflects the new occupant
- **AND** an axis handler that last reported nonzero emits at most one neutral update for the disconnect and does not leak history into the new occupant

#### Scenario: Capacity and duplicate notifications
- **WHEN** eight slots are occupied and another device or duplicate add notification arrives
- **THEN** tracked count remains eight and existing occupants remain unchanged
- **AND** no duplicate slot or extra tracked handle is created

#### Scenario: Teardown and recreation
- **WHEN** one of two live viewports is destroyed, then the final viewport is destroyed and a new one is initialized
- **THEN** the surviving viewport initially retains usable state
- **AND** final teardown releases manager handles and pending snapshots
- **AND** recreation rediscovers connected devices without stale names, edges, or handles

### Requirement: Event waiting and per-viewport edge ownership

Input collected by `wait_events()` or another viewport's SDL event pump SHALL remain pending until each participating viewport publishes it for its next consuming frame. Rendering one viewport SHALL not erase another's pending input. Each handler/slot/edge SHALL dispatch at most once per consuming frame and SHALL not replay on frames without new transitions. Controller input SHALL trigger needed rendering with `wait_for_input=True`.

#### Scenario: Wait before render
- **WHEN** button input is processed by `wait_events()` before `render_frame()`, including through `run_viewport_loop()`
- **THEN** the next frame's polling and handlers observe that input exactly once
- **AND** no unconditional global begin-frame clear discards it

#### Scenario: Alternating viewports
- **WHEN** two initialized viewports are rendered alternately after a button transition is pumped by the first
- **THEN** both observe that transition in their respective next consuming frame
- **AND** later frames without transitions do not duplicate callbacks

#### Scenario: Queued reads during lifecycle changes
- **WHEN** queued callbacks query names and levels while the main thread processes input, hot-plug, or teardown
- **THEN** the reads use synchronized valid state without data races or mutable borrowed-name pointers
- **AND** upstream's SDL main-thread and lock-order requirements remain intact

### Requirement: Legacy input compatibility

Existing `Key.GAMEPAD*` handlers SHALL remain functional through ImGui's AutoFirst controller path. The new per-slot API SHALL operate independently of UI navigation/capture settings, without enabling navigation globally or changing existing keyboard/mouse handler callback values.

#### Scenario: First-controller legacy input and second-controller direct input
- **WHEN** the first ImGui controller presses a mapped button and a second controller presses its own button
- **THEN** the legacy handler responds through the existing first-controller path
- **AND** the new handlers distinguish each controller's slot independently
- **AND** existing input handlers retain their upstream callback formats

### Requirement: Aligned documentation, stubs, and validation demo

Runtime exports, public stubs, and documentation SHALL agree on the implemented controller names, defaults, types, tuple payloads, frame semantics, and capacity limits. The port SHALL supply an upstream-compatible `Fancy_Demo.py` with event-driven button/axis updates, connection/name tracking, eight slots, and the existing fullscreen and plot interaction probes. Validation SHALL distinguish deterministic connected-input tests from physical observations and unperformed checks.

#### Scenario: Event-driven interactive validation
- **WHEN** two physical controllers are used in the adapted demo while the plot is panned/zoomed and fullscreen is toggled
- **THEN** each slot's held state, press/release counts, axis values, names, and history reflect its own controller
- **AND** disconnect/reconnect clears stale displayed state
- **AND** missed button callbacks are not hidden by button/axis polling

#### Scenario: Installed API and deterministic evidence
- **WHEN** the installed rebuilt extension, its stubs, and controller tests are checked
- **THEN** they agree on exported APIs and callback shapes
- **AND** connected-input tests use the same linked SDL instance as the extension
- **AND** unavailable hardware/platform validation is recorded as unverified rather than passed
