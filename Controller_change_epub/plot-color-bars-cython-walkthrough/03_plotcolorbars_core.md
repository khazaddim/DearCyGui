# Core PlotColorBars Implementation

## Construction And Stored State

The constructor initializes the series to a valid default configuration:

```cython
def __cinit__(self):
    self._colors = DCGVector[int32_t]()
    self._line_colors = DCGVector[int32_t]()
    self._weight = 1.
    self._horizontal = False
    self._anchor_mode = 0
    self._anchor_value = 0.
    self._value_space = 0
    self._normalized_max_fraction = 1.
```

Exact source anchor: `dearcygui/plot.pyx:3053`

There are two good Cython lessons here.

First, these are low-level fields, so they are cheap to read during drawing.
Second, the defaults already represent a complete configuration:

- no per-bar colors yet
- vertical mode by default
- baseline anchoring by default
- ordinary data-unit lengths by default

## Validation Strategy

`_validate_configuration()` is the guardrail for the whole feature. It checks:

- `len(X) == len(Y)` once both arrays are populated
- positive `weight`
- valid anchor enum range
- valid `value_space` enum range
- `normalized_max_fraction > 0 and <= 1`
- color vector sizes are either `0`, `1`, or `count`

Read the function at `dearcygui/plot.pyx:3063`.

The color-vector backing fields are declared at `dearcygui/plot.pxd:115` and `dearcygui/plot.pxd:116`.

This function is called from the setters rather than from every draw step. That is the right trade-off for DearCyGui:

- configuration mistakes fail fast at mutation time
- draw-time code assumes state is already coherent

## Property Surface

The Python-visible API is built from ordinary `@property` definitions in the Cython class. For example, the `anchor` setter converts Python strings into a compact integer mode:

```cython
if value == "baseline":
    self._anchor_mode = 0
elif value == "axis_min":
    self._anchor_mode = 1
elif value == "axis_max":
    self._anchor_mode = 2
else:
    raise ValueError(...)
```

This is a classic Cython pattern:

- expose a friendly Python API
- convert it immediately into a cheaper C representation
- keep the renderer working with integers and doubles rather than Python strings

Useful property anchors:

- `X` property begins near `dearcygui/plot.pyx:3081`
- `Y` property begins near `dearcygui/plot.pyx:3093`
- `colors` property begins near `dearcygui/plot.pyx:3105`
- `line_colors` property begins near `dearcygui/plot.pyx:3136`
- `horizontal` property begins near `dearcygui/plot.pyx:3155`
- `weight` property begins near `dearcygui/plot.pyx:3165`
- `anchor` property begins near `dearcygui/plot.pyx:3177`
- `anchor_value` property begins near `dearcygui/plot.pyx:3209`

## Draw Loop Structure

The draw loop is where the first change really pays off. The high-level flow is:

1. verify arrays are available
2. enter the ImPlot item with `BeginItem`
3. fetch live axis limits with `GetPlotLimits`
4. get the plot draw list
5. iterate bars and compute each rectangle
6. convert plot coordinates to pixels
7. emit `AddRectFilled` and optional `AddRect`

The most important design decision is that anchor resolution happens inside the loop from live limits:

```cython
start_value = resolve_anchor_value(limits,
                                   self._horizontal,
                                   self._anchor_mode,
                                   self._anchor_value)
```

That is exactly why axis-edge anchoring stays visually locked during pan and zoom. The value is not cached from earlier Python callbacks. It is pulled from ImPlot at render time.

Read the anchor helper at `dearcygui/plot.pyx:110`, then watch it being used inside the draw loop at `dearcygui/plot.pyx:3284`.

## Horizontal And Vertical Branches

The series supports both orientations by swapping semantic meaning:

- vertical mode: `X` is center, `Y` is length
- horizontal mode: `Y` is center, `X` is length

That is implemented as one branch in the draw loop, not two separate classes. This keeps the public API small while reusing the same rectangle-building logic.

Orientation branches to inspect:

- horizontal path starts around `dearcygui/plot.pyx:3288`
- vertical path starts around `dearcygui/plot.pyx:3298`
- pixel conversion happens through `PlotToPixels` in those same two branches
