"""Exercise mouse input spanning slow or on-demand frames."""

import gc
import threading
from collections.abc import Iterator

import dearcygui as dcg
import pytest


@pytest.fixture
def context() -> Iterator[dcg.Context]:
    """Create a hidden viewport and dispose of it after the test."""
    ctx = dcg.Context()
    ctx.viewport.initialize(visible=False, width=800, height=600)
    ctx.viewport.vsync = False
    yield ctx
    ctx.queue.shutdown(wait=True)
    ctx.viewport.destroy()
    gc.collect()


def _render(ctx: dcg.Context, *, count: int = 1) -> None:
    """Run the requested number of logical frames."""
    for _ in range(count):
        ctx.viewport.render_frame()


def test_plot_pan_uses_only_motion_between_press_and_release(context: dcg.Context) -> None:
    """Apply the release-frame drag without panning on a later click."""
    window = dcg.Window(context, width=700, height=500)
    plot = dcg.Plot(context, parent=window, width=600, height=400)
    for axis in (plot.X1, plot.Y1):
        axis.no_initial_fit = True
        axis.min = 0
        axis.max = 30
    _render(context, count=5)

    x, y = plot.state.pos_to_viewport
    width, height = plot.state.rect_size
    start = (x + width / 2, y + height / 2)
    context.inject_mouse_pos(*start)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    initial = (plot.X1.min, plot.X1.max, plot.Y1.min, plot.Y1.max)

    context.inject_mouse_pos(start[0] + 20, start[1] + 15)
    _render(context)
    held = (plot.X1.min, plot.X1.max, plot.Y1.min, plot.Y1.max)
    context.inject_mouse_pos(start[0] + 40, start[1] + 30)
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    context.inject_mouse_pos(start[0] + 80, start[1] + 60)
    _render(context)
    released = (plot.X1.min, plot.X1.max, plot.Y1.min, plot.Y1.max)
    assert released[0] < initial[0]
    assert released[2] > initial[2]
    assert released == pytest.approx(
        tuple(2 * held[i] - initial[i] for i in range(4)), abs=0.01
    )
    _render(context)
    assert (plot.X1.min, plot.X1.max, plot.Y1.min, plot.Y1.max) == pytest.approx(released)

    context.inject_mouse_pos(start[0] - 50, start[1] - 40)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    assert (plot.X1.min, plot.X1.max, plot.Y1.min, plot.Y1.max) == pytest.approx(released)


def test_plot_release_pan_respects_locked_axis(context: dcg.Context) -> None:
    """Keep a locked axis fixed when applying the final pan movement."""
    window = dcg.Window(context, width=700, height=500)
    plot = dcg.Plot(context, parent=window, width=600, height=400)
    for axis in (plot.X1, plot.Y1):
        axis.no_initial_fit = True
        axis.min = 0
        axis.max = 30
    plot.X1.lock_min = True
    plot.X1.lock_max = True
    _render(context, count=5)

    x, y = plot.state.pos_to_viewport
    width, height = plot.state.rect_size
    start = (x + width / 2, y + height / 2)
    initial = (plot.X1.min, plot.X1.max, plot.Y1.min, plot.Y1.max)
    context.inject_mouse_pos(*start)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    context.inject_mouse_pos(start[0] + 40, start[1] + 30)
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)

    assert (plot.X1.min, plot.X1.max) == pytest.approx(initial[:2])
    assert plot.Y1.min > initial[2]
    assert plot.Y1.max > initial[3]


def test_plot_axis_pan_applies_release_motion(context: dcg.Context) -> None:
    """Apply a release-frame axis drag only to the selected axis."""
    window = dcg.Window(context, width=700, height=500)
    plot = dcg.Plot(context, parent=window, width=600, height=400)
    for axis in (plot.X1, plot.Y1):
        axis.no_initial_fit = True
        axis.min = 0
        axis.max = 30
    _render(context, count=5)

    x, y = plot.state.pos_to_viewport
    width, height = plot.state.rect_size
    start = (x + width / 2, y + height - 10)
    initial = (plot.X1.min, plot.X1.max, plot.Y1.min, plot.Y1.max)
    context.inject_mouse_pos(*start)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    context.inject_mouse_pos(start[0] + 40, start[1] + 5)
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)

    assert plot.X1.min < initial[0]
    assert plot.X1.max < initial[1]
    assert (plot.Y1.min, plot.Y1.max) == pytest.approx(initial[2:])


