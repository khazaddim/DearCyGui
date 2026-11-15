"""Exercise mouse input spanning slow or on-demand frames."""

import gc
import os
import shutil
import subprocess
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


@pytest.mark.parametrize("button", list(dcg.MouseButton))
@pytest.mark.parametrize("drawn", [False, True])
def test_item_click_masks_preserve_views_and_snapshots(
    context: dcg.Context, *, button: dcg.MouseButton, drawn: bool
) -> None:
    """Keep button-specific clicks and double clicks in live and copied states."""
    clicks: list[dcg.MouseButton] = []
    doubles: list[dcg.MouseButton] = []

    def on_click(
        sender: dcg.ClickedHandler,
        target: dcg.Button | dcg.DrawInvisibleButton,
        data: dcg.ClickedHandlerCallbackValue,
    ) -> None:
        """Record the button reported by the click handler."""
        clicks.append(data.button)

    def on_double(
        sender: dcg.DoubleClickedHandler,
        target: dcg.Button | dcg.DrawInvisibleButton,
        data: dcg.DoubleClickedHandlerCallbackValue,
    ) -> None:
        """Record the button reported by the double-click handler."""
        doubles.append(data.button)

    handlers = [
        dcg.ClickedHandler(context, button=button, callback=on_click),
        dcg.DoubleClickedHandler(context, button=button, callback=on_double),
    ]
    window = dcg.Window(context, width=500, height=400)
    if drawn:
        drawing = dcg.DrawInWindow(context, parent=window, width=250, height=150)
        item = dcg.DrawInvisibleButton(context, parent=drawing, p1=(0, 0), p2=(200, 100),
                                       handlers=handlers)
    else:
        item = dcg.Button(context, parent=window, label="click", width=250, height=150,
                          handlers=handlers)
    _render(context, count=5)
    x, y = item.state.pos_to_viewport
    context.inject_mouse_pos(x + 30, y + 30)
    _render(context, count=2)
    assert item.state.hovered

    context.inject_mouse_down(button)
    _render(context)
    first = item.state.snapshot()
    expected = tuple(i == button.value for i in range(5))
    assert item.state.clicked == expected
    assert first.clicked == expected
    assert item.state.double_clicked == [False] * 5
    assert all(type(value) is bool for value in item.state.clicked)
    assert all(type(value) is bool for value in item.state.double_clicked)

    context.inject_mouse_up(button)
    _render(context)
    assert item.state.clicked == (False,) * 5
    context.inject_mouse_down(button)
    _render(context)
    second = item.state.snapshot()
    assert item.state.clicked == expected
    assert item.state.double_clicked == list(expected)
    assert second.double_clicked == list(expected)
    assert first.double_clicked == [False] * 5

    context.inject_mouse_up(button)
    _render(context)
    context.queue.submit(lambda: None).result(timeout=5)
    assert clicks == [button, button]
    assert doubles == [button]
    assert first.clicked == expected
    assert second.double_clicked == list(expected)

    item.show = False
    _render(context)
    assert item.state.clicked == (False,) * 5
    assert item.state.double_clicked == [False] * 5


