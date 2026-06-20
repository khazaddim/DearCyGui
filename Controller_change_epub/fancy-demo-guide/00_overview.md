# Fancy Demo Guide

This short guide is meant to help plan the next phase of the controller demo work.
It covers two things:

1. How [Fancy_Demo.py](c:/Chris/DearCyGui/Fancy_Demo.py) is structured now.
2. How the new multi-controller API is intended to be used across future UI designs.

The current demo is intentionally narrow. It proves that button and axis updates can be driven by handlers instead of a polling loop. That is the right foundation for a richer visual demo later, including controller images, highlight regions, join prompts, and per-slot player presentation.

## What changed

The old small demo mixed two models:

- per-frame polling for held buttons, edge detection, axes, and connection state
- handler callbacks for a small M3 and M4 proof of concept

The new fancy demo flips that around:

- button state comes from `GamepadButtonHandler`
- axis state comes from `GamepadAxisHandler`
- connection state is still checked once per frame because there is no dedicated connection callback yet

That split matters for planning. The next visual version should keep handler-driven gameplay state, then layer presentation on top of it.

## Core takeaway

Treat the new API as two channels:

- event channel: button press/release and axis changes
- snapshot channel: connected slots and current controller names

That model is clean enough to support a controller-image UI without going back to full input polling.
