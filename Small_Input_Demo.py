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

# Button names for display
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
}

# How long (in frames) to keep showing a single-frame edge event so the
# human eye can see it. Edge flags themselves are still strictly one frame
# at the API level; this is a UI-only display latch.
EDGE_LATCH_FRAMES = 30

# How many press/release events to keep in the rolling history per slot.
HISTORY_SIZE = 6


class InputDemo:
    def __init__(self):

        self.C = dcg.Context()
        self.C.queue = AsyncPoolExecutor()
        self.C.viewport.wait_for_input = False
        self.C.viewport.initialize(height=720, width=720, title="Multi-Controller Demo (M2)")

        # Per-slot counters used to verify "exactly once per press/release".
        self.press_counts = [{} for _ in range(8)]    # {label: int}
        self.release_counts = [{} for _ in range(8)]  # {label: int}

        # Rolling per-slot event history strings.
        self.history = [[] for _ in range(8)]

        # Per-slot display latches: {label: frames_remaining}
        self.pressed_latch = [{} for _ in range(8)]
        self.released_latch = [{} for _ in range(8)]

        # M3: rolling log of handler-driven callback events (most recent first).
        self.handler_log = []
        self.HANDLER_LOG_SIZE = 5
        # M3: per-slot press / release counters fed by the handler callback.
        self.handler_press_counts = [0] * 8
        self.handler_release_counts = [0] * 8

        # M4: per-slot axis-handler call counter and rolling log.
        self.axis_handler_counts = [0] * 8
        self.axis_handler_log = []
        self.AXIS_LOG_SIZE = 5
        # M4: latest reported (deadzone-filtered) value per slot for LEFT_X.
        self.axis_handler_last = [0.0] * 8

        with dcg.Window(self.C, primary=True) as self.window:
            dcg.Text(self.C, value="=== Multi-Controller Input Demo (M2: edge detection) ===")
            dcg.Text(self.C, value="Hold buttons to test 'Held'. Tap to test 'Pressed' / 'Released'.")
            dcg.Text(self.C, value="Counts confirm exactly-once edge detection per press/release.")
            dcg.Text(self.C, value="")

            # M3: handler-driven event log (independent of polling above).
            dcg.Text(self.C, value="--- M3 GamepadButtonHandler (A / SOUTH button, any controller) ---")
            dcg.Text(
                self.C,
                value="  Callback-driven (not polled). Each A press/release fires a callback.",
            )
            self.handler_counts_label = dcg.Text(
                self.C, value="  Totals:  (no events yet)"
            )
            self.handler_status = dcg.Text(
                self.C, value="  Last events (newest first):  (none yet)"
            )
            dcg.Text(self.C, value="")

            # M4: axis-handler event log.
            dcg.Text(self.C, value="--- M4 GamepadAxisHandler (LEFT_X, any controller, deadzone=0.15) ---")
            dcg.Text(
                self.C,
                value="  Callback-driven. Only fires when filtered value changes; deadzone suppresses jitter.",
            )
            self.axis_counts_label = dcg.Text(
                self.C, value="  Totals:  (no events yet)"
            )
            self.axis_last_label = dcg.Text(
                self.C, value="  Latest per slot:  (no events yet)"
            )
            self.axis_status = dcg.Text(
                self.C, value="  Last events (newest first):  (none yet)"
            )
            dcg.Text(self.C, value="")

            self.slot_labels = []
            self.held_labels = []
            self.pressed_labels = []
            self.released_labels = []
            self.axis_labels = []
            self.count_labels = []
            self.history_labels = []

            for i in range(8):
                dcg.Text(self.C, value=f"--- Slot {i} ---")
                sl = dcg.Text(self.C, value=f"  [{i}] (empty)")
                hl = dcg.Text(self.C, value="       Held:     ---")
                pl = dcg.Text(self.C, value="       Pressed:  ---")
                rl = dcg.Text(self.C, value="       Released: ---")
                al = dcg.Text(self.C, value="       Axes:     ---")
                cl = dcg.Text(self.C, value="       Counts:   ---")
                hsl = dcg.Text(self.C, value="       History:  ---")
                self.slot_labels.append(sl)
                self.held_labels.append(hl)
                self.pressed_labels.append(pl)
                self.released_labels.append(rl)
                self.axis_labels.append(al)
                self.count_labels.append(cl)
                self.history_labels.append(hsl)

        # M3: Attach GamepadButtonHandler instances to the window.
        # One handler for SOUTH (A / Cross) press on ANY controller,
        # another for SOUTH release on ANY controller. The callback runs
        # via the normal handler dispatch — no polling involved.
        h_press = dcg.GamepadButtonHandler(
            self.C,
            controller=-1,
            button=dcg.GamepadButton.SOUTH,
            on_press=True,
            callback=self._on_gamepad_event,
        )
        h_release = dcg.GamepadButtonHandler(
            self.C,
            controller=-1,
            button=dcg.GamepadButton.SOUTH,
            on_press=False,
            callback=self._on_gamepad_event,
        )
        # M4: GamepadAxisHandler — LEFT_X on any controller, default deadzone.
        h_axis = dcg.GamepadAxisHandler(
            self.C,
            controller=-1,
            axis=dcg.GamepadAxis.LEFT_X,
            deadzone=0.15,
            callback=self._on_axis_event,
        )
        self.window.handlers = [h_press, h_release, h_axis]

    def _on_gamepad_event(self, sender, target, data):
        """Callback for the M3 GamepadButtonHandler.

        ``data`` is a (controller_slot, GamepadButton) tuple.
        """
        slot, button = data
        if sender.on_press:
            self.handler_press_counts[slot] += 1
            edge = "DOWN"
        else:
            self.handler_release_counts[slot] += 1
            edge = "UP"
        # Newest-first rolling log.
        self.handler_log.insert(0, f"slot{slot} {button.name} {edge}")
        if len(self.handler_log) > self.HANDLER_LOG_SIZE:
            self.handler_log = self.handler_log[: self.HANDLER_LOG_SIZE]

        # Update counter line (one entry per slot that has fired).
        parts = []
        for s in range(8):
            p = self.handler_press_counts[s]
            r = self.handler_release_counts[s]
            if p or r:
                parts.append(f"slot{s}: {p} press / {r} release")
        self.handler_counts_label.value = (
            "  Totals:  " + ("   |   ".join(parts) if parts else "(no events yet)")
        )
        self.handler_status.value = (
            "  Last events (newest first):  " + "  <-  ".join(self.handler_log)
        )

    def _on_axis_event(self, sender, target, data):
        """Callback for the M4 GamepadAxisHandler.

        ``data`` is a (controller_slot, axis_value) tuple. The value is
        already deadzone-filtered by the handler (raw values whose absolute
        magnitude is below the deadzone arrive as exactly 0.0).
        """
        slot, value = data
        self.axis_handler_counts[slot] += 1
        self.axis_handler_last[slot] = value
        # Newest-first rolling log; show 2-decimal precision.
        self.axis_handler_log.insert(0, f"slot{slot} LEFT_X={value:+.2f}")
        if len(self.axis_handler_log) > self.AXIS_LOG_SIZE:
            self.axis_handler_log = self.axis_handler_log[: self.AXIS_LOG_SIZE]

        # Totals line (one entry per slot that has fired).
        parts = [
            f"slot{s}: {self.axis_handler_counts[s]} cb"
            for s in range(8)
            if self.axis_handler_counts[s]
        ]
        self.axis_counts_label.value = (
            "  Totals:  " + ("   |   ".join(parts) if parts else "(no events yet)")
        )
        # Latest filtered value per slot that has ever fired.
        latest = [
            f"slot{s}={self.axis_handler_last[s]:+.2f}"
            for s in range(8)
            if self.axis_handler_counts[s]
        ]
        self.axis_last_label.value = (
            "  Latest per slot:  " + ("  ".join(latest) if latest else "(no events yet)")
        )
        self.axis_status.value = (
            "  Last events (newest first):  " + "  <-  ".join(self.axis_handler_log)
        )

    def _reset_slot(self, i):
        self.press_counts[i].clear()
        self.release_counts[i].clear()
        self.history[i].clear()
        self.pressed_latch[i].clear()
        self.released_latch[i].clear()
        self.slot_labels[i].value = f"  [{i}] (empty)"
        self.held_labels[i].value = "       Held:     ---"
        self.pressed_labels[i].value = "       Pressed:  ---"
        self.released_labels[i].value = "       Released: ---"
        self.axis_labels[i].value = "       Axes:     ---"
        self.count_labels[i].value = "       Counts:   ---"
        self.history_labels[i].value = "       History:  ---"

    def poll_gamepads(self):
        """Update display from live gamepad state.

        Must be called AFTER render_frame() so edge flags reflect events
        processed during the just-completed frame.
        """
        gamepads = self.C.viewport.gamepads
        for i, gp in enumerate(gamepads):
            if not gp.connected:
                self._reset_slot(i)
                continue

            self.slot_labels[i].value = f"  [{i}] {gp.name}"

            # ---- Held buttons (continuous) ------------------------------------
            held = []
            for btn, label in BUTTON_NAMES.items():
                if gp.is_button_down(btn):
                    held.append(label)
            self.held_labels[i].value = (
                f"       Held:     {', '.join(held) if held else '(none)'}"
            )

            # ---- Edge events (one frame each) ---------------------------------
            for btn, label in BUTTON_NAMES.items():
                if gp.is_button_pressed(btn):
                    self.press_counts[i][label] = self.press_counts[i].get(label, 0) + 1
                    self.pressed_latch[i][label] = EDGE_LATCH_FRAMES
                    self.history[i].append(f"+{label}")
                if gp.is_button_released(btn):
                    self.release_counts[i][label] = self.release_counts[i].get(label, 0) + 1
                    self.released_latch[i][label] = EDGE_LATCH_FRAMES
                    self.history[i].append(f"-{label}")

            # Trim history to the most recent HISTORY_SIZE entries
            if len(self.history[i]) > HISTORY_SIZE:
                self.history[i] = self.history[i][-HISTORY_SIZE:]

            # Decay the display latches. The underlying edge flags themselves
            # are still strictly true for exactly one frame.
            for d in (self.pressed_latch[i], self.released_latch[i]):
                for k in list(d.keys()):
                    d[k] -= 1
                    if d[k] <= 0:
                        del d[k]

            self.pressed_labels[i].value = (
                "       Pressed:  "
                + (", ".join(sorted(self.pressed_latch[i].keys()))
                   if self.pressed_latch[i] else "(none)")
            )
            self.released_labels[i].value = (
                "       Released: "
                + (", ".join(sorted(self.released_latch[i].keys()))
                   if self.released_latch[i] else "(none)")
            )

            # ---- Axes ---------------------------------------------------------
            lx = gp.get_axis(dcg.GamepadAxis.LEFT_X)
            ly = gp.get_axis(dcg.GamepadAxis.LEFT_Y)
            rx = gp.get_axis(dcg.GamepadAxis.RIGHT_X)
            ry = gp.get_axis(dcg.GamepadAxis.RIGHT_Y)
            lt = gp.get_axis(dcg.GamepadAxis.LEFT_TRIGGER)
            rt = gp.get_axis(dcg.GamepadAxis.RIGHT_TRIGGER)
            self.axis_labels[i].value = (
                f"       Axes:     L({lx:+.2f},{ly:+.2f})  "
                f"R({rx:+.2f},{ry:+.2f})  "
                f"LT={lt:.2f}  RT={rt:.2f}"
            )

            # ---- Counts (verify exactly once per press / release) -------------
            if self.press_counts[i] or self.release_counts[i]:
                parts = []
                for label in BUTTON_NAMES.values():
                    p = self.press_counts[i].get(label, 0)
                    r = self.release_counts[i].get(label, 0)
                    if p or r:
                        parts.append(f"{label}:{p}/{r}")
                self.count_labels[i].value = (
                    f"       Counts:   {' | '.join(parts)}  (press/release)"
                )
            else:
                self.count_labels[i].value = "       Counts:   (none yet)"

            # ---- History ------------------------------------------------------
            if self.history[i]:
                self.history_labels[i].value = (
                    f"       History:  {'  '.join(self.history[i])}"
                )
            else:
                self.history_labels[i].value = "       History:  ---"


async def main_loop(viewport, demo):
    """Render loop that polls gamepad state AFTER render_frame().

    For M2, edge flags are cleared at the start of render_frame() and set as
    SDL events are processed. Polling after render_frame() reads the flags
    set during this frame.
    """
    while viewport.context.running:
        viewport.render_frame()
        demo.poll_gamepads()
        await asyncio.sleep(1.0 / 60.0)


if __name__ == "__main__":
    demo = InputDemo()
    try:
        loop.run_until_complete(main_loop(demo.C.viewport, demo))
    except Exception as e:
        print(f"Error: {e}")
