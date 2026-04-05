# timeseries.pxd
# Declaration file - like a C header
#
# This file declares the C-level interface of timeseries.pyx.
# Other Cython modules can "cimport" this to access the fast C-level API.
#
# KEY DIFFERENCE:
#   import timeseries      -> Python-level access only (slower)
#   cimport timeseries     -> C-level access (faster, typed)

# Declare the TimeSeries class's C-level interface
cdef class TimeSeries:
    # C-level attributes
    cdef double* _data
    cdef int _length
    cdef bint _owns_data
    
    # cpdef methods (accessible from both C and Python)
    cpdef double get_value(self, int index)
    cpdef void set_value(self, int index, double value)
    cpdef list to_list(self)
    cpdef double mean(self)
    cpdef double variance(self)
    cpdef double std_dev(self)
    
    # cdef methods (C-only, for internal fast access)
    cdef double _sum(self)
    cdef double _sum_range(self, int start, int end)


# Declare module-level functions
cpdef TimeSeries generate_random_walk(int length, double start_value=*, 
                                       double step_size=*, unsigned int seed=*)

cpdef TimeSeries simple_moving_average(TimeSeries source, int window_size)

cpdef TimeSeries exponential_moving_average(TimeSeries source, int period)

cpdef TimeSeries weighted_moving_average(TimeSeries source, int window_size)

cpdef double mean_absolute_error(TimeSeries series1, TimeSeries series2)