@pytest.mark.parametrize("button", list(dcg.MouseButton))
@pytest.mark.parametrize("activatable", [False, True])
def test_item_drag_masks_preserve_button_specific_release(
    context: dcg.Context, *, button: dcg.MouseButton, activatable: bool
) -> None:
    """Retain per-button dragging for activatable and non-activatable items."""
    ongoing: list[tuple[float, float]] = []
    completed: list[tuple[float, float]] = []

    def on_dragging(
        sender: dcg.DraggingHandler,
        target: dcg.Button | dcg.ProgressBar,
        data: dcg.DraggingHandlerCallbackValue,
    ) -> None:
        """Record the ongoing displacement."""
        ongoing.append((data.drag_delta.x, data.drag_delta.y))

    def on_dragged(
        sender: dcg.DraggedHandler,
        target: dcg.Button | dcg.ProgressBar,
        data: dcg.DraggedHandlerCallbackValue,
    ) -> None:
        """Record the final displacement."""
        completed.append((data.drag_delta.x, data.drag_delta.y))

    window = dcg.Window(context, width=500, height=400)
    handlers = [
        dcg.DraggingHandler(context, button=button, callback=on_dragging),
        dcg.DraggedHandler(context, button=button, callback=on_dragged),
    ]
    if activatable:
        item = dcg.Button(context, parent=window, label="drag", width=250, height=150,
                          handlers=handlers)
    else:
        item = dcg.ProgressBar(context, parent=window, width=250, height=150,
                               handlers=handlers)
    _render(context, count=5)
    x, y = item.state.pos_to_viewport
    start = (x + 30, y + 30)
    context.inject_mouse_pos(*start)
    _render(context, count=2)
    context.inject_mouse_down(button)
    _render(context)
    context.inject_mouse_pos(start[0] + 20, start[1] + 10)
    _render(context)
    context.inject_mouse_pos(start[0] + 40, start[1] + 20)
    _render(context)
    context.inject_mouse_up(button)
    _render(context)
    context.queue.submit(lambda: None).result(timeout=5)
    assert ongoing[-1] == pytest.approx((40, 20))
    assert completed == [pytest.approx((40, 20))]


def test_item_drag_masks_preserve_simultaneous_buttons(context: dcg.Context) -> None:
    """Keep simultaneous drags separate when one button stops before the other."""
    completed: list[tuple[dcg.MouseButton, tuple[float, float]]] = []

    def on_dragged(
        sender: dcg.DraggedHandler,
        target: dcg.Button,
        data: dcg.DraggedHandlerCallbackValue,
    ) -> None:
        """Record the button and final displacement."""
        completed.append((data.button, (data.drag_delta.x, data.drag_delta.y)))

    window = dcg.Window(context, width=500, height=400)
    item = dcg.Button(
        context, parent=window, label="drag", width=250, height=150,
        handlers=[
            dcg.DraggedHandler(context, button=button, callback=on_dragged)
            for button in (dcg.MouseButton.X1, dcg.MouseButton.X2)
        ],
    )
    _render(context, count=5)
    x, y = item.state.pos_to_viewport
    start = (x + 30, y + 30)
    context.inject_mouse_pos(*start)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.X1)
    context.inject_mouse_down(dcg.MouseButton.X2)
    _render(context)
    assert item.state.clicked == (False, False, False, True, True)

    context.inject_mouse_pos(start[0] + 20, start[1] + 10)
    _render(context)
    context.inject_mouse_up(dcg.MouseButton.X1)
    _render(context)
    context.inject_mouse_pos(start[0] + 40, start[1] + 20)
    _render(context)
    context.inject_mouse_up(dcg.MouseButton.X2)
    _render(context)
    context.queue.submit(lambda: None).result(timeout=5)
    assert len(completed) == 2
    assert completed[0][0] == dcg.MouseButton.X1
    assert completed[0][1] == pytest.approx((20, 10))
    assert completed[1][0] == dcg.MouseButton.X2
    assert completed[1][1] == pytest.approx((40, 20))


def test_item_drag_mask_preserves_delta_when_mouse_position_is_invalid(
    context: dcg.Context,
) -> None:
    """Keep the last delta when the mouse position is lost on the release frame."""
    completed: list[tuple[float, float]] = []

    def on_dragged(
        sender: dcg.DraggedHandler,
        target: dcg.ProgressBar,
        data: dcg.DraggedHandlerCallbackValue,
    ) -> None:
        """Record the final displacement."""
        completed.append((data.drag_delta.x, data.drag_delta.y))

    window = dcg.Window(context, width=500, height=400)
    item = dcg.ProgressBar(
        context, parent=window, width=250, height=150,
        handlers=[dcg.DraggedHandler(context, callback=on_dragged)],
    )
    _render(context, count=5)
    x, y = item.state.pos_to_viewport
    start = (x + 30, y + 30)
    context.inject_mouse_pos(*start)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    context.inject_mouse_pos(start[0] + 20, start[1] + 10)
    _render(context)
    context.inject_mouse_pos(-1e30, -1e30)
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)
    context.queue.submit(lambda: None).result(timeout=5)
    assert completed == [pytest.approx((20, 10))]


