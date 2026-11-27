# Tasks: Extend the Native Plot Context Menu

## 1. Baseline and Contained Experiment

- [x] 1.1 Run the included Python probe in baseline mode and record native
  plot-menu behavior without changing the existing extension.
- [x] 1.2 After proposal approval, make a minimal local Cython prototype that
  captures the plot ID and appends a visible test entry to the native popup.
  Keep the prototype isolated and do not edit vendored C++.
- [x] 1.3 Compile the local extension needed for the prototype. Confirm the
  Python probe imports that exact build rather than another installed copy.
- [x] 1.4 Manually verify native entries and the appended entry share one
  popup, native selection and closing still work, and reopening does not
  duplicate entries.
- [x] 1.5 Test two plots, a native nested menu, ordinary subplot cells, and
  shared-item subplots. Record results.
- [x] 1.6 Test popup behavior when the viewport is resized or focus changes.
  If the approach fails, stop and revisit the design before integration.

## 2. DearCyGui Integration

- [x] 2.1 Enable plot-owned widget children and render them only in the native
  plot-canvas context popup; add a separator only when appropriate.
- [x] 2.2 Preserve menu button, native popup behavior, existing plots with no
  children, child state propagation, locking, and queued callbacks.
- [x] 2.3 Verify custom submenus with at least two nesting levels open in the
  native popup, contain the correct entries, and invoke the selected item's
  callback once. Test per-plot isolation, removal, replacement, deletion, and
  GC. Complete and run the included ownership tests and extension-mode probe
  smoke test.
- [x] 2.4 Update relevant public stubs, documentation, and examples.
- [x] 2.5 Test checkable menu items: verify the checkmark toggles in both
  directions, the callback receives the new boolean state, and different
  plots maintain independent states.

## 3. Full Build and Acceptance

- [x] 3.1 Perform a full rebuild from the integrated sources and confirm the
  probes load the rebuilt extension.
- [x] 3.2 Run targeted existing tests plus the included ownership tests.
- [ ] 3.3 Manually run the extension-mode probe and verify callbacks fire
  exactly once, nested menus work, native actions remain usable, `no_menus`
  prevents opening a new popup, and an alternate `menu_button` opens it.
  The user confirmed direct, nested, and checkable actions on both plots,
  including after resizing and changing focus, and confirmed `no_menus` and
  the alternate button. A manual check of native actions remains.
- [x] 3.4 Repeat the subplot and multi-plot cases against the full build and
  record manual or automated interaction evidence.
- [x] 3.5 Validate this OpenSpec change and update task status only as work is
  completed.
- [ ] 3.6 Perform the clean/release rebuild before release.