@pytest.mark.parametrize("return_to_origin", [False, True])
def test_release_frame_drag_distance_tracks_motion(
    context: dcg.Context, *, return_to_origin: bool
) -> None:
    """Track drag threshold crossings before release, including a return to the start."""
    completed = threading.Event()

    def on_drag(sender: dcg.MouseDragHandler, target: dcg.Window, data) -> None:
        """Record release of a recognized drag."""
        if data.is_released:
            completed.set()

    window = dcg.Window(context, width=400, height=300)
    window.handlers = [dcg.MouseDragHandler(context, callback=on_drag)]
    _render(context, count=3)
    context.inject_mouse_pos(100, 100)
    _render(context)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    context.inject_mouse_pos(150, 100)
    if return_to_origin:
        context.inject_mouse_pos(100, 100)
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)

    expected_x = 0 if return_to_origin else 50
    assert tuple(context.get_mouse_drag_delta(dcg.MouseButton.LEFT)) == pytest.approx(
        (expected_x, 0)
    )
    assert completed.wait(5)
    if return_to_origin:
        assert tuple(context.get_mouse_drag_delta(dcg.MouseButton.LEFT, lock_threshold=51)) == (
            0,
            0,
        )


def test_dragged_handler_reports_release_delta(context: dcg.Context) -> None:
    """Report the final displacement rather than the previous frame's displacement."""
    received = []
    ready = threading.Event()

    def on_dragged(sender: dcg.DraggedHandler, target: dcg.Button, data) -> None:
        """Store the completion callback."""
        received.append((tuple(data.drag_delta), tuple(data.mouse_position)))
        ready.set()

    window = dcg.Window(context, width=500, height=400)
    handler = dcg.DraggedHandler(context, callback=on_dragged)
    button = dcg.Button(context, parent=window, label="drag", width=250, height=150,
                        handlers=[handler])
    _render(context, count=5)
    x, y = button.state.pos_to_viewport
    start = (x + 50, y + 50)
    context.inject_mouse_pos(*start)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    context.inject_mouse_pos(start[0] + 20, start[1])
    _render(context)
    context.inject_mouse_pos(start[0] + 50, start[1] + 10)
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)

    assert ready.wait(5)
    assert received[-1][0] == pytest.approx((50, 10))
    assert received[-1][1] == pytest.approx((start[0] + 50, start[1] + 10))


def test_drawn_dragged_handler_reports_local_release_delta(context: dcg.Context) -> None:
    """Report a transformed drawing button's final delta in local coordinates."""
    window = dcg.Window(context, width=700, height=500)
    plot = dcg.Plot(context, parent=window, width=600, height=400)
    for axis in (plot.X1, plot.Y1):
        axis.no_initial_fit = True
        axis.min = 0
        axis.max = 30
    plot.pan_button = dcg.MouseButton.RIGHT
    drawings = dcg.DrawInPlot(context, parent=plot)
    scale = dcg.DrawingScale(context, parent=drawings, origin=(10, 20), scales=(2, -3))
    received = []
    ready = threading.Event()

    def on_dragged(sender: dcg.DraggedHandler, target: dcg.DrawInvisibleButton, data) -> None:
        """Store the final drag callback."""
        received.append(tuple(data.drag_delta))
        ready.set()

    button = dcg.DrawInvisibleButton(
        context, parent=scale, p1=(1, 2), p2=(3, 4),
        handlers=[dcg.DraggedHandler(context, callback=on_dragged)],
    )
    _render(context, count=5)
    x, y = button.state.pos_to_viewport
    width, height = button.state.rect_size
    start = (x + width / 2, y + height / 2)
    context.inject_mouse_pos(*start)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    context.inject_mouse_pos(start[0] + width / 4, start[1] + height / 4)
    _render(context)
    context.inject_mouse_pos(start[0] + width / 2, start[1] + height / 2)
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)
    assert ready.wait(5)
    assert received[-1] == pytest.approx((1, 1), abs=0.05)


def test_wait_for_input_drains_trickled_events(context: dcg.Context) -> None:
    """Keep requesting logical frames until the ImGui input queue is empty."""
    _render(context, count=5)
    context.viewport.wait_for_input = True
    for i in range(5):
        context.inject_mouse_pos(100 + i * 10, 100)
        context.inject_mouse_wheel(0, 0.25)
    context.viewport.wake(full_refresh=True)

    presented_positions = []
    for _ in range(20):
        if not context.viewport.wait_events(0):
            break
        presented = context.viewport.render_frame()
        presented_positions.append((tuple(context.get_mouse_position()), presented))
    assert tuple(context.get_mouse_position()) == (140, 100)
    assert all(presented for _, presented in presented_positions)
    assert not context.viewport.wait_events(0)
