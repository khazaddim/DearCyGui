# demo.py
# Test script for the compiled Cython module
#
# Run this AFTER building:
#   python setup.py build_ext --inplace
#   python demo.py

import time

# Try to import the compiled module
try:
    import timeseries as ts
except ImportError as e:
    print("ERROR: Could not import timeseries module")
    print("Did you build it first?")
    print("  python setup.py build_ext --inplace")
    print(f"\nDetails: {e}")
    exit(1)

print("=" * 60)
print("Cython TimeSeries Demo")
print("=" * 60)

# ============================================================================
# 1. Basic TimeSeries usage
# ============================================================================
print("\n1. Basic TimeSeries Usage")
print("-" * 40)

series = ts.TimeSeries(10)
print(f"Created TimeSeries with length: {series.length}")

# Set some values
for i in range(10):
    series.set_value(i, float(i * 10))

print(f"Values: {series.to_list()}")
print(f"Mean: {series.mean():.2f}")
print(f"Std Dev: {series.std_dev():.2f}")

# ============================================================================
# 2. Random Walk Generation
# ============================================================================
print("\n2. Random Walk Generation")
print("-" * 40)

# Use a fixed seed for reproducibility
walk = ts.generate_random_walk(length=20, start_value=100.0, step_size=2.0, seed=42)

print(f"Random walk (20 points, starting at 100):")
values = walk.to_list()
print(f"  First 5: {[f'{v:.2f}' for v in values[:5]]}")
print(f"  Last 5:  {[f'{v:.2f}' for v in values[-5:]]}")
print(f"  Mean: {walk.mean():.2f}")
print(f"  Std Dev: {walk.std_dev():.2f}")

# ============================================================================
# 3. Moving Averages
# ============================================================================
print("\n3. Moving Averages")
print("-" * 40)

# Generate a longer series for demonstration
data = ts.generate_random_walk(length=100, start_value=100.0, step_size=3.0, seed=123)

# Calculate different moving averages
sma = ts.simple_moving_average(data, window_size=10)
ema = ts.exponential_moving_average(data, period=10)
wma = ts.weighted_moving_average(data, window_size=10)

print(f"Original series - Mean: {data.mean():.2f}, StdDev: {data.std_dev():.2f}")
print(f"SMA(10)         - Mean: {sma.mean():.2f}, StdDev: {sma.std_dev():.2f}")
print(f"EMA(10)         - Mean: {ema.mean():.2f}, StdDev: {ema.std_dev():.2f}")
print(f"WMA(10)         - Mean: {wma.mean():.2f}, StdDev: {wma.std_dev():.2f}")

# Compare smoothness
mae_sma = ts.mean_absolute_error(data, sma)
mae_ema = ts.mean_absolute_error(data, ema)
mae_wma = ts.mean_absolute_error(data, wma)
print(f"\nMean Absolute Error vs Original:")
print(f"  SMA: {mae_sma:.2f}")
print(f"  EMA: {mae_ema:.2f}")
print(f"  WMA: {mae_wma:.2f}")

# ============================================================================
# 4. Performance Test
# ============================================================================
print("\n4. Performance Comparison: Cython vs Pure Python")
print("-" * 40)

def python_random_walk(length, start=100.0, step=1.0):
    """Pure Python random walk for comparison."""
    import random
    result = [0.0] * length
    current = start
    for i in range(length):
        result[i] = current
        current += random.uniform(-step, step)
    return result

def python_sma(data, window):
    """Pure Python SMA for comparison."""
    result = [0.0] * len(data)
    for i in range(len(data)):
        if i < window:
            result[i] = sum(data[:i+1]) / (i+1)
        else:
            result[i] = sum(data[i-window+1:i+1]) / window
    return result

# Benchmark parameters
n_points = 100000
n_iterations = 5

print(f"Generating {n_points:,} point random walks, {n_iterations} iterations...")

# Time Cython version
start = time.perf_counter()
for _ in range(n_iterations):
    cy_walk = ts.generate_random_walk(n_points, seed=42)
cy_time = time.perf_counter() - start

# Time Python version
start = time.perf_counter()
for _ in range(n_iterations):
    py_walk = python_random_walk(n_points)
py_time = time.perf_counter() - start

print(f"\nRandom Walk Generation:")
print(f"  Cython: {cy_time:.4f}s")
print(f"  Python: {py_time:.4f}s")
print(f"  Speedup: {py_time/cy_time:.1f}x faster")

# Benchmark SMA
print(f"\nCalculating SMA({10}) on {n_points:,} points, {n_iterations} iterations...")

# Time Cython SMA
start = time.perf_counter()
for _ in range(n_iterations):
    cy_sma = ts.simple_moving_average(cy_walk, 10)
cy_sma_time = time.perf_counter() - start

# Time Python SMA
start = time.perf_counter()
for _ in range(n_iterations):
    py_sma = python_sma(py_walk, 10)
py_sma_time = time.perf_counter() - start

print(f"\nSimple Moving Average:")
print(f"  Cython: {cy_sma_time:.4f}s")
print(f"  Python: {py_sma_time:.4f}s")
print(f"  Speedup: {py_sma_time/cy_sma_time:.1f}x faster")

# ============================================================================
# 5. Show some actual data
# ============================================================================
print("\n5. Sample Data Output")
print("-" * 40)

# Create a small series to display
small = ts.generate_random_walk(15, start_value=50.0, step_size=5.0, seed=999)
small_sma = ts.simple_moving_average(small, 3)
small_ema = ts.exponential_moving_average(small, 3)

print(f"{'Index':<6} {'Original':<12} {'SMA(3)':<12} {'EMA(3)':<12}")
print("-" * 42)
orig_vals = small.to_list()
sma_vals = small_sma.to_list()
ema_vals = small_ema.to_list()

for i in range(15):
    print(f"{i:<6} {orig_vals[i]:<12.2f} {sma_vals[i]:<12.2f} {ema_vals[i]:<12.2f}")

print("\n" + "=" * 60)
print("Demo complete! Now try:")
print("  - Look at timeseries.html for Cython's annotation view")
print("  - Look at timeseries.cpp to see the generated C code")
print("  - Modify timeseries.pyx and rebuild to experiment")
print("=" * 60)

# ============================================================================
# 6. Bonus: Using the analyzer module (demonstrates cimport)
# ============================================================================
print("\n\n6. BONUS: Analyzer Module (demonstrates cimport)")
print("-" * 40)

try:
    import analyzer
    
    # Create a series with an upward trend
    trend_data = ts.generate_random_walk(50, start_value=100.0, step_size=1.0, seed=555)
    # Add a trend by modifying values
    for i in range(50):
        trend_data.set_value(i, trend_data.get_value(i) + i * 0.5)  # Add upward drift
    
    # Analyze the trend
    ta = analyzer.TrendAnalyzer(trend_data)
    slope, intercept = ta.calculate_trend()
    print(f"Trend Analysis:")
    print(f"  Slope: {slope:.4f}")
    print(f"  Intercept: {intercept:.2f}")
    print(f"  Direction: {ta.trend_direction()}")
    
    # Calculate momentum
    momentum = analyzer.calculate_momentum(trend_data, lookback=10)
    print(f"  Momentum (10-period): {momentum:.2f}%")
    
    # Detrend the data
    detrended = ta.detrend()
    print(f"\n  Original Mean: {trend_data.mean():.2f}")
    print(f"  Detrended Mean: {detrended.mean():.2f} (should be ~0)")
    
except ImportError as e:
    print(f"Analyzer module not available: {e}")
    print("(This is expected if you only built timeseries.pyx)")