def test_plot_axis_click_mask_preserves_axis_state(context: dcg.Context) -> None:
    """Capture click state for the hovered plot axis and its handler."""
    received: list[dcg.MouseButton] = []

    def on_click(
        sender: dcg.ClickedHandler,
        target: dcg.PlotAxisConfig,
        data: dcg.ClickedHandlerCallbackValue,
    ) -> None:
        """Record the axis click."""
        received.append(data.button)

    window = dcg.Window(context, width=700, height=500)
    plot = dcg.Plot(context, parent=window, width=600, height=400)
    plot.X1.handlers = [dcg.ClickedHandler(context, callback=on_click)]
    _render(context, count=5)
    x, y = plot.state.pos_to_viewport
    width, height = plot.state.rect_size
    context.inject_mouse_pos(x + width / 2, y + height - 10)
    _render(context, count=2)
    assert plot.X1.state.hovered
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    snapshot = plot.X1.state.snapshot()
    context.queue.submit(lambda: None).result(timeout=5)
    assert plot.X1.state.clicked == (True, False, False, False, False)
    assert snapshot.clicked == (True, False, False, False, False)
    assert received == [dcg.MouseButton.LEFT]
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)


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


def test_mouse_drag_handler_drag_queued_between_frames(context: dcg.Context) -> None:
    """Deliver one release callback for a complete drag queued between frames."""
    received: list[tuple[bool, tuple[float, float], tuple[float, float], tuple[float, float]]] = []

    def on_drag(
        sender: dcg.MouseDragHandler,
        target: dcg.Window,
        data: dcg.MouseDragHandlerCallbackValue,
    ) -> None:
        """Record the drag state and both mouse positions."""
        received.append(
            (data.is_released, tuple(data.drag_delta), tuple(data.click_position),
             tuple(data.mouse_position))
        )

    window = dcg.Window(context, width=400, height=300)
    window.handlers = [dcg.MouseDragHandler(context, callback=on_drag)]
    _render(context, count=3)
    context.inject_mouse_pos(100, 100)
    _render(context)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    context.inject_mouse_pos(150, 120)
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    context.inject_mouse_pos(200, 150)
    _render(context, count=5)

    context.queue.submit(lambda: None).result(timeout=5)
    assert len(received) == 1
    released, delta, click, position = received[0]
    assert released
    assert delta == pytest.approx((50, 20))
    assert click == pytest.approx((100, 100))
    assert position == pytest.approx((150, 120))


def test_mouse_drag_callback_constructor_preserves_release_compatibility(
    context: dcg.Context,
) -> None:
    """Keep the original constructor and expose cancellation separately."""
    delta = dcg.Coord(20, 10)
    click = dcg.Coord(100, 100)
    released = dcg.MouseDragHandlerCallbackValue(
        context, dcg.MouseButton.LEFT, delta, click, is_released=True, is_invalidated=False
    )
    invalidated = dcg.MouseDragHandlerCallbackValue(
        context, dcg.MouseButton.LEFT, delta, click, is_released=False, is_invalidated=True
    )
    assert released.is_released and not released.is_invalidated
    assert invalidated.is_invalidated and not invalidated.is_released


def test_mouse_move_handler_ignores_invalid_previous_position(context: dcg.Context) -> None:
    """Do not report movement from an unavailable mouse position."""
    received: list[tuple[tuple[float, float], tuple[float, float]]] = []

    def on_move(sender: dcg.MouseMoveHandler, target: dcg.Window, data) -> None:
        """Record both positions from a move callback."""
        received.append((tuple(data.previous_position), tuple(data.current_position)))

    window = dcg.Window(context, width=400, height=300)
    window.handlers = [dcg.MouseMoveHandler(context, callback=on_move)]
    _render(context, count=3)
    context.inject_mouse_pos(-1e30, -1e30)
    _render(context)
    context.queue.submit(lambda: None).result(timeout=5)
    received.clear()
    context.inject_mouse_pos(100, 100)
    _render(context)
    context.queue.submit(lambda: None).result(timeout=5)
    assert received == []
    context.inject_mouse_pos(110, 120)
    _render(context)
    context.queue.submit(lambda: None).result(timeout=5)
    assert received == [((100, 100), (110, 120))]


