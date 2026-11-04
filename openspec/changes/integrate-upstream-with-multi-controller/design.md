## Context

At proposal creation the integration branch and the November backup point to
`9db7a6b5537fc194229fcc9f20e389959ee5ff30`. Neither has a Git merge base with
current upstream. This does not mean all upstream development is absent:
465 upstream commits had exact stable patch-ID matches in the fork's history.
Patch-ID mismatches alone do not prove a missing change.

The rewritten local January baseline `f0948a0` matches upstream `01d2ce7` except
for three hand-written backend C++ files removed during history cleanup and
subsequently restored on the fork. Those files must not be discarded as
generated output. The fork's layout, sizing, and SVG utility files are unchanged
from the older baseline and lack later upstream fixes. The selected range
contains 31 prerequisite commits and the 24 October commits, not 577 independent
missing features.

Freeze the full hashes in the proposal rather than silently expanding scope if
upstream moves. Reconfirm this reconstruction in the baseline stage, especially
the restored backend content.

## Goals / Non-Goals

- Integrate the frozen range without losing working custom behavior.
- Keep each source commit traceable and pause at failed verification gates.
- Preserve controller consumer compatibility while accepting listed upstream
  API removals and documenting their migrations.
- Do not rewrite published history, merge unrelated histories automatically,
  replace whole custom files with upstream copies, redesign the controller API,
  repair unrelated defects, or change external applications without approval.

## Decisions

### Ordered integration and provenance

Use the oldest-first checklist in tasks.md. Read each full source patch and
identify prerequisites before editing. A clean cherry-pick is not proof of
correctness. Do not automatically choose all "ours" or all "theirs" for conflicts.

For each numbered source commit append a result directly beneath its checklist
entry, using this format:

`Disposition: pending | cherry-picked | adapted | already-present | superseded | deferred`

`Result: <integration SHA(s) or unchanged tree; source SHA; reason; changed surfaces>`

`Verification: <gate IDs; exact command/scenario; environment; outcome; evidence>`

All entries initially have disposition `pending`; an unchecked entry has no
claimed implementation or verification. Check an entry only after its result and
required gate evidence are recorded. Blocked/manual tests remain unchecked.
Record baseline failures separately from integration regressions.

Use source SHAs in adapted commit messages; use `cherry-pick -x` where appropriate.
A revert pair such as `a7ebaa8`/`914dd01` may be treated as an atomic unit to avoid
validating intentionally reverted transient behavior, but account for both source
commits. Stubs and build registration may need to travel with their producing
changes. Document any such group before applying it, retaining all checklist
entries and never leaving a supposedly verified checkpoint unbuildable.

Preserve `0.1.8+multicontroller.1` unless a separately recorded version decision
requires a different fork-qualified version. `bc00743` also changes the ImPlot
submodule: do not classify it as a version-only no-op.

### Protected fork behavior

- Eight stable controller slot objects; actual API names such as
  `GamepadButton.SOUTH`, not obsolete names from the original pending proposal.
- Polling, per-slot and any-controller handlers, deadzones, normalized stick and
  trigger values, hot-plug state cleanup, and controller identity.
- Existing callback argument order and data tuples: button `(slot, GamepadButton)`
  and axis `(slot, float)`. Upstream typed callback migration must not silently
  change these payloads. Runtime behavior, documentation, and stubs must agree.
- Clear controller edge state before processing a frame's SDL events, then run
  handlers against that frame. Preserve the supported manual game loop.
- Multiple viewports must not cause another viewport's frame start to erase
  unconsumed edges or duplicate callbacks. Record existing behavior first;
  investigate failures rather than declaring this passed by source inspection.
- Retain legacy keyboard/gamepad behavior, background-input policy, and
  initialized/uninitialized viewport cleanup unless an intentional migration is
  separately approved.
- Preserve PlotColorBars colors, borders, axis attachments, live edge anchors,
  normalized/data length modes, and same-frame behavior while panning/zooming.
- Keep joystick/gamepad support enabled in SDL, Linux dependency workarounds,
  free-threaded wheel settings, `workflow_dispatch`, and current platform scope.
  The manual trigger is already present via fork commit `28f6611`; importing
  `aebfcb4` is not necessary to preserve it.

### Verification gates

Use existing pytest files and demos first; add focused regression coverage where
no suitable test exists. Build all affected Cython sources with the documented
workspace build procedure after native/Cython/declaration changes. Run installed
package checks outside the repository source directory and record
`dearcygui.__file__`, Python version, and build revision so stale extensions
cannot masquerade as verification.

