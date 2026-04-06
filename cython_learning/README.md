# Cython Learning Examples

This folder contains small Cython examples to help you understand the build process
and how Cython works with typed, compiled code.

## Prerequisites: You Need a C/C++ Compiler!

**Cython requires a C/C++ compiler** - it's not optional. Cython transpiles `.pyx` → `.c`/`.cpp`, 
then the compiler builds the binary extension. Without a compiler, you can't build anything.

### Windows

Install **Visual Studio Build Tools**:
1. Download from https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run installer, select "Desktop development with C++"
3. Make sure "MSVC v143" and "Windows SDK" are checked

Or install full Visual Studio (Community edition is free).

### Linux

```bash
# Ubuntu/Debian
sudo apt install build-essential python3-dev

# Fedora/RHEL
sudo dnf install gcc gcc-c++ python3-devel

# Arch
sudo pacman -S base-devel
```

### macOS

```bash
xcode-select --install
```

### Android (Pydroid3)

Pydroid3 *can* compile Cython, but you need the compiler plugin:

1. Install **"Pydroid repository plugin"** from Google Play Store
2. In Pydroid3: Menu → Pip → Install repository packages
3. Install `gcc` and `clang` from the repository

**Potential issues on Android:**
- This folder uses `language="c++"` - if that fails, edit `setup.py` and remove that line
- Compiling is slow and memory-intensive on mobile devices
- May need additional packages for C standard library headers

### Quick Test: Is Your Compiler Working?

Create a tiny test before trying the full examples:

```python
# test_compile.py
from setuptools import setup, Extension
from Cython.Build import cythonize

# Create a minimal .pyx file
with open("hello.pyx", "w") as f:
    f.write("def say_hello(): return 'Hello from Cython!'")

setup(ext_modules=cythonize("hello.pyx"))
```

Run: `python test_compile.py build_ext --inplace`

Then test it:
```python
>>> import hello
>>> hello.say_hello()
'Hello from Cython!'
```

If this works, the full learning examples should work too!

---

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

## Why Type Annotations Are CRITICAL for Performance

This is the **most important concept** in Cython. Without type declarations, Cython generates 
code that still does Python-style dynamic type checking - you get almost no speedup!

### The Problem: Untyped Code

```cython
# BAD: No types - this is basically Python speed
def slow_sum(data):
    total = 0
    for i in range(len(data)):
        total += data[i]
    return total
```

Cython has to:
1. Check if `data` supports `len()` 
2. Check if `data` supports `[]` indexing
3. Check if `total` and `data[i]` can be added
4. Handle potential exceptions at every step
5. Box/unbox Python objects for every operation

### The Solution: Typed Code

```cython
# GOOD: Fully typed - this is C speed
cdef double fast_sum(double* data, int length):
    cdef double total = 0.0
    cdef int i
    for i in range(length):
        total += data[i]
    return total
```

Cython generates pure C code:
- No type checking at runtime
- No Python object overhead
- Direct memory access
- Can be 10-100x faster!

### Where Types Matter Most

| Location | Impact | Example |
|----------|--------|---------|
| **Loop variables** | HUGE | `cdef int i` in `for i in range(n)` |
| **Accumulators** | HUGE | `cdef double total = 0.0` |
| **Function parameters** | HIGH | `def func(int x, double y)` |
| **Return types** | MEDIUM | `cpdef double calculate()` |
| **Class attributes** | HIGH | `cdef double* _data` |

### Try It Yourself: The Demo Proves This!

**In `timeseries.pyx`**, look at the bottom - there are three sum functions:

```python
sum_untyped(data)         # No types - slow!
sum_partially_typed(data) # Loop vars typed - better
sum_typed(data)           # Fully typed - FAST!
```

**Run `demo.py`** and section 4b shows the benchmark:
```
sum_untyped()        : 0.8234s  (no types - this IS Cython!)
sum_partially_typed(): 0.4521s  (loop vars typed)
sum_typed()          : 0.0089s  (fully typed memoryview)

Full typing speedup:    92x faster
```

**Open `timeseries.html`** in a browser and search for these functions:
- `sum_untyped` - mostly **yellow** (Python overhead)
- `sum_typed` - mostly **white** (pure C)

### How to See the Difference

The annotation HTML files (`timeseries.html`) show this visually:
- **Yellow lines** = Python interaction (slow)
- **White lines** = Pure C code (fast)

**Rule of thumb:** If a line in a hot loop is yellow, add type declarations until it's white!

### Common Patterns

```cython
# Loop variable - ALWAYS type these
cdef int i, j, n

# Accumulators
cdef double total = 0.0
cdef int count = 0

# Working with arrays
cdef double* data       # C pointer (fastest)
cdef double[:] memview  # Typed memoryview (safe + fast)

# Function with typed params and return
cpdef double mean(double[:] arr):
    cdef double total = 0.0
    cdef int i, n = arr.shape[0]
    for i in range(n):
        total += arr[i]
    return total / n
```

### What Happens Without Types (Generated C Code)

Untyped:
```c
// Generated C for: total += data[i]
__pyx_t_1 = __Pyx_GetItemInt(__pyx_v_data, __pyx_v_i, ...);  // ~50 lines
__pyx_t_2 = PyNumber_Add(__pyx_v_total, __pyx_t_1);          // ~30 lines  
// Plus error checking, reference counting, etc.
```

Typed:
```c
// Generated C for: total += data[i]
__pyx_v_total = __pyx_v_total + (__pyx_v_data[__pyx_v_i]);   // 1 line!
```

---

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