def test_mouse_over_handlers_track_unavailable_position(context: dcg.Context) -> None:
    """Report entry and exit when the mouse becomes available or unavailable."""
    events: list[str] = []

    def on_enter(sender: dcg.GotMouseOverHandler, target: dcg.Window) -> None:
        """Record entry into the window rectangle."""
        events.append("enter")

    def on_leave(sender: dcg.LostMouseOverHandler, target: dcg.Window) -> None:
        """Record exit from the window rectangle."""
        events.append("leave")

    window = dcg.Window(context, width=400, height=300)
    window.handlers = [
        dcg.GotMouseOverHandler(context, callback=on_enter),
        dcg.LostMouseOverHandler(context, callback=on_leave),
    ]
    _render(context, count=3)
    context.inject_mouse_pos(-300000, -300000)
    _render(context)
    context.queue.submit(lambda: None).result(timeout=5)
    events.clear()
    x, y = window.state.pos_to_viewport
    context.inject_mouse_pos(x + 50, y + 50)
    _render(context)
    context.inject_mouse_pos(-300000, -300000)
    _render(context)
    context.queue.submit(lambda: None).result(timeout=5)
    assert events == ["enter", "leave"]


@pytest.mark.parametrize("release_while_hidden", [False, True])
def test_mouse_drag_handler_cancels_after_shared_targets_are_hidden(
    context: dcg.Context, *, release_while_hidden: bool
) -> None:
    """Cancel once per target after a shared handler misses rendering frames."""
    received: list[tuple[dcg.Window, bool, bool, tuple[float, float]]] = []

    def on_drag(sender: dcg.MouseDragHandler, target: dcg.Window, data) -> None:
        """Record target, ending reason, and drag displacement."""
        received.append((target, data.is_released, data.is_invalidated, tuple(data.drag_delta)))

    handler = dcg.MouseDragHandler(context, callback=on_drag)
    first = dcg.Window(context, width=400, height=300, handlers=[handler])
    second = dcg.Window(context, width=400, height=300, handlers=[handler])
    _render(context, count=3)
    context.inject_mouse_pos(100, 100)
    _render(context)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    context.inject_mouse_pos(150, 120)
    _render(context)
    context.queue.submit(lambda: None).result(timeout=5)
    assert len(received) == 2
    assert all(not released and not invalidated for _, released, invalidated, _ in received)
    first.show = False
    second.show = False
    _render(context, count=3)
    if release_while_hidden:
        context.inject_mouse_up(dcg.MouseButton.LEFT)
        _render(context, count=2)
    first.show = True
    second.show = True
    _render(context, count=3)
    if not release_while_hidden:
        context.inject_mouse_up(dcg.MouseButton.LEFT)
        _render(context, count=2)
    context.queue.submit(lambda: None).result(timeout=5)
    endings = [(target, released, invalidated, delta) for target, released, invalidated, delta
               in received if released or invalidated]
    assert len(endings) == 2
    assert {target for target, _, _, _ in endings} == {first, second}
    assert all(not released and invalidated and delta == (50, 20)
               for _, released, invalidated, delta in endings)