| Gate | Required observations |
|------|-----------------------|
| B | Record branch/backup/target hashes, clean status, submodule pins, import provenance, current build and focused baseline results. Inventory actual APIs against pending specs before asserting compatibility. |
| A | Run focused `test_asyncio.py` and cancellation/shutdown cases, including cross-thread cancellation and executor dispatch. Reverted loop-detection behavior is assessed at its final net state. |
| S | Rebuild with the selected SDL/ImPlot pins. Verify effective CMake joystick/gamepad settings, controller discovery, connection/disconnection, and plot startup. Do not run gamepad-disabled builds as controller validation. |
| C | Automated API/handler checks plus deterministic SDL virtual-controller input where feasible; otherwise real-device results explicitly remain manual. Verify 0/1/2 devices, slot filtering, two simultaneous sources, press/hold/release, deadzone entry/exit, trigger/stick ranges, unplug/reconnect, and legacy input. Validate eight-slot capacity using virtual devices when available; mark physical eight-device checks unavailable if necessary. |
| V | Run relevant `test_viewport.py`, sizing, and controller cases. Check idle/wake, pending refresh, timer rendering, continuous manual input with wait-for-input on/off, and two manually rendered contexts. For each injected press/release, observe its edge in the event-processing frame, no edge next frame, no repeated held-button edge, and one callback per matching handler/slot. Measure presented frames for a single wake before/after `866ecf4`, separate settling frames from duplicate input callbacks, and explain deviations. |
| L | Run focused `test_sizing.py` and `test_widgets.py` cases for nested layouts, hidden/shown items, menus, zero/negative dimensions, content origin, and failed configuration leaving valid items. Check expected geometry, not only absence of exceptions. |
| D | Verify solid/patterned primitives, arrows, vertex boundaries, and image rotation with asymmetric images and explicit quad UVs. Exercise DrawInWindow nested draw-state restoration and hidden/visible DrawingList publication. Check text screen-space sizing, font reload spacing, clipping, and animated DrawStream display. |
| T | Verify ordinary typed callback values and unchanged custom controller tuple payloads, callback arities/executors, per-slot dispatch, and exceptions. Regenerate/merge stubs without deleting Gamepad, enums, handlers, or PlotColorBars; compare runtime exports/signatures and generated declarations. |
| P | Run focused plot checks and PlotColorBars demo: horizontal/vertical, data/normalized modes, colors/borders, axis_min/axis_max/baseline anchors, secondary axes, ignore_fit, pan/zoom without a one-frame anchor lag. Verify against the same axes and input arrays before/after. |
| W | Review workflow diff and packaging registration, build/install Windows wheel, and verify import/custom exports. Validate existing Linux and free-threaded targets in their actual CI environments before declaring them passed. Do not trigger publishing/releases without approval. Preserve existing manual trigger and platform scope. |
| E | Finish cumulative in-scope regression run and bounded demo smoke checks. Where available, run DearCyFi with ChildWindow labels migrated and DrawInWindow3D publication, textured quads, animation, and interaction; unavailable consumers are recorded as unverified, not passed. |

Controller gates must record injected event counts and observed callback counts,
not just "controller works". A hardware-only visual smoke test does not replace
automated event-order or payload checks. Conversely mocks do not certify SDL
device discovery or real hardware.

Tests that need displays, hardware, another OS, a free-threaded interpreter, or
an external repository must record the available environment. Ask the user to
perform missing manual checks; do not silently waive them or install unrelated
tooling to create apparent coverage. A pre-existing failure must have a baseline
reproduction and explicit handling decision.

### Stage order and checkpoints

Stage A (commits 01-08): baseline, async execution, version/build and SDL updates.
Stage B (09-25): lifecycle/visibility, dependencies, layout rewrite and widgets.
Stage C (26-31): viewport scheduling, layout follow-ups, DrawInWindow state.
Stage D (32-43): drawing, initialization safety, API removals, initial stubs.
Stage E (44-49): typed callbacks and their follow-up fixes.
Stage F (50-55): fonts, negative widget sizes, wake fixes, final cleanup.

Dependencies follow source order unless a documented atomic group requires
otherwise. Build and run the relevant focused gates for each behavioral entry;
do not wait until a stage end to discover compile failures. Documentation-only
or comment-only patches need diff review, not a gratuitous full build. Stage
gates add cumulative coverage; all required stages must pass before continuing.

Create a named checkpoint at each passed stage with its evidence in tasks.md.
No push, commit, tag, branch promotion, or release publication is authorized by
proposal creation alone; obtain the applicable execution approval first.

## Risks / Trade-offs

- Disconnected histories make automatic merges misleading: use content and
  source-patch provenance, never raw ahead/behind counts as the feature inventory.
- Layout and callback changes are cross-cutting: stage them with prerequisites,
  consumers, declarations, package registration, and targeted regressions.
- Old generated stubs can erase custom APIs: inspect their custom generation
  inputs before regeneration.
- Native caches and generated C++ can hide failures: verify installed provenance
  and rebuild via the workspace procedure, keeping generated files untracked.
- Existing multi-controller/normalized-bar proposal checkboxes and wording lag
  the code: preserve observed behavior and record discrepancies; do not claim
  those independent proposals complete.

## Migration and rollback

Keep the original and backup refs unchanged. At a failed step, stop, record the
failure, and inspect only the integration work. Abort an in-progress cherry-pick
only after protecting deliberate resolution work; otherwise revert the relevant
integration commit(s) with approval. Do not use hard reset, force push, or
`--allow-unrelated-histories` as an integration shortcut.

Document migrations for removed arguments, changed drawing behavior and ordinary
typed callback data. Fix in-repository callers as part of the responsible stage.
External consumers receive a migration checklist; edits/runs in other repos need
permission. Preserve custom controller tuples rather than making users absorb an
unrequested gamepad API break.

## Open Questions

- Which physical/virtual controllers, displays, Linux CI runners, and
  free-threaded interpreters are available for the gates? Inventory before tests.
- Does the older replay integration branch contain useful prior resolutions?
  It is optional reference material, not an approved replacement for this branch.
- Does final validation reveal prerequisite corrections beyond the frozen range?
  Record and obtain approval for scope changes rather than silently extending it.
