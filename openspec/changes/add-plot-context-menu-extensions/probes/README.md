# Plot context-menu probes

Run from a directory outside the repository root using the Python interpreter
containing the intended DearCyGui build. This avoids importing the source
package instead of the compiled installation. The manual probe prints the
imported package and compiled extension paths; verify they are from the
intended build.

The menus use ordinary plot parenting; for example:

```python
with dcg.Plot(C, label="Chart"):
    line = dcg.PlotLine(C, label="Series", X=[0, 1], Y=[0, 1])
    with dcg.Menu(C, label="Application"):
        dcg.MenuItem(
            C, label="Show Series", check=True, value=True,
            callback=lambda sender, target, visible: setattr(line, "show", visible),
        )
```

The checkmark is the menu item's value. If application code changes the
underlying setting elsewhere, update the menu item's value as well.

Example from PowerShell, adjusting the repository and Python paths as needed:

```powershell
Set-Location $env:TEMP
$python = 'C:\Chris\DearCyGui-upstream\.venv\Scripts\python.exe'
$probe = 'C:\Chris\DearCyGui-upstream\openspec\changes\add-plot-context-menu-extensions\probes'
& $python "$probe\plot_context_menu_probe.py" --smoke
& $python "$probe\plot_context_menu_probe.py"
& $python -m pytest --import-mode=importlib "$probe\test_plot_context_menu_ownership.py" -k baseline
```

The baseline interactive run has no custom items. Right-click each plot canvas
and check that the normal native options work. `--smoke` only renders hidden
frames; it does not inspect a popup or verify any interaction.

After rebuilding with plot-menu integration, run:

```powershell
& $python "$probe\plot_context_menu_probe.py" --custom
& $python "$probe\plot_context_menu_probe.py" --custom --no-menus
& $python "$probe\plot_context_menu_probe.py" --custom --middle-button
& $python -m pytest --import-mode=importlib "$probe\test_plot_context_menu_ownership.py"
& $python -m pytest --import-mode=importlib 'C:\Chris\DearCyGui-upstream\tests\test_plot_context_menu.py'
```

In custom mode, each plot should have only its own `Probe` submenu, alongside
the native entries. Check its direct and nested actions, callback counts,
checkmark toggling, native actions, closing and reopening. Each plot's checkmark
is independent. With `--no-menus`, neither set should open from a fresh popup;
with `--middle-button`, use middle-click. The ownership tests do not test
rendered popup behavior.
