# Design: Extend the Native Plot Context Menu

## Context

ImPlot opens and renders `##PlotContext` inside `EndPlot()`. At that point it
uses `PushOverrideID(plot.ID)`. Dear ImGui permits a subsequent begin of an
already-begun window to append content in the same frame. Integration tests
confirm this approach without changes to ImPlot source.

## Goals and Non-Goals

- Keep native and custom actions in one plot-canvas context menu.
- Prefer Cython and Python changes; avoid vendored C++ edits.
- Reuse DearCyGui menu widgets and callback dispatch.
- Do not extend the separately opened axis or legend context menus.
- Do not introduce DearCyFi-specific actions in DearCyGui.

## Candidate Rendering Approach

1. Immediately after a successful `BeginPlot()`, capture the submitted plot
   item ID before subsequent submissions change ImGui's last item.
2. Let ImPlot render its usual plot and menu in `EndPlot()`.
3. If custom children exist, use that captured ID with ImGui's
   `PushOverrideID`, call `BeginPopup("##PlotContext")`, draw the custom menu
   children after the native items, then balance `EndPopup` and `PopID`.
4. Declare the existing internal ImGui function in the Cython wrapper if
   needed; do not modify vendored sources. Restore DearCyGui viewport state and
   honor the existing item locking and callback queueing conventions.

The captured ID is the plot item ID for ordinary plots and subplot cells,
including shared-item subplots. `EndPlot()` resets the current ImPlot plot and
advances the subplot, so the appended drawing does not assume a current
ImPlot plot remains.

## Proposed Python API

Use existing parenting:

```python
with dcg.Plot(C) as plot:
    dcg.PlotLine(C, X=[0, 1], Y=[0, 1])
    with dcg.Menu(C, label="Application"):
        dcg.MenuItem(C, label="Action", callback=on_action)
```

Menu items can also be attached directly to the plot. The widget children
appear only in the plot-canvas popup, after a separator, and are not drawn in
the plot body. An empty plot menu adds no separator.

## Risks and Validation

- The popup name, ID scheme and `PushOverrideID` are internal implementation
  details. Keep the dependency localized and test it when vendors are updated.
- A second `BeginPopup` could interact unexpectedly with sizing, focus, nested
  menus, native item selection, closing, or popup stack state. Test these in a
  rendered viewport rather than assuming ordinary window append is sufficient.
- IDs, ID stacks and subplot advancement may differ by layout. Test ordinary
  plots, multiple plots, subplot cells, and shared-item subplots explicitly.
- ImGui may keep a popup open when settings change; preserve native behavior,
  rather than claiming `no_menus` forcibly closes an already-open popup.
- Child state, locking, callbacks, deletion, and GC need the same handling as
  existing widget containers. Do not retain borrowed plot pointers across
  frames or invoke Python callbacks synchronously during drawing.

## Milestones

The first prototype requires a local extension compilation: Python cannot
exercise the candidate path without Cython support. That focused experiment
precedes the final integration and full clean/release rebuild; it does not
eliminate the need for either. If it fails, record the failure and seek a new
decision instead of silently falling back to vendored C++ changes.

## Initial Spike Results

Before rebuilding, the baseline probe ran without the spike, and a
hidden-viewport capture showed the native X-Axis, Y-Axis, Legend, and Settings
entries.

The opt-in local spike captures the plot item ID and appends a fixed ImGui
menu item after `EndPlot()`. In hidden-viewport captures with injected mouse
events, the native menu and the spike item appeared in the same popup. The
spike item activated and closed the popup; reopening it showed one spike item.
The native Settings submenu opened and its Crosshairs option changed the plot
setting. The item was also visible on a second ordinary plot and in regular
and shared-legend subplot examples.
The user also ran the interactive demo and reported that the menu works after
resizing the window and switching focus to VS Code and back.

These observations supported the approach but did not validate the Python API.
The temporary spike has since been removed.

## Integration Results

The integrated extension was rebuilt and installed from these sources using
the existing cached native build dependencies. Hidden-viewport interaction
tests cover nested custom menus, callback dispatch, per-plot ownership and
state, ordinary and shared-legend subplots, alternate menu buttons, no-menus
behavior, child removal and deletion, and separator visibility. Framebuffer
comparisons verify that a checkmark appears and disappears when toggled.
A separate injected-input capture confirmed that a Python-owned item appears
with native entries and that the native Crosshairs action still works. The user
ran the integrated custom probe and confirmed it works after resizing and
changing focus; the output showed direct, nested, checked, and unchecked
callbacks for both plots. The user also confirmed the `no_menus` and alternate
button modes and verified native Crosshairs and Box Select.

A clean source snapshot of commit `ebc70ef` and its recorded native submodules
produced a Windows CPython 3.14 wheel. The wheel was installed into an isolated
directory and passed 24 targeted menu, ownership, and GC tests; the GC memory
test was deselected because `psutil` was unavailable. Other platform and
Python-version wheels are left to the GitHub Actions build.
