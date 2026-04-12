# timeseries.pyx
# A simple Cython module demonstrating typed code, classes, and manual loops

# Import C standard library functions
from libc.stdlib cimport malloc, free, rand, srand, RAND_MAX
from libc.time cimport time
from libc.math cimport sqrt

# ============================================================================
# CYTHON CLASS: TimeSeries
# ============================================================================
# 'cdef class' creates a C-extension type - much faster than pure Python classes

cdef class TimeSeries:
    """
    A time series container with C-level storage for fast operations.
    
    This demonstrates:
    - C-level attributes (cdef)
    - Memory management with malloc/free
    - Typed loops for performance
    """
    
    # C-level attributes (not visible to Python, but very fast)
    # these are the C-level attributes that should only be in the .pxd file (header)
    # not to be confused with .pyd, the compiled extension module that results from building the .pyx file
    # cdef double* _data      # Raw C array
    # cdef int _length        # Length of the series
    # cdef bint _owns_data    # Track if we allocated the memory
    
    def __cinit__(self, int length):
        """
        __cinit__ is called BEFORE __init__, guaranteed to run.
        Use it for C-level memory allocation.
        """
        self._length = length
        self._owns_data = True
        
        # Allocate C array (like malloc in C)
        self._data = <double*>malloc(length * sizeof(double))
        if self._data == NULL:
            raise MemoryError("Failed to allocate TimeSeries data")
        
        # Initialize to zero using a C loop (no Python overhead!)
        cdef int i
        for i in range(length):
            self._data[i] = 0.0
    
    def __dealloc__(self):
        """
        __dealloc__ is called when the object is garbage collected.
        MUST free any malloc'd memory here!
        """
        if self._owns_data and self._data != NULL:
            free(self._data)
            self._data = NULL
    
    # -------------------------------------------------------------------------
    # Properties (Python-accessible)
    # -------------------------------------------------------------------------
    
    @property
    def length(self):
        """Length of the time series."""
        return self._length
    
    # -------------------------------------------------------------------------
    # cpdef methods: callable from both Python AND C
    # -------------------------------------------------------------------------
    
    cpdef double get_value(self, int index):
        """Get value at index (with bounds checking)."""
        if index < 0 or index >= self._length:
            raise IndexError(f"Index {index} out of range [0, {self._length})")
        return self._data[index]
    
    cpdef void set_value(self, int index, double value):
        """Set value at index (with bounds checking)."""
        if index < 0 or index >= self._length:
            raise IndexError(f"Index {index} out of range [0, {self._length})")
        self._data[index] = value
    
    cpdef list to_list(self):
        """Convert to Python list (for easy inspection)."""
        cdef int i
        cdef list result = []
        for i in range(self._length):
            result.append(self._data[i])
        return result
    
    # -------------------------------------------------------------------------
    # cdef methods: C-only (fastest, but not callable from Python)
    # -------------------------------------------------------------------------
    
    cdef double _sum(self):
        """Internal sum calculation - pure C speed."""
        cdef double total = 0.0
        cdef int i
        for i in range(self._length):
            total += self._data[i]
        return total
    
    cdef double _sum_range(self, int start, int end):
        """Sum a range [start, end) - pure C speed."""
        cdef double total = 0.0
        cdef int i
        for i in range(start, end):
            total += self._data[i]
        return total
    
    # -------------------------------------------------------------------------
    # Public methods using the fast internal methods
    # -------------------------------------------------------------------------
    
    cpdef double mean(self):
        """Calculate the mean of the series."""
        if self._length == 0:
            return 0.0
        return self._sum() / self._length
    
    cpdef double variance(self):
        """Calculate variance using a single-pass algorithm."""
        if self._length <= 1:
            return 0.0
        
        cdef double mean_val = self.mean()
        cdef double sum_sq_diff = 0.0
        cdef double diff
        cdef int i
        
        for i in range(self._length):
            diff = self._data[i] - mean_val
            sum_sq_diff += diff * diff
        
        return sum_sq_diff / (self._length - 1)
    
    cpdef double std_dev(self):
        """Calculate standard deviation."""
        return sqrt(self.variance())


# ============================================================================
# RANDOM WALK GENERATOR
# ============================================================================

cpdef TimeSeries generate_random_walk(int length, double start_value=100.0, 
                                       double step_size=1.0, unsigned int seed=0):
    """
    Generate a random walk time series.
    
    Parameters:
        length: Number of points
        start_value: Initial value
        step_size: Maximum step size (+/- step_size)
        seed: Random seed (0 = use current time)
    
    This demonstrates:
    - Creating and returning Cython objects
    - Using C random number generation
    - Typed loop variables for speed
    """
    # Seed the random number generator
    if seed == 0:
        srand(<unsigned int>time(NULL))
    else:
        srand(seed)
    
    # Create the time series
    cdef TimeSeries ts = TimeSeries(length)
    
    # Generate the random walk
    cdef double current = start_value
    cdef double random_step
    cdef int i
    
    for i in range(length):
        ts._data[i] = current
        # Generate random step: -step_size to +step_size
        random_step = ((<double>rand() / RAND_MAX) * 2.0 - 1.0) * step_size
        current += random_step
    
    return ts


# ============================================================================
# MOVING AVERAGE CALCULATOR
# ============================================================================

