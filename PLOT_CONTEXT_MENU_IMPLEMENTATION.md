# Plot context menu extensions

## Summary

DearCyGui plots can accept `Menu` and `MenuItem` children. These appear after
the existing ImPlot options in the **same plot-canvas context menu**. The
feature supports nested menus, checkable items, and callbacks associated with
individual plots.

The implementation uses Cython and existing Dear ImGui/ImPlot functionality;
it does not modify vendored C++ sources. The temporary, hardcoded spike action
and its `DCG_PLOT_MENU_SPIKE` environment variable are no longer used.

## Using the feature

Create menu widgets as children of a plot. For example, inside a DearCyGui
window:

```python
import dearcygui as dcg


def add_chart(context, label):
    with dcg.Plot(context, label=label) as plot:
        line = dcg.PlotLine(context, label="Series", X=[0, 1], Y=[0, 1])

        def set_series_visibility(sender, target, visible):
            line.show = visible
            print(f"{plot.label}: series visible = {visible}")

        with dcg.Menu(context, label="Application"):
            with dcg.Menu(context, label="Display"):
                dcg.MenuItem(
                    context,
                    label="Show series",
                    check=True,
                    value=True,
                    callback=set_series_visibility,
                )
    return plot


plot_a = add_chart(context, "Plot A")
plot_b = add_chart(context, "Plot B")
```

Each call creates its own plot, menu, and callback closure, so the callback can
operate on the correct plot or its data without interpreting internal ImGui
labels or IDs. `MenuItem(check=True)` stores its checkmark state in `value`;
the callback's third argument is the new boolean value. If application code
changes the underlying setting elsewhere, it should also update the menu
item's `value`.

Menu items can also be attached directly to a plot. These children extend the
plot-canvas menu, not the separate axis or legend context menus. The configured
`menu_button` controls opening, and `no_menus` prevents opening a new native
plot menu; it is not intended to forcibly close a popup that is already open.

## Implementation changes

### Plot parenting and rendering

In [`dearcygui/plot.pyx`](dearcygui/plot.pyx), `Plot.__cinit__` enables widget
children in addition to plot-element children. Plot elements continue to draw
in the plot as before; widget children are drawn in the context popup.

ImPlot normally opens and draws the plot popup inside `EndPlot()`, using the
plot ID as the ImGui ID seed and `##PlotContext` as the popup name. DearCyGui
appends to that same popup during the same frame:

1. Immediately after a successful `BeginPlot()`, capture the submitted plot
   item's ID with `ImGui::GetItemID()`, before other items replace it.
2. Draw the plot normally and call `EndPlot()` so ImPlot processes its native
   options.
3. If the plot has widget children, call `PushOverrideID` with the captured
   ID, then `BeginPopup("##PlotContext")`. If the popup is open, draw the
   children with the existing `draw_ui_children` helper, and balance
   `EndPopup` and `PopID`.

The separator is added only when at least one widget child is shown. Popup
position and parent sizing are set for child rendering and restored afterward.
When the popup is closed, hidden state is propagated to widget children without
hiding plot-element children. The existing child locking and callback queue
are reused. The code does not rely on an active ImPlot plot after `EndPlot()`,
which also matters for subplot cells.

[`dearcygui/wrapper/imgui.pxd`](dearcygui/wrapper/imgui.pxd) declares
`PushOverrideID` from `imgui_internal.h`; this declaration was added during
the spike and remains necessary for the integration. No change to ImPlot or
Dear ImGui C++ source is required.

### Public documentation and tests

- [`dearcygui/core.pyi`](dearcygui/core.pyi): documents plot-owned menus and
  permits widget children in the `Plot` constructor and `configure` stubs.
- [`dearcygui/widget.pyx`](dearcygui/widget.pyx): documents `Plot` as a menu
  parent.
- [`tests/test_plot_context_menu.py`](tests/test_plot_context_menu.py): tests
  ownership, per-plot callbacks and checkmarks, nested menus, subplots,
  configuration, removal, hidden state, and rendered menu behavior.
- [Probe instructions](openspec/changes/add-plot-context-menu-extensions/probes/README.md):
  explain how to run the interactive two-plot demo and ownership tests.

## Compatibility and validation

This approach depends on internal implementation details: ImPlot's popup name
and ID scheme, and ImGui's `PushOverrideID`. Vendor updates should recheck
those assumptions and rerun the rendered interaction tests.

The integrated extension was rebuilt and tested with the existing cached
native build dependencies. Automated interaction tests cover native-menu
integration, checkmark state, nested menus, multiple plots, subplot variants,
`no_menus`, and an alternate menu button. The interactive custom probe was
also tested after resizing and changing focus, and the user confirmed the
`no_menus` and alternate-button modes, as well as native Crosshairs and Box
Select. A clean Windows CPython 3.14 wheel built from commit `ebc70ef` passed
24 targeted tests when installed in an isolated directory; one `psutil`-based
GC memory test was deselected. Other platform and Python-version wheels are
left to GitHub Actions. See the
[task checklist](openspec/changes/add-plot-context-menu-extensions/tasks.md).

Because the implementation changes Cython code, users must rebuild and install
the extension before trying it. The probe prints the paths of the Python
package and compiled extension so the loaded build can be verified.

## Change size by file

The counts below compare the current working tree with commit `2351fdb`, before
the Cython spike. They include blank lines and documentation in source files;
a modified line counts as one addition and one deletion.

| Production source file | Added | Removed | Scope |
| --- | ---: | ---: | --- |
| [`dearcygui/plot.pyx`](dearcygui/plot.pyx) | 40 | 0 | Widget ownership, popup rendering, and documentation |
| [`dearcygui/wrapper/imgui.pxd`](dearcygui/wrapper/imgui.pxd) | 1 | 0 | `PushOverrideID` declaration, added during the spike |
| [`dearcygui/widget.pyx`](dearcygui/widget.pyx) | 2 | 2 | Menu documentation |
| [`dearcygui/core.pyi`](dearcygui/core.pyi) | 9 | 3 | Public documentation and child type annotations |
| **Production total** | **52** | **5** | |

Supporting Python changes:

| File | Added | Removed | Scope |
| --- | ---: | ---: | --- |
| [`tests/test_plot_context_menu.py`](tests/test_plot_context_menu.py) | 260 | 0 | New interaction and ownership tests |
| [`plot_context_menu_probe.py`](openspec/changes/add-plot-context-menu-extensions/probes/plot_context_menu_probe.py) | 9 | 2 | Checkable items in the existing interactive probe |

These are a snapshot of the current changes; documentation and OpenSpec files
are not included in the totals. There are no vendored C++ changes.