def test_mouse_drag_handler_button_change_invalidates_and_blocks_held_gesture(
    context: dcg.Context,
) -> None:
    """Invalidate the old button and wait for the newly selected button to be released."""
    received: list[tuple[dcg.MouseButton, bool, bool, tuple[float, float]]] = []

    def on_drag(
        sender: dcg.MouseDragHandler,
        target: dcg.Window,
        data: dcg.MouseDragHandlerCallbackValue,
    ) -> None:
        """Record the button and drag event."""
        received.append(
            (data.button, data.is_released, data.is_invalidated, tuple(data.drag_delta))
        )

    handler = dcg.MouseDragHandler(context, callback=on_drag)
    window = dcg.Window(context, width=400, height=300, handlers=[handler])
    _render(context, count=3)
    context.inject_mouse_pos(100, 100)
    _render(context)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    context.inject_mouse_pos(150, 120)
    _render(context)
    context.inject_mouse_down(dcg.MouseButton.RIGHT)
    _render(context)
    context.queue.submit(lambda: None).result(timeout=5)
    received.clear()

    handler.button = dcg.MouseButton.RIGHT
    _render(context)
    context.inject_mouse_pos(200, 140)
    _render(context, count=2)
    context.queue.submit(lambda: None).result(timeout=5)
    assert received == [(dcg.MouseButton.LEFT, False, True, (50, 20))]

    context.inject_mouse_up(dcg.MouseButton.RIGHT)
    _render(context, count=2)
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)
    context.inject_mouse_down(dcg.MouseButton.RIGHT)
    _render(context)
    context.inject_mouse_pos(230, 160)
    _render(context)
    context.inject_mouse_up(dcg.MouseButton.RIGHT)
    _render(context)
    context.queue.submit(lambda: None).result(timeout=5)
    assert received[1:] == [
        (dcg.MouseButton.RIGHT, False, False, (30, 20)),
        (dcg.MouseButton.RIGHT, True, False, (30, 20)),
    ]


@pytest.mark.parametrize("release_immediately", [False, True])
def test_mouse_drag_handler_threshold_change_after_drag(
    context: dcg.Context, *, release_immediately: bool
) -> None:
    """Preserve the release delta or invalidate when a raised threshold stops the drag."""
    received: list[tuple[bool, bool, tuple[float, float]]] = []

    def on_drag(
        sender: dcg.MouseDragHandler,
        target: dcg.Window,
        data: dcg.MouseDragHandlerCallbackValue,
    ) -> None:
        """Record drag events and displacement."""
        received.append((data.is_released, data.is_invalidated, tuple(data.drag_delta)))

    handler = dcg.MouseDragHandler(context, callback=on_drag)
    window = dcg.Window(context, width=400, height=300, handlers=[handler])
    _render(context, count=3)
    context.inject_mouse_pos(100, 100)
    _render(context)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    context.inject_mouse_pos(150, 100)
    _render(context)
    context.queue.submit(lambda: None).result(timeout=5)
    assert received == [(False, False, (50, 0))]
    received.clear()

    handler.threshold = 100
    if release_immediately:
        context.inject_mouse_pos(160, 100)
        context.inject_mouse_up(dcg.MouseButton.LEFT)
        _render(context)
        context.queue.submit(lambda: None).result(timeout=5)
        assert received == [(True, False, (60, 0))]
    else:
        _render(context)
        context.inject_mouse_pos(250, 100)
        _render(context, count=2)
        context.inject_mouse_up(dcg.MouseButton.LEFT)
        _render(context, count=2)
        context.queue.submit(lambda: None).result(timeout=5)
        assert received == [(False, True, (50, 0))]


def test_mouse_drag_handler_uses_last_position_if_release_is_invalid(context: dcg.Context) -> None:
    """End a drag with the last reported position when the mouse disappears."""
    received: list[tuple[bool, bool, tuple[float, float], tuple[float, float]]] = []

    def on_drag(sender: dcg.MouseDragHandler, target: dcg.Window, data) -> None:
        """Record the drag state and position."""
        received.append(
            (data.is_released, data.is_invalidated, tuple(data.drag_delta),
             tuple(data.mouse_position))
        )

    window = dcg.Window(context, width=400, height=300)
    window.handlers = [dcg.MouseDragHandler(context, callback=on_drag)]
    _render(context, count=3)
    context.inject_mouse_pos(100, 100)
    _render(context)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    context.inject_mouse_pos(150, 120)
    _render(context)
    context.inject_mouse_pos(-300000, -300000)
    _render(context)
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context, count=2)
    context.queue.submit(lambda: None).result(timeout=5)

    endings = [entry for entry in received if entry[0] or entry[1]]
    assert endings == [(True, False, (50, 20), (150, 120))]
    assert all(delta == (50, 20) and pos == (150, 120)
               for _, _, delta, pos in received)


