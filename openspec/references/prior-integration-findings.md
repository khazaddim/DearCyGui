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

## Original implementation commit index

All commits below are reachable from the reviewed `Game_Controller_Build` tip
`9db7a6b5537fc194229fcc9f20e389959ee5ff30`. Links use full commit hashes so
they remain precise if the branch moves. They are patch references, not a
cherry-pick plan: adapt feature-specific hunks to the current upstream code.

### Multi-controller implementation

| Commit | Relevant implementation |
|--------|-------------------------|
| [976e6bb](https://github.com/khazaddim/DearCyGui/commit/976e6bbc7f86b6deab977eb4eb6d90c8b2ed62ec) | Removes the Windows SDL joystick/haptic disables, enabling controller support in the build. |
| [14642b4 (M1)](https://github.com/khazaddim/DearCyGui/commit/14642b4e0ff2fd7c3d33f238b8a01d2498794ff2) | Native controller slots, startup discovery and hot-plug tracking, polling bridge, enums, `Gamepad`, and `viewport.gamepads`. |
| [ae4d433 (M2)](https://github.com/khazaddim/DearCyGui/commit/ae4d433a48d0c10698a638276a771612d9b30a24) | Press/release edge latching, clearing on connection changes, and the begin-frame hook before SDL event processing. Also contains study/EPUB material, not just source changes. |
| [a738e29 (M3)](https://github.com/khazaddim/DearCyGui/commit/a738e2935bdf7a5c05b46cf0dc30fc09c9d35882) | `GamepadButtonHandler`, slot filtering, press/release dispatch, and `(slot, GamepadButton)` payloads using the enum helper. Also removes generated C++ files; do not treat those deletions as feature code. |
| [34fdc1e (M4)](https://github.com/khazaddim/DearCyGui/commit/34fdc1e215612b2c91daa4846fe8cd9149bb8f80) | `GamepadAxisHandler`, per-slot change tracking, deadzone/return-to-center behavior, and `(slot, float)` callbacks. |
| [8b82b57](https://github.com/khazaddim/DearCyGui/commit/8b82b57d2336ad31795d934a9b0ca304cd8031c0) | Gamepad documentation, public/generated stubs, custom stub inputs, and hardware-name documentation. Merge the relevant declarations rather than replacing upstream stubs. |

The source history shows no subsequent controller implementation edits in the
examined core, handler, enum-declaration, and SDL backend paths before the
reviewed feature tip. This is a provenance observation, not evidence that those
implementations are bug-free.

### Color-bar implementation

| Commit | Relevant implementation |
|--------|-------------------------|
| [9812864](https://github.com/khazaddim/DearCyGui/commit/9812864a54be9b24349fdd54a76a7d9d4d7b9cb0) | Initial native `PlotColorBars`, horizontal/vertical rendering, per-bar colors and borders, baseline/edge anchors, validation, declarations, and demo. |
| [4ac62eb](https://github.com/khazaddim/DearCyGui/commit/4ac62eb670712f81a69d3ef5e54f34263041c43c) | Demo-only follow-up adding live controls; useful for manual verification, not a native rendering fix. |
| [b6f4aa1](https://github.com/khazaddim/DearCyGui/commit/b6f4aa1c4b5554b05a1ba03caf5b5852c9b10492) | Normalized length mode, `normalized_max_fraction`, render-time visible-axis-span scaling, declarations, and demo updates. |

The normalized-mode commit is the only subsequent edit to the examined plot
implementation/declarations before the reviewed feature tip. Do not confuse
proposal archival with a separate implementation fix.

### Proposal and supporting references

- [7b95ddb](https://github.com/khazaddim/DearCyGui/commit/7b95ddb44f738c28986566da5031f91c54e1a267):
  original multi-controller proposal.
- [c784a82](https://github.com/khazaddim/DearCyGui/commit/c784a82b06f47afd242362ddf855663c36dfe624):
  controller milestone demo requirements.
- [5a9ee8b](https://github.com/khazaddim/DearCyGui/commit/5a9ee8babd6fcbf5127e6e240a9c9319e7c3511f):
  original color-bar proposal; also changes the Demos submodule.
- [ba69e7d](https://github.com/khazaddim/DearCyGui/commit/ba69e7d570ac757cdfc1d00f8f2139f09d1ddaa6):
  normalized-mode proposal, initial color-bar archival, and consolidated spec.
- [4b772a6](https://github.com/khazaddim/DearCyGui/commit/4b772a6945d763b66aa616e96f592c5d0a5cb392):
  original build skill, already adapted for this worktree.
- [d4ef4a7](https://github.com/khazaddim/DearCyGui/commit/d4ef4a7759c3e92128ea53be73bfa2a3a817156f):
  restores backend C++ lost during old history cleanup. Upstream already has
  these files; this restoration is not a feature patch to apply here.

### Packaging context, not automatic port requirements

- [cee2948](https://github.com/khazaddim/DearCyGui/commit/cee2948e5fd820b4615d9a651fd45d993c5e8515):
  fork-qualified version and Linux optional-dependency disables. Review only
  still-needed deltas; current upstream already includes those Linux disables.
- [28f6611](https://github.com/khazaddim/DearCyGui/commit/28f6611b9d3b9e888285eb00d3ffee5ccbf182bf):
  manual wheel-workflow trigger.
- [cd66372](https://github.com/khazaddim/DearCyGui/commit/cd6637278da45a0238cfc99865beaf8a3daa8507):
  removes macOS wheel jobs; this is a platform-scope decision, not a controller
  or color-bar implementation requirement.
- [1fbe9ec](https://github.com/khazaddim/DearCyGui/commit/1fbe9ec793acda63e49d0e9ed9818f26379c4521),
  [2fd99ae](https://github.com/khazaddim/DearCyGui/commit/2fd99aee9105214648c6920ce32fc039d257be0a),
  and [9db7a6b](https://github.com/khazaddim/DearCyGui/commit/9db7a6b5537fc194229fcc9f20e389959ee5ff30):
  later wheel/free-threading configuration attempts. Their presence is not
  proof that those CI targets passed.

Later abandoned-integration adaptations, including the static-library relink
correction discussed below, are separate evidence. They are not original
feature-branch commits and must not be conflated with this index.

## What remains useful

For the original controller, color-bar, and normalized-mode proposals, see
[Original Feature Proposals](../project.md#original-feature-proposals). That
index also links the archived initial color-bar change and consolidated spec;
both are needed to understand the base feature, not just its normalized mode.

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
