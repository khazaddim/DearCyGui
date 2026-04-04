# Spec: Gamepad Input

## ADDED Requirements

### Requirement: Controller Enumeration
The system SHALL provide a `viewport.gamepads` property that returns a list of up to 8 `Gamepad` objects representing connected controllers.

#### Scenario: List connected controllers
- **GIVEN** two Xbox controllers are connected to the system
- **WHEN** the application accesses `viewport.gamepads`
- **THEN** it returns a list containing two `Gamepad` objects with `connected=True`
- **AND** remaining slots have `connected=False`

#### Scenario: Controller slots are stable
- **GIVEN** controller A is connected to slot 0
- **WHEN** controller B connects
- **THEN** controller B is assigned to slot 1
- **AND** controller A remains at slot 0

---

### Requirement: Gamepad Object Properties
Each `Gamepad` object SHALL expose the following read-only properties:
- `slot: int` - Controller slot index (0-7)
- `connected: bool` - Whether a controller is connected to this slot
- `name: str` - Human-readable controller name (empty string if not connected)

#### Scenario: Query controller name
- **GIVEN** an Xbox controller is connected to slot 0
- **WHEN** the application accesses `viewport.gamepads[0].name`
- **THEN** it returns a string like "Xbox Wireless Controller"

---

### Requirement: Button State Queries
Each `Gamepad` object SHALL provide methods to query button state:
- `is_button_down(button: GamepadButton) -> bool` - True if button is currently held
- `is_button_pressed(button: GamepadButton) -> bool` - True if button was pressed this frame
- `is_button_released(button: GamepadButton) -> bool` - True if button was released this frame

#### Scenario: Detect button press
- **GIVEN** controller 0 is connected and the A button is not pressed
- **WHEN** the user presses the A button
- **THEN** `is_button_pressed(GamepadButton.FACE_DOWN)` returns True for one frame
- **AND** `is_button_down(GamepadButton.FACE_DOWN)` returns True while held

#### Scenario: Detect button release
- **GIVEN** controller 0 is connected and the A button is held
- **WHEN** the user releases the A button
- **THEN** `is_button_released(GamepadButton.FACE_DOWN)` returns True for one frame
- **AND** `is_button_down(GamepadButton.FACE_DOWN)` returns False

---

### Requirement: Axis State Queries
Each `Gamepad` object SHALL provide a method to query analog axis values:
- `get_axis(axis: GamepadAxis) -> float`

Axis values SHALL be normalized:
- Stick axes: -1.0 (left/up) to +1.0 (right/down)
- Trigger axes: 0.0 (released) to +1.0 (fully pressed)

#### Scenario: Read stick position
- **GIVEN** controller 0 is connected
- **WHEN** the user pushes the left stick fully right
- **THEN** `get_axis(GamepadAxis.LEFT_X)` returns approximately 1.0

#### Scenario: Read trigger value
- **GIVEN** controller 0 is connected
- **WHEN** the user presses the left trigger halfway
- **THEN** `get_axis(GamepadAxis.LEFT_TRIGGER)` returns approximately 0.5

---

### Requirement: GamepadButton Enum
The system SHALL provide a `GamepadButton` enum with the following values:
- `FACE_DOWN` (A/Cross), `FACE_RIGHT` (B/Circle), `FACE_LEFT` (X/Square), `FACE_UP` (Y/Triangle)
- `BACK`, `GUIDE`, `START`
- `LEFT_STICK`, `RIGHT_STICK` (stick clicks)
- `LEFT_SHOULDER`, `RIGHT_SHOULDER` (bumpers)
- `DPAD_UP`, `DPAD_DOWN`, `DPAD_LEFT`, `DPAD_RIGHT`

#### Scenario: Use button enum
- **WHEN** the application checks `gamepad.is_button_down(dcg.GamepadButton.FACE_DOWN)`
- **THEN** it checks the state of the A button (Xbox) or Cross button (PlayStation)

---

### Requirement: GamepadAxis Enum
The system SHALL provide a `GamepadAxis` enum with the following values:
- `LEFT_X`, `LEFT_Y` (left stick)
- `RIGHT_X`, `RIGHT_Y` (right stick)
- `LEFT_TRIGGER`, `RIGHT_TRIGGER`

#### Scenario: Use axis enum
- **WHEN** the application calls `gamepad.get_axis(dcg.GamepadAxis.LEFT_X)`
- **THEN** it returns the horizontal position of the left analog stick

---

### Requirement: GamepadButtonHandler
The system SHALL provide a `GamepadButtonHandler` class for event-driven button input with parameters:
- `controller: int | None` - Controller slot (0-7) or None for any controller
- `button: GamepadButton` - Which button to monitor
- `callback: Callable` - Function called when button state changes

The callback SHALL receive the controller slot that triggered the event.

#### Scenario: Handle specific controller button
- **GIVEN** a `GamepadButtonHandler(controller=0, button=GamepadButton.FACE_DOWN, callback=on_jump)`
- **WHEN** controller 0 presses the A button
- **THEN** `on_jump` is called with controller slot 0
- **AND** pressing A on controller 1 does NOT trigger the callback

#### Scenario: Handle any controller button
- **GIVEN** a `GamepadButtonHandler(controller=None, button=GamepadButton.START, callback=on_start)`
- **WHEN** any connected controller presses START
- **THEN** `on_start` is called with the slot of the controller that pressed it

---

### Requirement: GamepadAxisHandler
The system SHALL provide a `GamepadAxisHandler` class for event-driven axis input with parameters:
- `controller: int | None` - Controller slot (0-7) or None for any controller
- `axis: GamepadAxis` - Which axis to monitor
- `deadzone: float` - Minimum absolute value to trigger callback (default 0.15)
- `callback: Callable` - Function called when axis value changes

The callback SHALL receive the controller slot and current axis value.

#### Scenario: Handle stick movement with deadzone
- **GIVEN** a `GamepadAxisHandler(controller=0, axis=GamepadAxis.LEFT_X, deadzone=0.15, callback=on_move)`
- **WHEN** controller 0's left stick moves from 0.0 to 0.5
- **THEN** `on_move` is called with (slot=0, value=0.5)
- **AND** small movements within deadzone (e.g., 0.0 to 0.1) do NOT trigger the callback

---

### Requirement: Controller Connect/Disconnect Handling
The system SHALL detect controller connect and disconnect events at runtime:
- When a controller connects, it SHALL be assigned to the lowest available slot
- When a controller disconnects, its slot SHALL show `connected=False`
- Slot assignments SHALL be stable (reconnecting same controller may get different slot)

#### Scenario: Controller connects during runtime
- **GIVEN** the application is running with no controllers connected
- **WHEN** a user connects a controller
- **THEN** `viewport.gamepads[0].connected` becomes True
- **AND** the controller is usable immediately

#### Scenario: Controller disconnects during runtime
- **GIVEN** controller is connected at slot 0
- **WHEN** the controller disconnects (battery dies, cable unplugged)
- **THEN** `viewport.gamepads[0].connected` becomes False
- **AND** button/axis queries for slot 0 return default values (False/0.0)

---

### Requirement: Compatibility with Existing Keyboard/Gamepad Handlers
The existing `KeyPressHandler` with `dcg.Key.GAMEPAD*` keys SHALL continue to function, using the first connected controller via ImGui's gamepad abstraction.

#### Scenario: Legacy gamepad handler still works
- **GIVEN** existing code using `KeyPressHandler(key=dcg.Key.GAMEPADFACEDOWN)`
- **WHEN** the first connected controller presses A
- **THEN** the handler fires as before
- **AND** the new `GamepadButtonHandler` API is available for per-controller handling