def test_mouse_drag_handler_ignores_invalid_click_origin(context: dcg.Context) -> None:
    """Do not treat a press at an unavailable position as an enormous drag."""
    received: list[object] = []

    def on_drag(sender: dcg.MouseDragHandler, target: dcg.Window, data) -> None:
        """Record unexpected callbacks."""
        received.append(data)

    window = dcg.Window(context, width=400, height=300)
    window.handlers = [dcg.MouseDragHandler(context, callback=on_drag)]
    _render(context, count=3)
    context.inject_mouse_pos(-300000, -300000)
    _render(context)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    context.inject_mouse_pos(150, 120)
    _render(context)
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)
    context.queue.submit(lambda: None).result(timeout=5)
    assert received == []


def test_drag_drop_source_skips_unavailable_mouse_position(context: dcg.Context) -> None:
    """Do not publish an invalid position for an external drag source."""
    received: list[tuple[float, float]] = []

    def on_drag_source(sender: dcg.DragDropSourceHandler, target: dcg.Window, data) -> None:
        """Record source positions."""
        received.append(tuple(data.mouse_position))

    window = dcg.Window(context, width=400, height=300)
    window.handlers = [dcg.DragDropSourceHandler(context, callback=on_drag_source)]
    context.inject_mouse_pos(100, 100)
    _render(context, count=3)
    context.queue.submit(lambda: None).result(timeout=5)
    assert received
    received.clear()
    context.inject_mouse_pos(-300000, -300000)
    _render(context, count=2)
    context.queue.submit(lambda: None).result(timeout=5)
    assert received == []
    context.inject_mouse_pos(120, 110)
    _render(context, count=2)
    context.queue.submit(lambda: None).result(timeout=5)
    assert received and received[-1] == (120, 110)


@pytest.mark.skipif(
    os.environ.get("DCG_TEST_X11_FOCUS") != "1"
    or shutil.which("xdotool") is None
    or shutil.which("xwininfo") is None,
    reason="Requires an isolated X11 display, xdotool, and xwininfo",
)
def test_mouse_drag_handler_cancels_on_window_focus_loss() -> None:
    """Deliver one cancellation after the operating system moves window focus."""
    first = dcg.Context()
    second = dcg.Context()
    received: list[tuple[bool, bool, tuple[float, float]]] = []

    def on_drag(sender: dcg.MouseDragHandler, target: dcg.Window, data) -> None:
        """Record the drag ending and its last known displacement."""
        received.append((data.is_released, data.is_invalidated, tuple(data.drag_delta)))

    try:
        first_title = f"dcg-focus-first-{os.getpid()}"
        second_title = f"dcg-focus-second-{os.getpid()}"
        first.viewport.initialize(title=first_title, visible=True, width=500, height=400)
        second.viewport.initialize(title=second_title, visible=True, width=500, height=400)
        first.viewport.vsync = False
        window = dcg.Window(first, width=400, height=300)
        window.handlers = [dcg.MouseDragHandler(first, callback=on_drag)]
        _render(first, count=3)

        def focus(title: str) -> None:
            """Set X11 input focus to the uniquely named viewport."""
            info = subprocess.check_output(["xwininfo", "-name", title], text=True)
            window_id = next(line.split()[3] for line in info.splitlines()
                             if "Window id:" in line)
            subprocess.run(["xdotool", "windowfocus", "--sync", window_id], check=True)

        focus(first_title)
        _render(first, count=2)
        first.inject_mouse_pos(100, 100)
        _render(first)
        first.inject_mouse_down(dcg.MouseButton.LEFT)
        _render(first)
        first.inject_mouse_pos(150, 120)
        _render(first)
        first.queue.submit(lambda: None).result(timeout=5)
        assert received and received[-1] == (False, False, (50, 20))
        focus(second_title)
        _render(first, count=3)
        first.queue.submit(lambda: None).result(timeout=5)
        assert [event for event in received if event[0] or event[1]] == [
            (False, True, (50, 20))
        ]
    finally:
        first.queue.shutdown(wait=True)
        second.queue.shutdown(wait=True)
        first.viewport.destroy()
        second.viewport.destroy()
        gc.collect()


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


