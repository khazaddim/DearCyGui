import sys
import random
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

        - No polling of `is_button_*` or `get_axis` happens here.
        - Every UI update is triggered by a `GamepadButtonHandler` or
            `GamepadAxisHandler` callback.
        - The single exception is connection / SDL name tracking, which has no
            event-driven API yet; a `RenderHandler` checks it periodically and
            re-syncs the slot labels.

        Important design notes:

        - Gamepad button handlers depend on frame-latched edge state
            (`pressed this frame` / `released this frame`), not on a persistent
            event queue.
        - That is a good fit for game input because it gives exactly-once
            semantics for actions like jump, confirm, or menu navigation while
            keeping held-state separate.
        - Because those button edges are tied to frame processing, the
            recommended loop for gamepad button handlers is the custom frame loop
            below, not `run_viewport_loop()`.
        - The custom loop calls `render_frame()` directly, so button edges are
            captured and consumed in the same frame.
        - In contrast, a helper that waits for events before starting the frame
            can process SDL button input too early, causing one-frame button edges
            to be cleared before the handlers observe them.
        - Axis values are level state and are less sensitive to that ordering,
            but buttons and D-pad presses are not.
    """

    def __init__(self):
        self.C = dcg.Context()
        self.C.queue = AsyncPoolExecutor()
        self.C.viewport.wait_for_input = True
        self.C.viewport.initialize(
            height=920, width=1440,
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
        self._plot_rng = random.Random(7)
        self._fullscreen_state = None

        # ---- UI ------------------------------------------------------------
        with dcg.Window(self.C, primary=True) as self.window:
            with dcg.HorizontalLayout(self.C, no_wrap=True):
                with dcg.ChildWindow(self.C, width=620, height=820, resizable_x=True):
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
                    dcg.Text(
                        self.C,
                        value="Use the plot on the right to test mouse pan/zoom while "
                              "pressing buttons or moving sticks.",
                    )
                    self.fullscreen_button = dcg.Button(
                        self.C,
                        label="Enter Fullscreen",
                        width="fillx",
                        callback=self._toggle_fullscreen,
                    )
                    self.fullscreen_status = dcg.Text(
                        self.C,
                        value="Viewport: windowed",
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

                with dcg.ChildWindow(self.C, width="fillx", height=820):
                    dcg.Text(self.C, value="--- Plot Interaction Probe ---")
                    dcg.Text(
                        self.C,
                        value="Pan with the mouse, zoom with the wheel, and mash controller "
                              "buttons to check that neither side interferes with the other.",
                    )
                    with dcg.Plot(self.C, label="Pannable Test Plot", width=-1, height=760):
                        with dcg.DrawInPlot(self.C, no_legend=True):
                            self._build_plot_probe()
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
        self._refresh_viewport_controls()

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
        self._refresh_viewport_controls()
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

    def _toggle_fullscreen(self, sender=None, target=None, data=None):
        self.C.viewport.fullscreen = not self.C.viewport.fullscreen
        self._refresh_viewport_controls()

    def _refresh_viewport_controls(self):
        is_fullscreen = bool(self.C.viewport.fullscreen)
        if is_fullscreen == self._fullscreen_state:
            return
        self._fullscreen_state = is_fullscreen
        self.fullscreen_button.label = (
            "Exit Fullscreen" if is_fullscreen else "Enter Fullscreen"
        )
        self.fullscreen_status.value = (
            "Viewport: fullscreen" if is_fullscreen else "Viewport: windowed"
        )

    def _build_plot_probe(self):
        for coord in range(-100, 101, 20):
            grid_color = (70, 78, 92, 110)
            axis_color = (105, 140, 175, 170)
            color = axis_color if coord == 0 else grid_color
            dcg.DrawLine(self.C, p1=(coord, -100), p2=(coord, 100), color=color, thickness=-1)
            dcg.DrawLine(self.C, p1=(-100, coord), p2=(100, coord), color=color, thickness=-1)

        route = [(-88, -72), (-62, -50), (-28, -36), (8, -12), (34, 16), (58, 22), (86, 48)]
        for p1, p2 in zip(route, route[1:]):
            dcg.DrawLine(self.C, p1=p1, p2=p2, color=(92, 218, 160, 230), thickness=-3)

        for point in route:
            dcg.DrawCircle(
                self.C,
                center=point,
                radius=-5,
                color=(14, 18, 24, 220),
                fill=(92, 218, 160, 255),
                thickness=-1,
            )

        palette = [
            ((208, 122, 88, 255), (208, 122, 88, 70)),
            ((111, 161, 224, 255), (111, 161, 224, 70)),
            ((199, 179, 76, 255), (199, 179, 76, 70)),
        ]
        for index in range(9):
            cx = self._plot_rng.uniform(-82.0, 82.0)
            cy = self._plot_rng.uniform(-82.0, 82.0)
            half_w = self._plot_rng.uniform(5.0, 14.0)
            half_h = self._plot_rng.uniform(4.0, 12.0)
            outline, fill = palette[index % len(palette)]
            dcg.DrawRect(
                self.C,
                pmin=(cx - half_w, cy - half_h),
                pmax=(cx + half_w, cy + half_h),
                color=outline,
                fill=fill,
                thickness=-2,
            )

        for index in range(10):
            x = self._plot_rng.uniform(-90.0, 90.0)
            y = self._plot_rng.uniform(-90.0, 90.0)
            radius = self._plot_rng.uniform(3.0, 8.0)
            dcg.DrawCircle(
                self.C,
                center=(x, y),
                radius=radius,
                color=(184, 116, 236, 230),
                fill=(184, 116, 236, 70),
                thickness=-2,
            )

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
        await asyncio.sleep(1.0 / 120.0)


if __name__ == "__main__":
    demo = InputDemo()
    try:
        loop.run_until_complete(main_loop(demo.C.viewport))
    except Exception as e:
        print(f"Error: {e}")
