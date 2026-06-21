import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent
sys.path = [p for p in sys.path if Path(p).resolve() != repo_root]
site_packages = Path(sys.executable).resolve().parent.parent / "Lib" / "site-packages"
if site_packages.exists():
    sys.path.insert(0, str(site_packages))

import asyncio

import dearcygui as dcg
from dearcygui.utils.asyncio_helpers import run_viewport_loop


async def main():
    ctx = dcg.Context()
    ctx.viewport.wait_for_input = True
    ctx.viewport.initialize(height=320, width=480, title="Bare Window Probe")

    with dcg.Window(ctx, label="Bare", primary=True, width="fillx", height="filly"):
        dcg.Text(ctx, value="Bare window probe")

    try:
        await asyncio.wait_for(run_viewport_loop(ctx.viewport), timeout=1.0)
    except TimeoutError:
        print("BARE_WINDOW_OK")
    finally:
        ctx.running = False
        ctx.viewport.wake()


asyncio.run(main())