import sys
from pathlib import Path

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

C = dcg.Context()
C.queue = AsyncPoolExecutor()
C.viewport.wait_for_input = True
C.viewport.initialize(height=600, width=900, title="Minimal PlotColorBars")

with dcg.Window(C, label="Minimal", primary=True, width="fillx", height="filly"):
    with dcg.Plot(C, label="Test", width="fillx", height="filly"):
        dcg.PlotColorBars(
            C,
            X=np.arange(5, dtype=np.float64),
            Y=np.array([1.0, 2.0, 3.0, 2.5, 1.5], dtype=np.float64),
            weight=0.8,
            anchor="baseline",
            anchor_value=0.0,
            ignore_fit=True,
            label="bars",
        )

async def main():
    await run_viewport_loop(C.viewport)

loop.run_until_complete(main())
