# Project Context

## Purpose

DearCyGui is a Python GUI library that combines Dear ImGui with Cython bindings
to provide performant graphical interfaces, widgets, and data visualization.

## Tech Stack

- Python package with Cython `.pyx` and `.pxd` sources
- C++ native code and vendored dependencies, including Dear ImGui, ImPlot, and
  SDL
- Setuptools and CMake-based build configuration
- Pytest tests

## Project Conventions

### Architecture

- Public Python APIs are implemented primarily in `dearcygui/`.
- Native and third-party integrations live in `dearcygui/backends/` and
  `thirdparty/`.
- User-facing documentation is in `dearcygui/docs/`.

### Testing

- Tests are in `tests/` and use pytest.
- Changes to Cython or native code may require building the extension before
  runtime tests can be run.

## Important Constraints

- Preserve the existing Python API unless a proposal explicitly covers an API
  change.
- Treat vendored third-party code as external; avoid unrelated edits there.
