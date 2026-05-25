import sys
from pathlib import Path

# This demo lives in the repo root next to the source package folder.
# Without this path fix, `import dearcygui` resolves to local sources first,
# which do not include the compiled extension module used at runtime.
# We force imports to come from the installed venv package instead.
repo_root = Path(__file__).resolve().parent
sys.path = [p for p in sys.path if Path(p).resolve() != repo_root]

# Put the active venv's site-packages first so the installed package wins.
site_packages = Path(sys.executable).resolve().parent.parent / "Lib" / "site-packages"
if site_packages.exists():
    sys.path.insert(0, str(site_packages))

import asyncio

import dearcygui as dcg
from dearcygui.utils.asyncio_helpers import AsyncPoolExecutor


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


# All named buttons exposed by the GamepadButton enum, with display labels.
BUTTON_NAMES = {
    dcg.GamepadButton.SOUTH:          "A / Cross",
    dcg.GamepadButton.EAST:           "B / Circle",
    dcg.GamepadButton.WEST:           "X / Square",
    dcg.GamepadButton.NORTH:          "Y / Triangle",
    dcg.GamepadButton.BACK:           "Back",
    dcg.GamepadButton.GUIDE:          "Guide",
    dcg.GamepadButton.START:          "Start",
    dcg.GamepadButton.LEFT_STICK:     "L-Stick Click",
    dcg.GamepadButton.RIGHT_STICK:    "R-Stick Click",
    dcg.GamepadButton.LEFT_SHOULDER:  "LB",
    dcg.GamepadButton.RIGHT_SHOULDER: "RB",
    dcg.GamepadButton.DPAD_UP:        "D-Pad Up",
    dcg.GamepadButton.DPAD_DOWN:      "D-Pad Down",
    dcg.GamepadButton.DPAD_LEFT:      "D-Pad Left",
    dcg.GamepadButton.DPAD_RIGHT:     "D-Pad Right",
    dcg.GamepadButton.MISC1:          "Misc1",
    dcg.GamepadButton.RIGHT_PADDLE1:  "R-Paddle1",
    dcg.GamepadButton.LEFT_PADDLE1:   "L-Paddle1",
    dcg.GamepadButton.RIGHT_PADDLE2:  "R-Paddle2",
    dcg.GamepadButton.LEFT_PADDLE2:   "L-Paddle2",
    dcg.GamepadButton.TOUCHPAD:       "Touchpad",
}

AXIS_NAMES = {
    dcg.GamepadAxis.LEFT_X:        "LX",
    dcg.GamepadAxis.LEFT_Y:        "LY",
    dcg.GamepadAxis.RIGHT_X:       "RX",
    dcg.GamepadAxis.RIGHT_Y:       "RY",
    dcg.GamepadAxis.LEFT_TRIGGER:  "LT",
    dcg.GamepadAxis.RIGHT_TRIGGER: "RT",
}

NUM_SLOTS = 8
HISTORY_SIZE = 8
AXIS_DEADZONE = 0.15


