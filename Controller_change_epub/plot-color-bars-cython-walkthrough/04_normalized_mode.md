# Normalized Mode Walkthrough

## The New State

The normalized-mode change is small but instructive. It adds exactly two fields:

```cython
cdef int32_t _value_space
cdef double _normalized_max_fraction
```

The first acts like a compact enum:

- `0` means data mode
- `1` means normalized mode

The second is the user-configurable occupancy fraction.

Read the declaration at `dearcygui/plot.pxd:121` and `dearcygui/plot.pxd:122`.

## Why The Design Uses An Int Instead Of A String

The public API accepts strings because that is pleasant for Python users. The renderer stores an integer because:

- integer comparisons are cheaper
- draw-time code avoids Python string handling
- validation can reject unsupported values once at assignment time

That is a typical Cython design split in DearCyGui: Python ergonomics at the boundary, compact C state internally.

## The Property Setters

The new `value_space` property does the Python-to-C translation:

```cython
if value == "data":
    self._value_space = 0
elif value == "normalized":
    self._value_space = 1
else:
    raise ValueError(...)
self._validate_configuration()
```

And `normalized_max_fraction` stores the numeric value and revalidates it.

Exact source anchors:

- `value_space` getter: `dearcygui/plot.pyx:3213`
- `value_space` setter: `dearcygui/plot.pyx:3221`
- `normalized_max_fraction` getter: `dearcygui/plot.pyx:3233`
- `normalized_max_fraction` setter: `dearcygui/plot.pyx:3239`

A useful lesson here is that the setters do not perform the full rendering calculation. They only keep the object state coherent.

## The Draw-Time Conversion

The actual normalized behavior lives in two tiny branches inside `draw_element()`.

For horizontal bars:

```cython
length = _get_1d_plot_value(self._X, i)
if self._value_space == 1:
    value_span = limits.X.Max - limits.X.Min
    length = length * self._normalized_max_fraction * value_span
```

For vertical bars:

```cython
length = _get_1d_plot_value(self._Y, i)
if self._value_space == 1:
    value_span = limits.Y.Max - limits.Y.Min
    length = length * self._normalized_max_fraction * value_span
```

That is the whole feature.

The important architectural point is where the conversion happens:

- not in the setter
- not in Python callbacks
- not in a cached precomputed array
- directly inside the draw loop from live visible limits

This is why the bars respond correctly to zoom without needing outside coordination.

Read the real draw code at:

- draw loop start: `dearcygui/plot.pyx:3245`
- horizontal normalized branch: `dearcygui/plot.pyx:3289`
- vertical normalized branch: `dearcygui/plot.pyx:3301`

## Why Anchor Behavior Does Not Need To Change

Notice that only `length` changes. The existing `start_value` and `end_value` logic stays the same.

That is a good example of extending a renderer without disturbing unrelated semantics:

- anchor selection is one concern
- length interpretation is another concern

By keeping those concerns separate, the normalized change remained local and low-risk.

Compare the spec to the implementation:

- normalized design text: `openspec/changes/add-plot-color-bars-normalized-mode/design.md:1`
- validating fields in code: `dearcygui/plot.pyx:3069`
- normalized properties: `dearcygui/plot.pyx:3213`
- normalized draw conversion: `dearcygui/plot.pyx:3245`
