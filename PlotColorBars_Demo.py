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

        with dcg.Window(self.C, label="PlotColorBars Demo", primary=True, width="fillx", height="filly"):
            with dcg.VerticalLayout(self.C, width="fillx", height="filly"):
                dcg.Text(
                    self.C,
                    value="Top plot: bottom-edge-anchored vertical bars with one fill color per bar.",
                )
                dcg.Text(
                    self.C,
                    value="Bottom plot: right-anchored horizontal bars. Pan or zoom the plot to verify the bars stay locked to the visible right edge.",
                )

                with dcg.Plot(self.C, label="Per-Bar Vertical Bars", width="fillx", height=380):
                    self._build_vertical_plot()

                with dcg.Plot(self.C, label="Right-Anchored Horizontal Bars", width="fillx", height=420) as horizontal_plot:
                    horizontal_plot.Y1.label = "Price"
                    horizontal_plot.X1.label = "Overlay / Backdrop X"
                    self._build_horizontal_plot()

    def _build_vertical_plot(self) -> None:
        x = np.arange(12, dtype=np.float64)
        y = np.array([3.5, 1.5, 4.0, 2.5, 5.2, 3.0, 4.4, 2.2, 5.8, 4.7, 3.1, 2.8], dtype=np.float64)
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
        dcg.PlotColorBars(
            self.C,
            X=x,
            Y=y,
            colors=colors,
            weight=0.8,
            anchor="axis_min",
            ignore_fit=True,
            label="Bottom-edge bars",
        )

        dcg.PlotLine(
            self.C,
            X=x,
            Y=np.array([2.0, 2.2, 2.3, 2.7, 3.0, 3.3, 3.2, 3.7, 4.0, 4.1, 4.2, 4.5], dtype=np.float64),
            label="Reference line",
        )

    def _build_horizontal_plot(self) -> None:
        x = np.linspace(0.0, 200.0, 240, dtype=np.float64)
        y = 100.0 + 8.0 * np.sin(x * 0.05) + 2.0 * np.cos(x * 0.13)
        lane_y = np.array([92.0, 96.0, 101.0, 106.0, 111.0], dtype=np.float64)
        widths = np.array([16.0, 10.0, 22.0, 14.0, 18.0], dtype=np.float64)
        fills = [
            (231, 76, 60, 150),
            (52, 152, 219, 150),
            (46, 204, 113, 150),
            (241, 196, 15, 150),
            (155, 89, 182, 150),
        ]
        #borders = [(255, 255, 255, 210)]

        dcg.PlotLine(
            self.C,
            X=x,
            Y=y,
            label="Backdrop price",
        )

        # In horizontal mode, axis_max anchors each bar to the visible right edge
        # of the plot. Using axis_min here would anchor them to the visible left
        # edge instead. Baseline mode is still available when you want a fixed
        # plot-coordinate origin rather than a viewport edge.
        dcg.PlotColorBars(
            self.C,
            X=widths,
            Y=lane_y,
            colors=fills,
            #line_colors=borders,  #this makes white borders around the bars, but they are clipped at the plot edge when anchored to axis_max
            horizontal=True,
            weight=2.7,
            anchor="axis_max",
            ignore_fit=True,
            label="Right-edge liquidity",
        )


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