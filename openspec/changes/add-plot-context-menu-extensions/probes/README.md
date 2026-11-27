# Plot context-menu probes

These are proposal fixtures, not proof that the feature exists. Run from a
directory outside the repository root using the Python interpreter containing
the intended DearCyGui build. This avoids importing the source package instead
of the compiled installation. The manual probe prints the imported package
and compiled extension paths; verify they are from the intended build.

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

## Temporary Cython spike

When the local extension has been rebuilt with the temporary spike, enable it
for this process and run the baseline probe without `--custom`:

```powershell
$env:DCG_PLOT_MENU_SPIKE = '1'
& $python "$probe\plot_context_menu_probe.py"
Remove-Item Env:\DCG_PLOT_MENU_SPIKE
```

Right-click either plot canvas. `Cython spike action` should appear beneath the
native entries; selecting it writes a message to the terminal. The spike
inserts the same fixed item into every plot and does not provide Python menu
children or callbacks. The environment variable is an experiment switch, not
a supported public API.

After integrating the proposed plot-child API into the tested build, run:

```powershell
& $python "$probe\plot_context_menu_probe.py" --custom
& $python "$probe\plot_context_menu_probe.py" --custom --no-menus
& $python "$probe\plot_context_menu_probe.py" --custom --middle-button
& $python -m pytest --import-mode=importlib "$probe\test_plot_context_menu_ownership.py"
```

In custom mode, each plot should have only its own `Probe` submenu, alongside
the native entries. Check its direct and nested actions, callback counts,
native actions, closing and reopening. With `--no-menus`, neither set should
open from a fresh popup; with `--middle-button`, use middle-click. The
ownership tests do not test rendered popup behavior.

Before integration, `--custom` and the `test_extension_*` cases are expected to
fail because the current `Plot` does not accept widget children. A separate
minimal Cython spike may test appending a fixed native item before the proposed
Python API exists; do not treat that spike as a passed custom-mode test.
