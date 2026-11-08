# Prior Integration Findings

This is reference material for the upstream-first controller and color-bar
ports, not an active change proposal, completed port, or validation report for
this worktree. It summarizes useful findings from the abandoned approach of
bringing upstream commits into the disconnected feature branch.

## Sources and provenance

At review on 2026-11-08:

- The published
  [integration branch](https://github.com/khazaddim/DearCyGui/tree/integrate/game-controller-upstream-2026-11-03/openspec/changes/integrate-upstream-with-multi-controller)
  pointed to `5213cc71d80b890ee1115cd0b47974724c6e91cd`: the initial proposal,
  design, tasks, and integration delta spec.
- The local branch of the same name in `C:\Chris\DearCyGui` pointed to
  `471ba7d4d112b71c5d392c28e3f3850de6963737`. Its documents include later
  baseline and Stage A results not yet present on the published branch.
- The feature source, `Game_Controller_Build`, pointed to
  `9db7a6b5537fc194229fcc9f20e389959ee5ff30` both locally and remotely.
- This worktree was reviewed at
  `baa7d92b872088bbc9cbfa517ce987647d4fe732`. Its history contains the old
  integration's frozen upstream target,
  `3d13328f3434db2ed9498831ce6fd2c5018ce430`.

The historical observations below come from the local integration documents.
They were not reproduced during this reference review. Their original session
log files are cited in those documents, but were not retrieved here.

The Git objects can be inspected from this worktree without switching branches:

```powershell
git show 471ba7d4d112b71c5d392c28e3f3850de6963737:openspec/changes/integrate-upstream-with-multi-controller/tasks.md
git show 471ba7d4d112b71c5d392c28e3f3850de6963737:openspec/changes/integrate-upstream-with-multi-controller/design.md
git show 471ba7d4d112b71c5d392c28e3f3850de6963737:tests/test_fork_regressions.py
```

These later commits were local when reviewed. Do not assume their hashes or
findings are available on GitHub until that history is published.

## What remains useful

### Controller compatibility targets

The old baseline reported eight stable `Gamepad` objects in
`viewport.gamepads`, with slots 0-7, `GamepadButton.SOUTH`, and
`GamepadButtonHandler` / `GamepadAxisHandler`. Handler filtering used `-1`
for any controller and accepted `None` as that setting; the default axis
deadzone was approximately 0.15.

The design requires preserving existing callback argument order and data:

- Button: `(slot, GamepadButton)`
- Axis: `(slot, float)`

Those payloads and connected-device behavior were not verified by the baseline
configuration tests. Treat them as compatibility targets to confirm against
the feature source and test during the port, not as previously certified input.
In particular:

- Clear frame-edge state before processing the frame's SDL events.
- Observe press/release edges only in the event-processing frame; held input
  must not repeat an edge callback.
- Keep stable slot identity, slot filtering, hot-plug cleanup, stick/trigger
  normalization, deadzones, and legacy input behavior.
- Two manually rendered viewports must not erase each other's unconsumed input
  or duplicate callbacks.
- Adapt to upstream's typed callback machinery without accidentally replacing
  the controller tuple payloads. Keep runtime exports, docs, and stubs aligned.

### Color-bar compatibility targets

The baseline already exposed `PlotColorBars.value_space="data"|"normalized"`
and `normalized_max_fraction`, despite unchecked tasks in the older normalized
bar proposal. Proposal checkboxes alone are not a feature inventory.

Preserve horizontal and vertical bars, colors and borders, `baseline`,
`axis_min`, and `axis_max` anchors, `anchor_value`, axis attachments,
`ignore_fit`, and both value spaces. Edge anchoring must use current render-pass
axis limits rather than lagging by a frame during pan/zoom.

### Reusable tests and outstanding coverage

The local `tests/test_fork_regressions.py` contains 25 parameterized cases for
controller slot stability, disconnected state, handler defaults/filter
validation, and color-bar configuration/invalid values. It is a useful starting
point to adapt as the two features land, not an active test suite for upstream
before those APIs exist. Follow this worktree's fixture cleanup conventions.

The old tests did not verify connected input, callback types/counts, rendered
bar geometry, or live pan/zoom. Zero-controller discovery and three hidden plot
frames were smoke checks only. Physical controllers, same-instance virtual
input, Linux, free-threaded Python, and external consumers remained unverified.
Because SDL is statically linked, injecting devices into an unrelated SDL DLL
would not establish input behavior in the extension's SDL instance.

## Concrete build hazards to revisit

Two findings were checked against this worktree's [setup.py](../../setup.py):

1. **Windows controller support is disabled.** The Windows CMake arguments
   currently set `SDL_JOYSTICK=OFF` and `SDL_HAPTIC=OFF` alongside
   `SDL_PRESEED=OFF`. The controller port needs a buildable, controller-capable
   configuration and verification of effective CMake settings, not only API
   tests. The prior integration reported joystick/haptic enabled and preseed
   disabled after building SDL 3.4.4; it did not certify physical input.
2. **Native archive updates may not relink the extension.** SDL and FreeType
   archives are in `Extension.extra_objects`, but not `Extension.depends`.
   Prior local commit `c14bfc16f3652c0830bb91287670b5fe1b0905da` added
   `depends=[sdl3_lib, FT_lib]` after observing an SDL rebuild packaged with an
   old extension. Review that narrow correction when changing dependencies;
   a successful pip install alone does not prove a new SDL archive was linked.

The current worktree pins SDL
`c9a6709bd21750f1ad9597be21abace78c6378c9` and ImPlot
`78ca3a52915f74394b8f710ffde40a55efe760e6`. Do not copy later dependency pins
or packaging/workflow changes wholesale simply because the earlier integration
used them. Review necessary build changes as part of the feature ports.

Use the [local build skill](../../.github/skills/dearcygui-build/SKILL.md).
The old build used CPython 3.14.0 with the GIL enabled and Cython 3.2.4, despite
a documented Cython 3.1.6 pin. That successful historical environment is not
proof that this worktree's declared dependency environment has been tested.

## Historical baseline failures, not current waivers

The prior documents reported:

| Observation | Historical interpretation |
|-------------|---------------------------|
| Async graceful cancellation failed | Later upstream cancellation patch resolved it in the old integration. |
| Requested viewport width 550 measured 549 at 1.25 display scaling | Old adapted test used a one-pixel absolute tolerance, not upstream's very broad relative tolerance. |
| `test_viewport_singlethreaded_wake` delays accumulated too quickly | Remained a recorded failure at the Stage A automated checkpoint. |
| Windows subprocess termination returned 1 in `test_hanging_scenario_detection` | Test accepted only 0 or POSIX -15. |
| Nested executor ordering intermittently failed | Reported baseline scheduling sensitivity; isolated rerun passed. |
| Cross-thread viewport deallocation and shutdown callback warnings | Reported before upstream integration. |

These results belong to the old build and machine conditions. Rebuild and
baseline this worktree separately before porting. Reproduce any failures here
before classifying them as pre-existing; the old branch's approvals and deferred
gates do not transfer to this work.

## What not to carry forward

- Do not import the old proposal as an active OpenSpec change or replay its
  55-commit checklist: the selected upstream target is already in this history.
- Do not cherry-pick whole upstream adaptation commits into upstream-first code.
  Reuse only relevant fork-specific fixes after examining their diffs.
- Do not copy stale execution approvals, model suggestions, branch-promotion
  steps, version decisions, or completion checkboxes as current instructions.
- Retain upstream API changes, including typed callbacks and removed layout/
  child-window arguments. Adapt feature code and callers to them rather than
  restoring old core files.
- Keep hand-written backend C++ tracked; it is not Cython-generated output.