def test_drawn_drag_survives_unavailable_mouse_position(context: dcg.Context) -> None:
    """Keep the last local delta and screen position when the mouse disappears."""
    window = dcg.Window(context, width=700, height=500)
    plot = dcg.Plot(context, parent=window, width=600, height=400)
    for axis in (plot.X1, plot.Y1):
        axis.no_initial_fit = True
        axis.min = 0
        axis.max = 30
    plot.pan_button = dcg.MouseButton.RIGHT
    drawings = dcg.DrawInPlot(context, parent=plot)
    scale = dcg.DrawingScale(context, parent=drawings, origin=(10, 20), scales=(2, -3))
    received: list[tuple[tuple[float, float], tuple[float, float]]] = []

    def on_dragged(sender: dcg.DraggedHandler, target: dcg.DrawInvisibleButton, data) -> None:
        """Record the final local delta and screen position."""
        received.append((tuple(data.drag_delta), tuple(data.mouse_position)))

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
    moved = (start[0] + width / 4, start[1] + height / 4)
    context.inject_mouse_pos(*moved)
    _render(context)
    context.inject_mouse_pos(-1e30, -1e30)
    _render(context)
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)
    context.queue.submit(lambda: None).result(timeout=5)

    assert len(received) == 1
    assert received[0][0] == pytest.approx((0.5, 0.5), abs=0.05)
    assert received[0][1] == pytest.approx(moved, abs=1)


@pytest.mark.parametrize("release_with_transform_change", [False, True])
def test_drawn_drag_uses_last_position_with_changed_transform(
    context: dcg.Context, *, release_with_transform_change: bool
) -> None:
    """Convert the last valid mouse position with the current drawing transform."""
    window = dcg.Window(context, width=700, height=500)
    plot = dcg.Plot(context, parent=window, width=600, height=400)
    for axis in (plot.X1, plot.Y1):
        axis.no_initial_fit = True
        axis.min = 0
        axis.max = 30
    plot.pan_button = dcg.MouseButton.RIGHT
    drawings = dcg.DrawInPlot(context, parent=plot)
    scale = dcg.DrawingScale(context, parent=drawings, origin=(10, 20), scales=(2, -3))
    dragging: list[tuple[float, float]] = []
    dragged: list[tuple[float, float]] = []

    def on_dragging(
        sender: dcg.DraggingHandler,
        target: dcg.DrawInvisibleButton,
        data: dcg.DraggingHandlerCallbackValue,
    ) -> None:
        """Record ongoing drag deltas."""
        dragging.append(tuple(data.drag_delta))

    def on_dragged(
        sender: dcg.DraggedHandler,
        target: dcg.DrawInvisibleButton,
        data: dcg.DraggedHandlerCallbackValue,
    ) -> None:
        """Record completed drag deltas."""
        dragged.append(tuple(data.drag_delta))

    button = dcg.DrawInvisibleButton(
        context, parent=scale, p1=(1, 2), p2=(3, 4),
        handlers=[
            dcg.DraggingHandler(context, callback=on_dragging),
            dcg.DraggedHandler(context, callback=on_dragged),
        ],
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
    context.inject_mouse_pos(-1e30, -1e30)
    _render(context)

    scale.origin = (12, 20)
    if release_with_transform_change:
        context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)
    context.queue.submit(lambda: None).result(timeout=5)
    if release_with_transform_change:
        assert len(dragged) == 1
        assert dragged[-1] == pytest.approx((-0.5, 0.5), abs=0.05)
    else:
        assert dragging[-1] == pytest.approx((-0.5, 0.5), abs=0.05)
        context.inject_mouse_up(dcg.MouseButton.LEFT)
        _render(context)
        context.queue.submit(lambda: None).result(timeout=5)
        assert dragged[-1] == pytest.approx((-0.5, 0.5), abs=0.05)


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
