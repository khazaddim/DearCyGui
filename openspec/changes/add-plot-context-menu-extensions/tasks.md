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

- [ ] 2.1 Enable plot-owned widget children and render them only in the native
  plot-canvas context popup; add a separator only when appropriate.
- [ ] 2.2 Preserve menu button, native popup behavior, existing plots with no
  children, child state propagation, locking, and queued callbacks.
- [ ] 2.3 Verify custom nested menus, per-plot isolation, removal, replacement,
  deletion, and GC. Complete and run the included ownership tests and
  extension-mode probe.
- [ ] 2.4 Update relevant public stubs, documentation, and examples.

## 3. Full Build and Acceptance

- [ ] 3.1 Perform a full rebuild from the integrated sources and confirm the
  probes load the rebuilt extension.
- [ ] 3.2 Run targeted existing tests plus the included ownership tests.
- [ ] 3.3 Run the extension-mode probe and verify callbacks fire exactly once,
  nested menus work, native actions remain usable, `no_menus` prevents opening
  a new popup, and an alternate `menu_button` opens it.
- [ ] 3.4 Repeat the subplot and multi-plot cases against the full build and
  record manual or automated interaction evidence.
- [ ] 3.5 Validate this OpenSpec change and update task status only as work is
  completed.
