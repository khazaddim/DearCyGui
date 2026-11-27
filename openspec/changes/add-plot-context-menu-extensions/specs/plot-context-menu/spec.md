## ADDED Requirements

### Requirement: Custom actions in the native plot context menu

The system SHALL allow a plot to own menu widgets that are displayed in its
native plot-canvas context menu alongside the existing ImPlot entries.

#### Scenario: Plot context menu with custom children
- **GIVEN** a plot has a custom menu or menu item child
- **WHEN** the user opens the plot-canvas context menu
- **THEN** the existing native options and the plot's custom entries appear in the same popup
- **AND** custom entries follow the native options

#### Scenario: Plot without custom children
- **GIVEN** a plot has no custom menu children
- **WHEN** the user opens its plot-canvas context menu
- **THEN** its native menu is unchanged and no custom separator is added

### Requirement: Native menu interaction and plot isolation

The system SHALL preserve native plot context-menu controls and isolate custom
entries by plot, including plots inside subplots.

#### Scenario: Native menus disabled
- **GIVEN** `no_menus` is enabled before a menu is opened
- **WHEN** the user invokes the plot menu
- **THEN** neither native nor custom plot context-menu entries open

#### Scenario: Alternate menu button
- **GIVEN** a plot uses an alternate `menu_button`
- **WHEN** the user invokes the menu with that button
- **THEN** native and custom entries appear together in the popup

#### Scenario: Multiple plots
- **GIVEN** two plots have different custom entries
- **WHEN** the user opens each plot's context menu
- **THEN** each popup displays only its own custom entries

#### Scenario: Plot in a subplot
- **GIVEN** a plot in a subplot has custom entries
- **WHEN** the user opens that plot's context menu
- **THEN** its native and custom entries appear together without entries from another plot

### Requirement: Menu widget lifecycle and callbacks

The system SHALL use existing DearCyGui menu widget ownership and callback
semantics for custom plot menu entries.

#### Scenario: Nested custom action
- **GIVEN** a plot has a nested custom submenu containing a menu item
- **WHEN** the user selects the item once
- **THEN** its callback is queued through the normal DearCyGui callback mechanism and invoked once

#### Scenario: Child removed or plot deleted
- **WHEN** a custom menu child is detached or its plot is deleted
- **THEN** the removed child is not rendered in the plot popup
- **AND** the system retains no stale plot or child pointer for later frames
