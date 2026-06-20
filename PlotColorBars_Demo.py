import sys
from pathlib import Path

# This demo lives in the repo root next to the source package folder.
# Without this path fix, `import dearcygui` resolves to local sources first,
# which do not include the compiled extension module used at runtime.
repo_root = Path(__file__).resolve().parent
sys.path = [p for p in sys.path if Path(p).resolve() != repo_root]

site_packages = Path(sys.executable).resolve().parent.parent / "Lib" / "site-packages"
if site_packages.exists():
    sys.path.insert(0, str(site_packages))

import asyncio

import numpy as np

import dearcygui as dcg
from dearcygui.utils.asyncio_helpers import AsyncPoolExecutor, run_viewport_loop


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


class PlotColorBarsDemo:
    def __init__(self):
        self.C = dcg.Context()
        self.C.queue = AsyncPoolExecutor()
        self.C.viewport.wait_for_input = True
        self.C.viewport.initialize(height=920, width=1400, title="PlotColorBars Demo")

        self._lane_width_template = np.array([1.6, 1.0, 2.2, 1.4, 1.8], dtype=np.float64)
        self._lane_fill_template = [
            (231, 76, 60, 150),
            (52, 152, 219, 150),
            (46, 204, 113, 150),
            (241, 196, 15, 150),
            (155, 89, 182, 150),
        ]

        with dcg.Window(self.C, label="PlotColorBars Demo", primary=True, width="fillx", height="filly"):
            with dcg.VerticalLayout(self.C, width="fillx", height="filly"):
                dcg.Text(
                    self.C,
                    value="Single-plot test: bottom-edge vertical bars plus right-edge horizontal bars.",
                )
                dcg.Text(
                    self.C,
                    value="Pan or zoom to compare normalization behavior for both orientations in the same viewport.",
                )

                with dcg.HorizontalLayout(self.C, width="fillx"):
                    self.vertical_normalized_mode_toggle = dcg.Checkbox(
                        self.C,
                        label="Normalize Vertical Lengths",
                        value=True,
                        callback=lambda *_: self._update_vertical_bars(),
                    )
                    self.vertical_normalized_fraction_slider = dcg.Slider(
                        self.C,
                        label="Vertical Max Fraction",
                        min_value=0.05,
                        max_value=1.0,
                        value=0.2,
                        print_format="%.2f",
                        width=260,
                        callback=lambda *_: self._update_vertical_bars(),
                    )

                with dcg.HorizontalLayout(self.C, width="fillx"):
                    self.lane_base_slider = dcg.Slider(
                        self.C,
                        label="Lane Base",
                        min_value=0,
                        max_value=12.0,
                        value=0,
                        print_format="%.1f",
                        width=220,
                        callback=lambda *_: self._update_horizontal_bars(),
                    )
                    self.lane_pitch_slider = dcg.Slider(
                        self.C,
                        label="Lane Pitch",
                        min_value=0.3,
                        max_value=2.5,
                        value=0.9,
                        print_format="%.1f",
                        width=220,
                        callback=lambda *_: self._update_horizontal_bars(),
                    )
                    self.lane_count_slider = dcg.Slider(
                        self.C,
                        label="Lane Count",
                        min_value=1,
                        max_value=8,
                        value=5,
                        print_format="%.0f",
                        width=220,
                        callback=lambda *_: self._update_horizontal_bars(),
                    )
                    self.normalized_mode_toggle = dcg.Checkbox(
                        self.C,
                        label="Normalize Horizontal Lengths",
                        value=True,
                        callback=lambda *_: self._update_horizontal_bars(),
                    )
                    self.normalized_fraction_slider = dcg.Slider(
                        self.C,
                        label="Horizontal Max Fraction",
                        min_value=0.05,
                        max_value=1.0,
                        value=0.2,
                        print_format="%.2f",
                        width=260,
                        callback=lambda *_: self._update_horizontal_bars(),
                    )

                with dcg.Plot(self.C, label="Combined Vertical + Horizontal PlotColorBars", width="fillx", height=620) as combined_plot:
                    combined_plot.X1.label = "X"
                    combined_plot.Y1.label = "Y"
                    self._build_vertical_plot()
                    self._build_horizontal_plot()

    def _build_vertical_plot(self) -> None:
        self._vertical_x = np.arange(12, dtype=np.float64)
        self._vertical_y_template = np.array([3.5, 1.5, 4.0, 2.5, 5.2, 3.0, 4.4, 2.2, 5.8, 4.7, 3.1, 2.8], dtype=np.float64)
        colors = [
            (235, 94, 84, 185),
            (245, 176, 65, 185),
            (72, 201, 176, 185),
            (93, 109, 126, 185),
            (88, 214, 141, 185),
            (52, 152, 219, 185),
            (155, 89, 182, 185),
            (241, 196, 15, 185),
            (46, 204, 113, 185),
            (230, 126, 34, 185),
            (231, 76, 60, 185),
            (26, 188, 156, 185),
        ]

        # PlotColorBars supports three anchor modes:
        # - "baseline": bars start from anchor_value in plot coordinates
        # - "axis_min": bars start from the currently visible lower plot edge
        # - "axis_max": bars start from the currently visible upper plot edge
        # This example uses axis_min so the bars stay glued to the bottom edge
        # of the visible Y range while panning or zooming.
        self.vertical_bars = dcg.PlotColorBars(
            self.C,
            X=self._vertical_x,
            Y=self._vertical_y_template,
            colors=colors,
            weight=0.8,
            anchor="axis_min",
            ignore_fit=True,
            label="Bottom-edge bars",
        )

        dcg.PlotLine(
            self.C,
            X=self._vertical_x,
            Y=np.array([2.0, 2.2, 2.3, 2.7, 3.0, 3.3, 3.2, 3.7, 4.0, 4.1, 4.2, 4.5], dtype=np.float64),
            label="Reference line",
        )

        self._update_vertical_bars()

    def _update_vertical_bars(self) -> None:
        if not hasattr(self, "vertical_bars"):
            return

        is_normalized = bool(self.vertical_normalized_mode_toggle.value)
        normalized_fraction = float(self.vertical_normalized_fraction_slider.value)
        heights = np.array(self._vertical_y_template, copy=True)
        if is_normalized:
            height_scale = float(np.max(np.abs(heights)))
            if height_scale > 0.:
                heights = heights / height_scale

        self.vertical_bars.Y = heights
        self.vertical_bars.value_space = "normalized" if is_normalized else "data"
        self.vertical_bars.normalized_max_fraction = normalized_fraction
        self.C.viewport.wake()

    def _build_horizontal_plot(self) -> None:
        self._backdrop_x = np.linspace(0.0, 12.0, 240, dtype=np.float64)
        self._backdrop_y = 2.8 + 0.9 * np.sin(self._backdrop_x * 0.9) + 0.4 * np.cos(self._backdrop_x * 1.8)
        #borders = [(255, 255, 255, 210)]

        dcg.PlotLine(
            self.C,
            X=self._backdrop_x,
            Y=self._backdrop_y,
            label="Backdrop price",
        )

        # In horizontal mode, axis_max anchors each bar to the visible right edge
        # of the plot. Using axis_min here would anchor them to the visible left
        # edge instead. Baseline mode is still available when you want a fixed
        # plot-coordinate origin rather than a viewport edge.
        self.horizontal_bars = dcg.PlotColorBars(
            self.C,
            X=self._lane_width_template,
            Y=7.2 + 0.9 * np.arange(5, dtype=np.float64),
            colors=self._lane_fill_template,
            #line_colors=borders,  #this makes white borders around the bars, but they are clipped at the plot edge when anchored to axis_max
            horizontal=True,
            weight=4.5 * 0.6,
            anchor="axis_max",
            ignore_fit=True,
            label="Right-edge liquidity",
        )

        self._update_horizontal_bars()

    def _update_horizontal_bars(self) -> None:
        if not hasattr(self, "horizontal_bars"):
            return

        lane_base = float(self.lane_base_slider.value)
        lane_pitch = float(self.lane_pitch_slider.value)
        lane_count = max(1, int(round(float(self.lane_count_slider.value))))

        lane_y = lane_base + lane_pitch * np.arange(lane_count, dtype=np.float64)
        lane_bar_weight = lane_pitch * 0.6
        widths = np.resize(self._lane_width_template, lane_count)
        is_normalized = bool(self.normalized_mode_toggle.value)
        normalized_fraction = float(self.normalized_fraction_slider.value)
        if is_normalized:
            width_scale = float(np.max(np.abs(widths)))
            if width_scale > 0.:
                widths = widths / width_scale
        fills = [
            self._lane_fill_template[i % len(self._lane_fill_template)]
            for i in range(lane_count)
        ]

        current_count = len(self.horizontal_bars.X)
        if current_count != lane_count:
            # Avoid transient validation errors while count-dependent arrays
            # are being resized in separate property assignments.
            self.horizontal_bars.colors = None
            self.horizontal_bars.Y = None
            self.horizontal_bars.X = widths
            self.horizontal_bars.Y = lane_y
            self.horizontal_bars.colors = fills
        else:
            self.horizontal_bars.X = widths
            self.horizontal_bars.Y = lane_y
            self.horizontal_bars.colors = fills

        self.horizontal_bars.value_space = "normalized" if is_normalized else "data"
        self.horizontal_bars.normalized_max_fraction = normalized_fraction
        self.horizontal_bars.weight = lane_bar_weight
        self.C.viewport.wake()


if __name__ == "__main__":
    demo = PlotColorBarsDemo()
    try:
        loop.run_until_complete(run_viewport_loop(demo.C.viewport))
    except KeyboardInterrupt:
        print("PlotColorBars demo interrupted.")
    finally:
        for task in asyncio.all_tasks(loop):
            task.cancel()
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()