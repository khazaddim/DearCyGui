---
name: dearcygui-build
description: "Use when building DearCyGui from source, rebuilding after editing .pyx/.pxd files, debugging Cython/MSVC/CMake/SDL3 build failures, or running tests against the freshly built extension. Covers the Windows virtual environment and native build workflow for this upstream integration worktree."
---

# DearCyGui Build Workflow

Adapted from the
[Game_Controller_Build skill](https://github.com/khazaddim/DearCyGui/blob/Game_Controller_Build/.github/skills/dearcygui-build/SKILL.md).
Use this workflow to rebuild after Cython changes and test the installed
extension, not the uncompiled source package or the old checkout's build.

## Environment (Windows / this worktree)

- **Repo root:** `C:\Chris\DearCyGui-upstream`
- **Worktree-local venv:** `C:\Chris\DearCyGui-upstream\.venv`
- **Venv Python:** `C:\Chris\DearCyGui-upstream\.venv\Scripts\python.exe`
- Do not assume the venv exists or that its Python version matches the old
  checkout. Inspect the selected interpreter before creating a venv.
- Do not reuse or reinstall into `C:\Chris\DearCyGui\.venv`; that environment
  belongs to the original feature checkout.
- Build dependencies come from [pyproject.toml](../../../pyproject.toml):
  `Cython==3.1.6`, `wheel`, `click`, `setuptools`, and `cmake`.
  The manifest notes that Cython 3.1.2 fails.
- Native toolchain: Visual Studio Build Tools with Desktop development with
  C++. MinGW support in [setup.py](../../../setup.py) is currently disabled.

If the local venv is missing, create it with the selected supported Python
interpreter using `-m venv C:\Chris\DearCyGui-upstream\.venv`.
For `--no-build-isolation`, ensure the manifest's build dependencies are
installed in that venv; restore missing dependencies before retrying a failed
build. Pytest must also be installed there to run tests.

Fresh agent terminals do not inherit an interactive terminal's venv activation.
Always invoke the worktree-local Python by absolute path.

## Canonical Build Command

Run from this worktree, not the original checkout:

```powershell
Set-Location 'C:\Chris\DearCyGui-upstream'
& 'C:\Chris\DearCyGui-upstream\.venv\Scripts\python.exe' -m pip install --no-build-isolation . --force-reinstall --no-cache-dir
```

- `--no-build-isolation` uses the venv's installed build dependencies.
- `--force-reinstall` installs the new wheel even if the version is unchanged.
- `--no-cache-dir` avoids reusing a stale cached wheel.
- `.` builds the current worktree.

The build configures and builds static SDL3 and FreeType libraries in
`build_SDL` and `build_FT`, transpiles Cython sources to C++, compiles the native
extension with setuptools/MSVC, and installs the wheel in the local venv.
CMake can reuse its build directories for incremental work, but `setup.py`
still invokes both configure and build on each run.

Allow several minutes for a full rebuild. Use a long-running command session
and retrieve its final result rather than launching overlapping builds.
When `.pxd` files change, rebuild the package rather than trying to compile
only one dependent `.pyx` file.

## Verify the Installed Extension

An absolute interpreter path alone does not prevent source-package shadowing:
Python can still put the current directory or a script's directory on
`sys.path`. Use isolated mode for the import smoke test:

```powershell
& 'C:\Chris\DearCyGui-upstream\.venv\Scripts\python.exe' -I -c "import dearcygui; import dearcygui.dearcygui; print(dearcygui.__file__)"
```

Verify the printed path is under this worktree's
`.venv\Lib\site-packages\dearcygui`, not the old checkout or the source tree.

Run the smallest relevant pytest selection with isolated Python and pytest's
importlib mode to avoid importing the source package:

```powershell
& 'C:\Chris\DearCyGui-upstream\.venv\Scripts\python.exe' -I -m pytest --import-mode=importlib 'C:\Chris\DearCyGui-upstream\tests\test_widgets.py'
```

Replace the example selector with tests covering the change. GUI tests may
require a working display and graphics context; report environmental failures
explicitly. For standalone scripts, run outside the source tree and ensure
the script directory does not shadow the installed package. The old
checkout's `Small_Input_Demo.py` is not part of this worktree.

## Generated Files

Cython emits `.cpp` beside `.pyx` sources. Do not commit generated files under
the top-level `dearcygui` package or `dearcygui\utils`. This worktree's
[.gitignore](../../../.gitignore) does not currently exclude them or all native
build directories, so inspect `git status` after building and leave those
artifacts unstaged. Likewise, do not commit the venv or generated package
metadata.

Keep the tracked, hand-written backend C++ sources:

- `dearcygui\backends\imgui_impl_opengl3.cpp`
- `dearcygui\backends\imgui_impl_sdl3.cpp`
- `dearcygui\backends\sdl3_gl3_backend.cpp`

Do not delete or revert pre-existing worktree changes during cleanup.

## Common Failures

- **Missing `dearcygui.dearcygui`:** check whether the import resolved to the
  uncompiled source package. Use the isolated import check above and confirm
  that the build and installation succeeded.
- **Missing Cython, CMake, or setuptools:** restore the dependencies declared
  in `pyproject.toml` into the local venv before retrying.
- **CMake/compiler failure:** verify MSVC Build Tools and CMake availability.
  If a Visual Studio `.bat` environment setup is needed, run it and the build
  in the same `cmd.exe` process; its environment does not persist across tool
  calls.
- **Stale extension:** rebuild and reinstall with the canonical command, then
  verify the imported package path.

Surface the first Cython/compiler error and the failing command; later errors
may be cascades. Do not report success until the build, installed-extension
import, and relevant tests have succeeded, or clearly state any blockers.
