# Public API And Demo Layer

## `core.pyi` Matters More Than It Looks

After the Cython implementation is in place, DearCyGui exposes the public Python surface through `dearcygui/core.pyi`.

For `PlotColorBars`, that stub file now documents:

- constructor arguments
- `configure()` keyword support
- the `anchor` and `anchor_value` properties
- `colors` and `line_colors`
- `horizontal` and `weight`
- `value_space` and `normalized_max_fraction`

Exact stub anchors:

- class start: `dearcygui/core.pyi:33745`
- constructor: `dearcygui/core.pyi:33754`
- `configure()`: `dearcygui/core.pyi:33789`
- `value_space`: `dearcygui/core.pyi:33918`
- `normalized_max_fraction`: `dearcygui/core.pyi:33935`

This file does not execute at runtime, but it is still important because it keeps the user-facing contract explicit for editors, completions, and static tooling.

## Why `plot.pxd`, `plot.pyx`, And `core.pyi` Move Together

A useful DearCyGui habit is to think of the change in three layers:

1. `plot.pxd` says what compiled state and C methods exist.
2. `plot.pyx` implements the state transitions and draw logic.
3. `core.pyi` explains the supported Python API.

Follow those three layers directly:

- declaration layer: `dearcygui/plot.pxd:114`
- behavior layer: `dearcygui/plot.pyx:3045`
- stub layer: `dearcygui/core.pyi:33745`

When those drift apart, the feature becomes harder to maintain. The PlotColorBars changes are a good example of keeping them aligned.

## Demo Role

`PlotColorBars_Demo.py` is not just a showcase. It is part of the validation strategy.

The demo evolved to cover:

- vertical bottom-edge anchoring
- horizontal right-edge anchoring
- normalization toggles for both orientations
- control values that can be changed live while panning and zooming

Demo anchors:

- vertical plot setup: `PlotColorBars_Demo.py:125`
- vertical normalization update path: `PlotColorBars_Demo.py:169`
- horizontal plot setup: `PlotColorBars_Demo.py:186`
- horizontal update path: `PlotColorBars_Demo.py:217`

That matters in DearCyGui because some rendering bugs only show up during viewport interaction. A static constructor test is not enough to validate edge-anchored native drawing.

## Subtle Lesson From The Demo Bug

One of the practical issues encountered during this work was that `PlotColorBars` validates array sizes immediately. That means a count-changing UI update can temporarily put `X`, `Y`, and `colors` out of sync if those properties are assigned in the wrong order.

The demo fixes that by clearing or resizing fields in a safe sequence before restoring the final state.

Look at the resize-sensitive sequence in `PlotColorBars_Demo.py:234` and the immediate validation logic in `dearcygui/plot.pyx:3063`.

This is a helpful Cython lesson too: once a class validates eagerly, all multi-step mutations must respect transient invariants, not just final invariants.