class InputDemo:
    """Purely event-driven multi-controller demo.

    No polling of `is_button_*` or `get_axis` happens here. Every UI
    update is triggered by a `GamepadButtonHandler` or `GamepadAxisHandler`
    callback. The single exception is connection / SDL name tracking,
    which has no event-driven API yet — a `RenderHandler` checks it
    periodically and re-syncs the slot labels.
    """

    def __init__(self):
        self.C = dcg.Context()
        self.C.queue = AsyncPoolExecutor()
        self.C.viewport.wait_for_input = True
        self.C.viewport.initialize(
            height=820, width=900,
            title="Multi-Controller Demo (event-driven)",
        )

        # ---- Per-slot state (mutated only from handler callbacks) ----------
        self.held = [set() for _ in range(NUM_SLOTS)]            # set[GamepadButton]
        self.press_counts = [0] * NUM_SLOTS
        self.release_counts = [0] * NUM_SLOTS
        self.axis_event_counts = [0] * NUM_SLOTS
        self.axis_values = [
            {ax: 0.0 for ax in AXIS_NAMES} for _ in range(NUM_SLOTS)
        ]
        self.history = [[] for _ in range(NUM_SLOTS)]            # newest-first
        # Cached connection state, updated by the RenderHandler.
        self.connected = [False] * NUM_SLOTS
        self.names = [""] * NUM_SLOTS

        # ---- UI ------------------------------------------------------------
        with dcg.Window(self.C, primary=True) as self.window:
            dcg.Text(self.C, value="=== Multi-Controller Input Demo (event-driven) ===")
            dcg.Text(
                self.C,
                value="All updates come from GamepadButtonHandler / "
                      "GamepadAxisHandler callbacks. No polling.",
            )
            dcg.Text(
                self.C,
                value=f"Axis deadzone = {AXIS_DEADZONE}. Slot/name list "
                      "is refreshed once per frame from a RenderHandler.",
            )
            dcg.Text(self.C, value="")

            self.slot_labels = []
            self.held_labels = []
            self.counts_labels = []
            self.axis_labels = []
            self.history_labels = []

            for i in range(NUM_SLOTS):
                dcg.Text(self.C, value=f"--- Slot {i} ---")
                self.slot_labels.append(
                    dcg.Text(self.C, value=f"  [{i}] (disconnected)")
                )
                self.held_labels.append(
                    dcg.Text(self.C, value="       Held:    (none)")
                )
                self.counts_labels.append(
                    dcg.Text(self.C, value="       Counts:  press=0  release=0  axis=0")
                )
                self.axis_labels.append(
                    dcg.Text(
                        self.C,
                        value="       Axes:    LX=+0.00 LY=+0.00  "
                              "RX=+0.00 RY=+0.00  LT=0.00 RT=0.00",
                    )
                )
                self.history_labels.append(
                    dcg.Text(self.C, value="       Events:  ---")
                )

        # ---- Handlers ------------------------------------------------------
        # One press- and one release-handler per named button, in
        # "any controller" mode. Callbacks demultiplex by slot.
        handlers = []
        for btn in BUTTON_NAMES:
            handlers.append(dcg.GamepadButtonHandler(
                self.C, controller=-1, button=btn, on_press=True,
                callback=self._on_button_press,
            ))
            handlers.append(dcg.GamepadButtonHandler(
                self.C, controller=-1, button=btn, on_press=False,
                callback=self._on_button_release,
            ))
        # One axis handler per axis, any controller, shared deadzone.
        for ax in AXIS_NAMES:
            handlers.append(dcg.GamepadAxisHandler(
                self.C, controller=-1, axis=ax, deadzone=AXIS_DEADZONE,
                callback=self._on_axis,
            ))
        # RenderHandler keeps the connection / SDL3 name line in sync.
        # (There's no connect/disconnect callback in the API yet.)
        handlers.append(dcg.RenderHandler(
            self.C, callback=self._on_render,
        ))

        self.window.handlers = handlers

    # ---- Handler callbacks -------------------------------------------------
    def _on_button_press(self, sender, target, data):
        slot, button = data
        self.held[slot].add(button)
        self.press_counts[slot] += 1
        self._push_event(slot, f"+{BUTTON_NAMES.get(button, button.name)}")
        self._refresh_slot(slot)

    def _on_button_release(self, sender, target, data):
        slot, button = data
        self.held[slot].discard(button)
        self.release_counts[slot] += 1
        self._push_event(slot, f"-{BUTTON_NAMES.get(button, button.name)}")
        self._refresh_slot(slot)

    def _on_axis(self, sender, target, data):
        slot, value = data
        self.axis_values[slot][sender.axis] = value
        self.axis_event_counts[slot] += 1
        self._refresh_slot(slot)

    def _on_render(self, sender, target, data):
        # The only non-event work: notice connect / disconnect and refresh
        # the slot header. We DO NOT poll buttons or axes here.
        gamepads = self.C.viewport.gamepads
        for i in range(NUM_SLOTS):
            gp = gamepads[i]
            now_connected = bool(gp.connected)
            now_name = gp.name if now_connected else ""
            if now_connected != self.connected[i] or now_name != self.names[i]:
                self.connected[i] = now_connected
                self.names[i] = now_name
                if not now_connected:
                    # Clear stale per-slot state so the UI doesn't lie.
                    self.held[i].clear()
                    for ax in AXIS_NAMES:
                        self.axis_values[i][ax] = 0.0
                    self.history[i].clear()
                self._refresh_slot(i)

    # ---- UI helpers --------------------------------------------------------
    def _push_event(self, slot, entry):
        log = self.history[slot]
        log.insert(0, entry)
        if len(log) > HISTORY_SIZE:
            del log[HISTORY_SIZE:]

    def _refresh_slot(self, i):
        if self.connected[i]:
            self.slot_labels[i].value = f"  [{i}] {self.names[i] or '(unnamed)'}"
        else:
            self.slot_labels[i].value = f"  [{i}] (disconnected)"

        if self.held[i]:
            held_str = ", ".join(
                BUTTON_NAMES.get(b, b.name) for b in sorted(self.held[i], key=lambda b: int(b))
            )
        else:
            held_str = "(none)"
        self.held_labels[i].value = f"       Held:    {held_str}"

        self.counts_labels[i].value = (
            f"       Counts:  press={self.press_counts[i]}  "
            f"release={self.release_counts[i]}  axis={self.axis_event_counts[i]}"
        )

        v = self.axis_values[i]
        self.axis_labels[i].value = (
            f"       Axes:    "
            f"LX={v[dcg.GamepadAxis.LEFT_X]:+.2f} LY={v[dcg.GamepadAxis.LEFT_Y]:+.2f}  "
            f"RX={v[dcg.GamepadAxis.RIGHT_X]:+.2f} RY={v[dcg.GamepadAxis.RIGHT_Y]:+.2f}  "
            f"LT={v[dcg.GamepadAxis.LEFT_TRIGGER]:.2f} "
            f"RT={v[dcg.GamepadAxis.RIGHT_TRIGGER]:.2f}"
        )

        if self.history[i]:
            self.history_labels[i].value = (
                "       Events:  " + "  ".join(self.history[i])
            )
        else:
            self.history_labels[i].value = "       Events:  ---"


async def main_loop(viewport):
    while viewport.context.running:
        viewport.render_frame()
        await asyncio.sleep(1.0 / 60.0)


if __name__ == "__main__":
    demo = InputDemo()
    try:
        loop.run_until_complete(main_loop(demo.C.viewport))
    except Exception as e:
        print(f"Error: {e}")
