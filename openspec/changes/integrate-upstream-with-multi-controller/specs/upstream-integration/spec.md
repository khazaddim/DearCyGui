## ADDED Requirements

### Requirement: Frozen and Traceable Upstream Integration
The integration SHALL account for each of the 55 source commits after
`01d2ce70f00658f4119a86c34a915e53d3775b88` through
`3d13328f3434db2ed9498831ce6fd2c5018ce430`, using source patch content rather
than disconnected-history ahead/behind counts to determine applicability.

#### Scenario: An upstream change is processed
- **WHEN** a source commit is reviewed for integration
- **THEN** its checklist entry SHALL record a disposition, source SHA, resulting
  integration SHA or no-change justification, overlap resolution, and verification
- **AND** an already-present or superseded change SHALL require content evidence
  rather than being silently skipped

#### Scenario: Coupled or reverted commits are handled together
- **WHEN** individually applying commits would expose intentionally reverted or
  unbuildable intermediate behavior
- **THEN** the integration SHALL record an explicit atomic group and rationale
- **AND** every source commit SHALL retain an individual accounting entry

### Requirement: Isolated and Reversible Execution
Implementation SHALL start only after proposal approval and a recorded baseline,
on the integration branch rather than the original or backup branches.

#### Scenario: An integration gate fails
- **WHEN** a required verification fails
- **THEN** the integration SHALL stop advancement, record the failure and classify
  whether it is pre-existing or introduced
- **AND** the original and backup refs SHALL remain unchanged
- **AND** rollback SHALL protect uncommitted resolution work and avoid destructive
  resets or forced history replacement

### Requirement: Multi-Controller Behavior Preservation
The integrated system SHALL preserve the fork's eight-slot controller API,
polling semantics, slot-specific and any-controller handlers, hot-plug cleanup,
axis normalization, and deadzone behavior.

#### Scenario: Two controllers produce independent input
- **WHEN** two connected controllers issue distinguishable button and axis events
- **THEN** polling and callbacks SHALL identify the correct stable slots
- **AND** a slot-specific handler SHALL not dispatch another slot's events
- **AND** disconnected slots SHALL clear their input state

#### Scenario: Existing controller callbacks consume migrated internals
- **WHEN** upstream typed callback internals dispatch a custom gamepad callback
- **THEN** its existing sender/target/data argument ordering SHALL be preserved
- **AND** button data SHALL remain `(slot, GamepadButton)`
- **AND** axis data SHALL remain `(slot, float)`
- **AND** runtime declarations, stubs, and documentation SHALL agree

### Requirement: Frame-Latched Input and Presentation
The integrated system SHALL preserve controller frame-edge ordering in the
supported manual rendering loop while adopting upstream presentation fixes.

#### Scenario: A button is pressed, held, and released
- **WHEN** one press is processed, followed by held frames and one release
- **THEN** polling SHALL report each edge in its event-processing frame only
- **AND** each matching handler SHALL dispatch once for that edge and slot
- **AND** held frames SHALL not repeat the press callback

#### Scenario: Two viewports are rendered manually
- **WHEN** two contexts render in sequence and receive controller events
- **THEN** the secondary frame SHALL not erase unconsumed primary input or
  duplicate dispatch from a matching primary handler
- **AND** idle/wake and wait-for-input behavior SHALL have recorded event-count
  and presentation evidence rather than source-inspection-only approval

### Requirement: Custom Plot and Build Preservation
The integrated system SHALL preserve PlotColorBars behavior and the fork's
controller-capable packaging and workflow configuration.

#### Scenario: Custom plots are rendered after dependency upgrades
- **WHEN** data-unit and normalized bars are panned or zoomed
- **THEN** their colors, borders, axes, fit controls, and anchor behavior SHALL
  remain consistent with the recorded baseline and related bar specifications
- **AND** edge anchoring SHALL use the current rendering pass's axis limits

#### Scenario: A wheel is built from the integration
- **WHEN** an existing supported build target is validated
- **THEN** SDL joystick/gamepad support and custom Python exports SHALL remain
  available in the installed artifact
- **AND** the manual workflow trigger, free-threaded configuration, Linux
  workarounds, and existing platform scope SHALL not be silently overwritten

### Requirement: Deliberate Upstream API Migration
The integration SHALL adopt applicable upstream changes with explicit migration
notes and updated in-repository callers, while preserving protected custom APIs.

#### Scenario: A deprecated upstream argument is removed
- **WHEN** child-window labels, deprecated manual layout positioning, wrap_x, or
  no_saved_setting are removed
- **THEN** in-repository call sites and declarations SHALL be migrated and tested
- **AND** external caller requirements SHALL be documented without silently
  editing another repository

### Requirement: Evidence-Gated Completion
Each behavioral change SHALL receive its assigned focused checks; stage gates
SHALL pass before advancing, and final acceptance SHALL require cumulative
controller, rendering, plot, packaging, and regression evidence.

#### Scenario: A test needs unavailable hardware or another operating system
- **WHEN** the required test cannot run in the available environment
- **THEN** the checklist SHALL remain blocked or unchecked with the missing
  environment identified
- **AND** the integration SHALL not claim a mocked or source-only check proves
  actual hardware, display, free-threaded, or platform behavior

#### Scenario: A stage is declared verified
- **WHEN** a stage checkpoint is accepted
- **THEN** the record SHALL include exact tests or manual scenarios, observed
  outcomes, package/build provenance, and source/result mappings
- **AND** successful Git application alone SHALL not count as verification
