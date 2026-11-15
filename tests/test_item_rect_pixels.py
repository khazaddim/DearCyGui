"""Verify that item state rectangles contain their framebuffer pixels."""

import gc
import time
from collections.abc import Iterator

import dearcygui as dcg
import numpy as np
import pytest


@pytest.fixture
def context() -> Iterator[dcg.Context]:
    """Create a viewport with framebuffer readback enabled."""
    ctx = dcg.Context()
    ctx.viewport.initialize(
        visible=False, width=800, height=600,
        always_submit_to_gpu=True, retrieve_framebuffer=True,
    )
    ctx.viewport.vsync = False
    yield ctx
    ctx.queue.shutdown(wait=True)
    ctx.viewport.children = []
    gc.collect()
    deadline = time.monotonic() + 5
    while True:
        try:
            ctx.viewport.destroy()
            break
        except RuntimeError as error:
            if "resources are in use" not in str(error) or time.monotonic() >= deadline:
                raise
            time.sleep(0.01)


def _pixels(ctx: dcg.Context) -> np.ndarray:
    """Render stabilized frames and return top-down framebuffer pixels."""
    for _ in range(6):
        ctx.viewport.render_frame()
    framebuffer = ctx.viewport.framebuffer
    assert framebuffer is not None
    return np.asarray(framebuffer.read())[::-1].copy()


@pytest.mark.parametrize(
    "kind", (
        "small_button", "text", "bullet_text", "text_value", "vector", "selectable",
        "collapsing_header", "open_header", "tree_node",
    )
)
@pytest.mark.parametrize("frame_padding", ((4, 3), (6, 8)))
def test_item_rect_contains_drawn_pixels(
    context: dcg.Context, *, kind: str, frame_padding: tuple[int, int]
) -> None:
    """Contain the visual changes in the reported rectangle on a shared line."""
    theme = dcg.ThemeStyleImGui(context, frame_padding=frame_padding)
    window = dcg.Window(context, width=600, height=400, theme=theme)
    dcg.Button(context, parent=window, label="Leading", no_newline=True)
    if kind == "small_button":
        item = dcg.Button(context, parent=window, label="Small", small=True, show=False)
    elif kind == "text":
        item = dcg.Text(context, parent=window, value="Example text", show=False)
    elif kind == "bullet_text":
        item = dcg.Text(
            context, parent=window, value="Example text", marker="bullet", show=False
        )
    elif kind == "text_value":
        item = dcg.TextValue(
            context, parent=window, value=-42, print_format="Value: %.3f", show=False
        )
    elif kind == "vector":
        item = dcg.TextValue(
            context, parent=window, shareable_value=dcg.SharedFloatVect(context, (1, 2, 3)),
            show=False,
        )
    elif kind == "collapsing_header":
        item = dcg.CollapsingHeader(context, parent=window, label="Header", show=False)
    elif kind == "open_header":
        item = dcg.CollapsingHeader(
            context, parent=window, label="Header", value=True, show=False
        )
        dcg.Button(context, parent=item, label="Child")
    elif kind == "tree_node":
        item = dcg.TreeNode(context, parent=window, label="Tree", show=False)
    else:
        item = dcg.Selectable(
            context, parent=window, label="Selectable", highlighted=True, width=100, show=False
        )
    background = _pixels(context)
    item.show = True
    foreground = _pixels(context)
    changed = np.any(background[:, :, :3] != foreground[:, :, :3], axis=2)
    assert changed.any()
    x, y = (int(value) for value in item.state.pos_to_viewport)
    width, height = (int(value) for value in item.state.rect_size)
    assert tuple(item.state.pos_to_window) == pytest.approx(
        (x - window.state.content_pos.x, y - window.state.content_pos.y)
    )
    assert tuple(item.state.pos_to_parent) == pytest.approx(
        (x - window.state.content_pos.x, y - window.state.content_pos.y)
    )
    changed[y:y + height, x:x + width] = False
    assert not changed.any(), f"{kind} draws outside {(x, y, width, height)}"
