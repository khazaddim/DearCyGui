# Milestone 1 Changes Walkthrough

This document explains every change made for M1 (multi-controller polling support), file by file, bottom-up from C++ to Python. Each section shows what was added and **why**.

## The Big Picture

DearCyGui has a layered architecture:

```
Python app  ←  you write this
    ↓
Cython (.pyx/.pxd)  ←  bridge between Python and C++
    ↓
C++ backend (.h/.cpp)  ←  talks directly to SDL3 and OpenGL
    ↓
SDL3  ←  cross-platform library that talks to your OS and hardware
```

To add multi-controller support, we needed to add code at **every layer**:

1. C++ captures raw SDL events and stores state
2. Cython declares those C++ functions so Python can call them
3. Cython classes wrap it in a clean Python API
4. The demo script exercises the new API

The chapters that follow walk through each layer from bottom (C++) to top (Python).
