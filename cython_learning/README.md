# Cython Learning Examples

This folder contains small Cython examples to help you understand the build process
and how Cython works with typed, compiled code.

## Ways to Use Cython

There are several approaches to using Cython in a Python project:

### 1. setup.py (Traditional)

This is what we use in this folder. It's the traditional approach, good for distributable packages:

```python
from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension("mymodule", sources=["mymodule.pyx"])
]

setup(
    name="mypackage",
    ext_modules=cythonize(extensions),
)
```

Build with: `python setup.py build_ext --inplace`

**Pros:** Tried and true, works everywhere, good for packages
**Cons:** Considered "legacy" by modern Python packaging standards

### 2. pyproject.toml (Modern Standard)

The current recommended approach for Python packaging:

```toml
[build-system]
requires = ["setuptools>=61.0", "cython>=3.0"]
build-backend = "setuptools.build_meta"

[project]
name = "mypackage"
version = "1.0.0"

[tool.setuptools]
ext-modules = [
    {name = "mymodule", sources = ["mymodule.pyx"]}
]
```

Build with: `pip install .` or `pip install -e .` (editable/development mode)

**Pros:** Modern, declarative, follows PEP 517/518 standards
**Cons:** Less flexible for complex builds

### 3. Jupyter `%%cython` Magic (Interactive/Learning)

Great for experimentation! Compile and run Cython code directly in notebook cells.

First, load the extension:
```python
%load_ext Cython
```

Then use the `%%cython` magic in any cell:
```python
%%cython
cdef int square(int x):
    return x * x

def py_square(x):
    return square(x)
```

The cell gets compiled on-the-fly and functions become available immediately!

**Additional options:**
```python
%%cython --annotate
# Shows HTML annotation inline (yellow = Python overhead)

%%cython -+
# Use C++ instead of C

%%cython --compile-args=-O3
# Pass compiler flags
```

**Pros:** Instant feedback, no rebuild cycle, great for learning
**Cons:** Not for production, can't create `.pxd` files, limited for complex projects

### 4. cythonize Command Line

Compile `.pyx` files directly without a setup script:

```bash
cythonize -i mymodule.pyx
```

The `-i` flag builds in-place. Useful for quick one-off compilations.

### Which Should You Use?

| Use Case | Recommended Approach |
|----------|---------------------|
| Learning/experimenting | Jupyter `%%cython` magic |
| Quick one-off script | `cythonize -i` command |
| Small project | `setup.py` (this folder's approach) |
| Distributable package | `pyproject.toml` |
| Complex build (like DearCyGui) | `setup.py` with custom logic |

---

## Files

- `timeseries.pyx` - Main Cython implementation (random walks, moving averages)
- `timeseries.pxd` - Cython declaration file (exposes C-level API)
- `analyzer.pyx` - Second module demonstrating `cimport` (uses timeseries)
- `setup.py` - Build script
- `demo.py` - Python script to test the compiled modules

## Build Steps

### 1. Navigate to this folder

```powershell
cd cython_learning
```

### 2. Build the extension (in-place)

```powershell
python setup.py build_ext --inplace
```

This does two things:
1. **Cython transpiles** `timeseries.pyx` → `timeseries.cpp` (or `.c`)
2. **MSVC compiles** `timeseries.cpp` → `timeseries.cp314-win_amd64.pyd`

### 3. Run the demo

```powershell
python demo.py
```

## What to Observe

After building, you'll see:
- `timeseries.cpp` - The generated C/C++ code (look at it to see what Cython produces!)
- `timeseries.cp314-win_amd64.pyd` - The compiled Python extension (importable binary)
- `timeseries.html` - Cython annotation view (yellow = Python interaction, white = pure C)
- `analyzer.cpp`, `analyzer.pyd`, `analyzer.html` - Same for the analyzer module
- `build/` folder - Intermediate build artifacts

**Open the `.html` files in a browser!** They show which lines are "hot" (yellow = Python overhead)
versus "cold" (white = pure C speed). Click on a line to see the generated C code.

## Key Cython Concepts Demonstrated

### 1. Typed Variables (`cdef`)

```cython
cdef int i           # C int, not Python int
cdef double value    # C double
cdef double* data    # C pointer
```

### 2. Cython Classes (`cdef class`)

```cython
cdef class TimeSeries:
    cdef double* _data    # C-level attribute (fast, private)
    cdef int _length
```

### 3. Typed Functions

```cython
# cpdef = callable from both Python AND C (best of both worlds)
cpdef double get_value(self, int index):
    return self._data[index]

# cdef = C only (fastest, not visible to Python)
cdef double _internal_calc(self):
    ...
```

### 4. The `.pxd` File

Like a C header file - declares what exists so other Cython modules can use it:

```cython
# In timeseries.pxd
cdef class TimeSeries:
    cdef double* _data
    cdef int _length
    cpdef double get_value(self, int index)
```

### 5. Memory Management

Cython doesn't have garbage collection for C types. We use `malloc`/`free`:

```cython
from libc.stdlib cimport malloc, free

cdef double* data = <double*>malloc(n * sizeof(double))
# ... use data ...
free(data)  # Must free manually!
```

### 6. cimport (Cross-Module Access)

The `cimport` keyword gives C-level access to another Cython module:

```cython
# In analyzer.pyx:
from timeseries cimport TimeSeries  # C-level access to class internals

cdef class TrendAnalyzer:
    cdef TimeSeries _source
    
    cpdef analyze(self):
        # Can directly access _source._data (C pointer!)
        # This is MUCH faster than going through Python
        for i in range(self._source._length):
            value = self._source._data[i]  # Direct C access
```

Compare to regular `import` which only gives Python-level access (slower).

## Exercises

1. **View the generated C code**: Open `timeseries.cpp` and search for your function names
2. **Add a new method**: Try adding `calculate_std_dev()` to the TimeSeries class
3. **Compare performance**: Time the Cython loops vs equivalent Python loops
4. **Try without types**: Remove the `cdef` type declarations and rebuild - notice the speed difference

## Troubleshooting

**"Unable to find vcvarsall.bat"**: You need Visual Studio Build Tools installed

**Import error after build**: Make sure you're in the `cython_learning` folder when running `demo.py`

**Changes not reflected**: Delete `timeseries.cpp` and the `.pyd` file, then rebuild
