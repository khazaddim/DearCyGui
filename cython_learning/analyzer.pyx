# analyzer.pyx
# A second Cython module that demonstrates cimport
#
# This file shows how to use the .pxd declarations to get
# fast C-level access to another Cython module's internals.

# cimport gives us C-level access to TimeSeries internals
# This is MUCH faster than regular Python import
from timeseries cimport TimeSeries, generate_random_walk

# Regular import for comparison (Python-level only)
# import timeseries  # Would work but be slower for class access


cdef class TrendAnalyzer:
    """
    Analyzes trends in time series data.
    
    Demonstrates:
    - cimport to access another module's C internals
    - Direct pointer access to TimeSeries._data
    """
    
    cdef TimeSeries _source
    
    def __init__(self, TimeSeries source):
        self._source = source
    
    cpdef tuple calculate_trend(self):
        """
        Calculate linear regression trend (slope and intercept).
        Returns (slope, intercept).
        
        Uses C-level access to source._data for speed.
        """
        cdef int n = self._source._length
        if n < 2:
            return (0.0, 0.0)
        
        cdef double sum_x = 0.0
        cdef double sum_y = 0.0
        cdef double sum_xy = 0.0
        cdef double sum_xx = 0.0
        cdef double x, y
        cdef int i
        
        # Direct access to the C array (fast!)
        for i in range(n):
            x = <double>i
            y = self._source._data[i]  # Direct pointer access via cimport
            sum_x += x
            sum_y += y
            sum_xy += x * y
            sum_xx += x * x
        
        cdef double denom = n * sum_xx - sum_x * sum_x
        if denom == 0:
            return (0.0, sum_y / n)
        
        cdef double slope = (n * sum_xy - sum_x * sum_y) / denom
        cdef double intercept = (sum_y - slope * sum_x) / n
        
        return (slope, intercept)
    
    cpdef str trend_direction(self):
        """Returns 'up', 'down', or 'flat' based on slope."""
        slope, _ = self.calculate_trend()
        if slope > 0.01:
            return "up"
        elif slope < -0.01:
            return "down"
        else:
            return "flat"
    
    cpdef TimeSeries detrend(self):
        """
        Remove linear trend from the series.
        Returns a new TimeSeries with trend removed.
        """
        cdef double slope, intercept
        slope, intercept = self.calculate_trend()
        
        cdef int n = self._source._length
        cdef TimeSeries result = TimeSeries(n)
        cdef int i
        cdef double trend_value
        
        for i in range(n):
            trend_value = intercept + slope * i
            result._data[i] = self._source._data[i] - trend_value
        
        return result


cpdef double calculate_momentum(TimeSeries series, int lookback=10):
    """
    Calculate price momentum (rate of change).
    
    Momentum = (current_price - price_n_periods_ago) / price_n_periods_ago * 100
    
    Returns the momentum of the last value.
    """
    cdef int n = series._length
    if n <= lookback:
        return 0.0
    
    cdef double current = series._data[n - 1]
    cdef double past = series._data[n - 1 - lookback]
    
    if past == 0:
        return 0.0
    
    return (current - past) / past * 100.0


cpdef TimeSeries calculate_rolling_momentum(TimeSeries series, int lookback=10):
    """
    Calculate momentum for each point in the series.
    """
    cdef int n = series._length
    cdef TimeSeries result = TimeSeries(n)
    cdef int i
    cdef double current, past
    
    for i in range(n):
        if i < lookback:
            result._data[i] = 0.0
        else:
            current = series._data[i]
            past = series._data[i - lookback]
            if past == 0:
                result._data[i] = 0.0
            else:
                result._data[i] = (current - past) / past * 100.0
    
    return result
