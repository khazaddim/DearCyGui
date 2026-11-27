---
name: dearcygui-build
description: "Use when: building DearCyGui from source, rebuilding after editing .pyx/.pxd files, debugging build failures, running the demo/tests after a code change, or invoking Python against the freshly-built extension on this workspace. Covers the Cython + setuptools + CMake (SDL3) build pipeline and the Windows venv conventions used here."
---

# DearCyGui Build Workflow

Use this skill whenever you have edited any Cython source (`.pyx` or `.pxd`) under `dearcygui/` and need to recompile the extension, or when you need to run Python code that imports `dearcygui` after a change.

## When To Use

- "rebuild" / "build" / "recompile" after editing `.pyx` or `.pxd`
- Running the demo (`Small_Input_Demo.py`) or tests after code changes
- Diagnosing `ModuleNotFoundError: No module named 'dearcygui.dearcygui'`
- Diagnosing Cython compile errors, linker errors, or SDL3 build issues
- Any task that involves importing `dearcygui` from Python on this workspace

## Environment (Windows / this workspace)

- **Repo root:** `C:\Chris\DearCyGui`
- **Venv:** `C:\Chris\DearCyGui\.venv` (Python 3.14, cp314)
- **Venv Python (absolute):** `C:\Chris\DearCyGui\.venv\Scripts\python.exe`
- **PowerShell activation:** `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned; & .\.venv\Scripts\Activate.ps1`
- **Build deps** (declared in `pyproject.toml`, must be pre-installed in venv when using `--no-build-isolation`): `Cython==3.1.6`, `wheel`, `click`, `setuptools`, `cmake`. Note: Cython 3.1.2 is known to fail; 3.1.6 works.
- **Native toolchain:** MSVC (Visual Studio Build Tools, "Desktop development with C++"). MinGW path exists in `setup.py` but is disabled.

## Canonical Build Command

```powershell
C:\Chris\DearCyGui\.venv\Scripts\python.exe -m pip install --no-build-isolation . --force-reinstall --no-cache-dir
```

Why each flag:

- `--no-build-isolation`: build runs against the venv's already-installed Cython/setuptools/cmake (faster, reproducible). Requires those deps to be present in the venv.
- `--force-reinstall`: ensures the wheel is reinstalled even when version string didn't change.
- `--no-cache-dir`: avoids pip caching a stale wheel from a previous build.
- `.`: build from the current directory (the repo root).

The build does several phases:
1. **CMake** builds SDL3 (static) into `build_SDL/` and FreeType into `build_FT/`.
2. **Cython** transpiles every `.pyx` under `dearcygui/` → `.cpp`.
3. **setuptools / MSVC** compiles the `.cpp` files + hand-written backend C++ into the extension module.
4. **pip** installs the resulting wheel into the venv's `site-packages`.

The full rebuild takes several minutes on Windows. The SDL3 / FreeType CMake phases are cached and skip on re-runs unless their `build_*/` folders are deleted.

## Build Flags (optional)

Pass to `pip install` via `--config-settings` or directly to `setup.py`. From [setup.py](setup.py):

- `--msvc-compat` — when using MinGW, emit MSVC-compatible flags (`-fms-extensions`, etc.).
- `--gcc-clang-compat` — extra GCC/Clang interop flags.

Neither is needed on a stock MSVC setup.

## Running Python After A Build

**CRITICAL:** Do NOT run Python from the repo root with bare `python script.py`. The repo root contains a `dearcygui/` source folder, so `import dearcygui` resolves to the *source* (no compiled extension), producing:

```
ModuleNotFoundError: No module named 'dearcygui.dearcygui'
```

Two safe patterns:

1. **Use the venv Python by absolute path from any cwd:**
   ```powershell
   C:\Chris\DearCyGui\.venv\Scripts\python.exe path\to\script.py
   ```
   pip-install puts the compiled package in `.venv\Lib\site-packages\dearcygui\`, which the venv Python finds first when cwd is anywhere except the repo root.

2. **Run from the repo root only after sys.path massaging.** `Small_Input_Demo.py` does this: it removes the repo root from `sys.path` and prepends `.venv\Lib\site-packages` before `import dearcygui`.

Tool-launched fresh terminals do NOT inherit venv activation from the user's interactive session — always invoke the venv Python by absolute path in agent terminals, or re-run the activation incantation.

## Generated Files (gitignore policy)

Cython emits `.cpp` next to each `.pyx`. These are build artifacts and must not be committed:

- `dearcygui/*.cpp` — gitignored.
- `dearcygui/utils/*.cpp` — gitignored.
- `cython_learning/*.cpp` — gitignored.

Hand-written C++ that IS tracked:

- `dearcygui/backends/imgui_impl_opengl3.cpp`
- `dearcygui/backends/imgui_impl_sdl3.cpp`
- `dearcygui/backends/sdl3_gl3_backend.cpp`

If a regenerated `.cpp` appears as modified in `git status`, the rule of thumb is: it's a build artifact, leave it unstaged. If it's under `dearcygui/utils/` or top-level `dearcygui/` it should already be gitignored; if it shows up anyway, check the `.gitignore` patterns (recursive globs are NOT used — each subdirectory needs its own rule).

## Common Failure Modes

- **`ModuleNotFoundError: No module named 'dearcygui.dearcygui'`** — running from repo root with bare `python`. Fix: use venv Python absolute path from a different cwd.
- **`NameError` on a Cython `cpdef enum class` (e.g. `GamepadButton`)** — inside `.pyx` files, bare `EnumName(int_value)` is not callable at Python runtime without an explicit import. Use the helper `make_EnumName(int_value)` (defined alongside the enum in `dearcygui/types.pxd`) or cimport the enum.
- **Cython 3.1.2 build error** — pin Cython to 3.1.6 in the venv.
- **SDL3 CMake fails on first build** — make sure `cmake` is installed in the venv (`pip install cmake`) and a C++ compiler is available on PATH (MSVC Build Tools on Windows).
- **Stale extension after `.pxd` edit** — `.pxd` changes affect every `.pyx` that cimports from it, plus their transitive consumers. The canonical command rebuilds everything; do not try to partial-rebuild a single file.
- **Venv not activated in agent terminal** — symptom: `python` resolves to system Python and `import dearcygui` finds nothing or the wrong build. Fix: always use `C:\Chris\DearCyGui\.venv\Scripts\python.exe` by absolute path.

## Recommended Agent Workflow

When the user asks you to rebuild and test:

1. Edit the `.pyx` / `.pxd` files.
2. Run the canonical build command (sync mode, generous timeout — at least 10 min).
3. On success, run the demo or test with the venv Python by absolute path.
4. Do NOT stage regenerated `.cpp` files — they're either gitignored or by-convention untracked.

When the user reports a build failure, surface the **first** Cython/compiler error from the log (later errors are usually downstream cascades) and ask before attempting fixes that change source semantics.