cpdef TimeSeries simple_moving_average(TimeSeries source, int window_size):
    """
    Calculate Simple Moving Average (SMA).
    
    For the first (window_size - 1) points, uses available data.
    
    This demonstrates:
    - Taking Cython objects as parameters
    - Efficient windowed calculations
    - Direct C-array access for speed
    """
    if window_size < 1:
        raise ValueError("Window size must be at least 1")
    if window_size > source._length:
        raise ValueError("Window size cannot exceed series length")
    
    cdef TimeSeries result = TimeSeries(source._length)
    cdef double window_sum = 0.0
    cdef int i
    cdef int actual_window
    
    for i in range(source._length):
        # Add new value to window
        window_sum += source._data[i]
        
        if i < window_size:
            # Not enough data for full window yet
            actual_window = i + 1
            result._data[i] = window_sum / actual_window
        else:
            # Remove oldest value from window
            window_sum -= source._data[i - window_size]
            result._data[i] = window_sum / window_size
    
    return result


cpdef TimeSeries exponential_moving_average(TimeSeries source, int period):
    """
    Calculate Exponential Moving Average (EMA).
    
    EMA gives more weight to recent values.
    Formula: EMA_today = (Value_today * k) + (EMA_yesterday * (1-k))
    where k = 2 / (period + 1)
    
    This demonstrates:
    - A different smoothing algorithm
    - Stateful calculations in loops
    """
    if period < 1:
        raise ValueError("Period must be at least 1")
    
    cdef TimeSeries result = TimeSeries(source._length)
    cdef double multiplier = 2.0 / (period + 1)
    cdef double ema
    cdef int i
    
    # First value is just the source value
    if source._length > 0:
        ema = source._data[0]
        result._data[0] = ema
    
    # Calculate EMA for remaining values
    for i in range(1, source._length):
        ema = (source._data[i] * multiplier) + (ema * (1.0 - multiplier))
        result._data[i] = ema
    
    return result


# ============================================================================
# WEIGHTED MOVING AVERAGE
# ============================================================================

cpdef TimeSeries weighted_moving_average(TimeSeries source, int window_size):
    """
    Calculate Weighted Moving Average (WMA).
    
    Recent values get higher weights: weight[i] = i + 1
    For window_size=3: weights are [1, 2, 3], newest gets weight 3.
    
    This demonstrates:
    - More complex loop logic
    - Nested calculations
    """
    if window_size < 1:
        raise ValueError("Window size must be at least 1")
    
    cdef TimeSeries result = TimeSeries(source._length)
    cdef double weighted_sum
    cdef double weight_total
    cdef int i, j
    cdef int start_idx
    cdef int actual_window
    cdef double weight
    
    for i in range(source._length):
        weighted_sum = 0.0
        weight_total = 0.0
        
        # Determine window bounds
        if i < window_size:
            start_idx = 0
            actual_window = i + 1
        else:
            start_idx = i - window_size + 1
            actual_window = window_size
        
        # Calculate weighted sum
        for j in range(actual_window):
            weight = <double>(j + 1)  # Weights: 1, 2, 3, ...
            weighted_sum += source._data[start_idx + j] * weight
            weight_total += weight
        
        result._data[i] = weighted_sum / weight_total
    
    return result


# ============================================================================
# UTILITY: Compare two series
# ============================================================================

cpdef double mean_absolute_error(TimeSeries series1, TimeSeries series2):
    """
    Calculate Mean Absolute Error between two series.
    Useful for comparing smoothed series to original.
    """
    if series1._length != series2._length:
        raise ValueError("Series must have same length")
    
    cdef double total_error = 0.0
    cdef int i
    
    for i in range(series1._length):
        if series1._data[i] > series2._data[i]:
            total_error += series1._data[i] - series2._data[i]
        else:
            total_error += series2._data[i] - series1._data[i]
    
    return total_error / series1._length


# ============================================================================
# DEMONSTRATION: Typed vs Untyped Performance
# ============================================================================
# These two functions do THE SAME THING, but one is fully typed and one isn't.
# Run demo.py to see the massive performance difference!
#
# Look at timeseries.html after building:
# - sum_typed() will be mostly WHITE (pure C)
# - sum_untyped() will be mostly YELLOW (Python overhead)

def sum_untyped(data):
    """
    UNTYPED version - Cython compiles this, but it's still slow!
    
    No type declarations means Cython must:
    - Check types at runtime
    - Use Python object protocol for everything
    - Handle exceptions at every step
    
    This is basically Python speed, even though it's "Cython".
    """
    total = 0.0
    for i in range(len(data)):
        total = total + data[i]
    return total


cpdef double sum_typed(double[:] data):
    """
    TYPED version - This is FAST!
    
    Type declarations tell Cython:
    - data is a typed memoryview of doubles
    - total is a C double
    - i is a C int
    
    Cython generates pure C loop code - no Python overhead.
    Can be 50-100x faster than the untyped version!
    """
    cdef double total = 0.0
    cdef int i
    cdef int n = data.shape[0]
    
    for i in range(n):
        total = total + data[i]
    
    return total


def sum_partially_typed(data):
    """
    PARTIALLY TYPED - Better than nothing, but still yellow spots.
    
    The loop variable and accumulator are typed, but 'data' is not.
    This helps, but data[i] still requires Python indexing protocol.
    """
    cdef double total = 0.0
    cdef int i
    
    for i in range(len(data)):
        total = total + data[i]  # data[i] is still a Python operation!
    
    return total
