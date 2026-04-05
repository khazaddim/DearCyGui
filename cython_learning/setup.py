# setup.py
# Build script for Cython extension
#
# Usage:
#   python setup.py build_ext --inplace
#
# This will:
#   1. Run Cython to convert .pyx files -> .cpp files
#   2. Compile .cpp files -> .pyd files

from setuptools import setup, Extension
from Cython.Build import cythonize

# Define the extension modules
extensions = [
    Extension(
        name="timeseries",           # Module name (import timeseries)
        sources=["timeseries.pyx"],  # Cython source file
        language="c++",              # Use C++ compiler (optional, can use "c")
    ),
    Extension(
        name="analyzer",             # Second module that uses cimport
        sources=["analyzer.pyx"],
        language="c++",
    )
]

# Cythonize converts .pyx to .cpp and returns Extension objects
# annotate=True generates an HTML file showing Python/C interaction
cython_modules = cythonize(
    extensions,
    annotate=True,           # Generate .html files showing yellow highlights
    compiler_directives={
        'language_level': "3",   # Python 3 syntax
        'boundscheck': False,    # Disable bounds checking for speed (careful!)
        'wraparound': False,     # Disable negative indexing for speed
    }
)

setup(
    name="cython_learning",
    ext_modules=cython_modules,
)
