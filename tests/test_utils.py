"""This test file is meant to test modules provided in dearcygui.utils (except asyncio)"""

import asyncio
import gc
from collections.abc import Generator, Iterator
from concurrent.futures import Executor
from datetime import datetime
from types import SimpleNamespace

import dearcygui as dcg
import numpy as np
import pytest

from dearcygui.utils.handler import (
    add_callbacks_to_handler,
    async_generator_from_handlers,
    auto_cleanup_handler,
    future_from_handlers,
    generator_from_handlers,
)
from dearcygui.utils.image import DrawTiledImage
from dearcygui.utils.window import (
    ItemInspecter,
    MetricsWindow,
    ScrollingBuffer,
    StyleEditor,
    _get_children_recursive as get_children_recursive,
)

from dearcygui.utils.widget import DatePicker, DateTimePicker, TimePicker, DraggableBar


@pytest.fixture
def ctx() -> Generator[dcg.Context, None, None]:
    """Create and clean up a DearCyGui context."""
    context = dcg.Context()
    yield context
    context.queue.shutdown(wait=True)
    context.viewport.destroy()
    gc.collect()

@pytest.fixture
def context() -> Iterator[dcg.Context]:
    """Create a viewport and dispose of its callback queue and resources."""
    ctx = dcg.Context()
    ctx.viewport.initialize(visible=False, width=900, height=700)
    ctx.viewport.vsync = False
    yield ctx
    queue = ctx.queue
    assert isinstance(queue, Executor)
    queue.shutdown(wait=True)
    ctx.viewport.destroy()
    gc.collect()

def _render(ctx: dcg.Context, *, count: int = 1) -> None:
    """Render frames and wait for their callbacks."""
    for _ in range(count):
        ctx.viewport.render_frame()
        ctx.queue.submit(lambda: None).result(timeout=5)

def _coordinates(position: dcg.Coord) -> tuple[float, float]:
    """Return coordinates as a typed pair."""
    return position.x, position.y

def _plot(ctx: dcg.Context) -> dcg.Plot:
    """Create a plot with fixed linear limits and no left-button panning."""
    window = dcg.Window(ctx, width=700, height=500)
    plot = dcg.Plot(ctx, parent=window, width=600, height=400)
    for axis in (plot.X1, plot.Y1):
        axis.no_initial_fit = True
        axis.min = 0
        axis.max = 30
    plot.pan_button = dcg.MouseButton.RIGHT
    return plot


# handler.py



def test_add_callbacks_to_handler_preserves_and_chains_callbacks(
    ctx: dcg.Context,
) -> None:
    """Run the existing callback before all newly-added callbacks."""
    handler = dcg.ClickedHandler(ctx)
    target = dcg.Button(ctx)
    calls: list[tuple[str, object, object, object]] = []
    handler.callback = lambda sender, item, data: calls.append(
        ("existing", sender, item, data)
    )
    add_callbacks_to_handler(
        handler,
        lambda sender, item, data: calls.append(("first", sender, item, data)),
        lambda sender, item, data: calls.append(("second", sender, item, data)),
    )

    handler.callback(handler, target, "payload")

    assert calls == [
        ("existing", handler, target, "payload"),
        ("first", handler, target, "payload"),
        ("second", handler, target, "payload"),
    ]


def test_auto_cleanup_handler_removes_triggered_handler_and_keeps_callback(
    ctx: dcg.Context,
) -> None:
    """Remove a triggered handler after its previous callback runs."""
    handler = dcg.ClickedHandler(ctx)
    target = dcg.Button(ctx)
    calls: list[tuple[object, object, object]] = []
    handler.callback = lambda sender, item, data: calls.append((sender, item, data))
    target.handlers = [handler]

    auto_cleanup_handler(handler)
    handler.callback(handler, target, "payload")

    assert calls == [(handler, target, "payload")]
    assert handler not in target.handlers


def test_auto_cleanup_handler_rejects_non_handler() -> None:
    """Reject values that cannot be used as event handlers."""
    with pytest.raises(TypeError, match="handler must be"):
        auto_cleanup_handler(object())


@pytest.mark.parametrize(("cleanup", "handler_remains"), [(False, True), (True, False)])
def test_future_from_handlers_resolves_once_and_cleans_up_triggered_handler(
    ctx: dcg.Context,
    cleanup: bool,
    handler_remains: bool,
) -> None:
    """Resolve with the first event and honor the cleanup option."""
    first_handler = dcg.ClickedHandler(ctx)
    second_handler = dcg.ClickedHandler(ctx)
    first_target = dcg.Button(ctx)
    second_target = dcg.Button(ctx)
    first_target.handlers = [first_handler]
    second_target.handlers = [second_handler]

    future = future_from_handlers(first_handler, second_handler, cleanup=cleanup)
    first_handler.callback(first_handler, first_target, "first")

    assert future.result() == (first_handler, first_target, "first")
    assert future.done()
    assert (first_handler in first_target.handlers) is handler_remains
    assert second_handler in second_target.handlers


def test_generator_from_handlers_yields_each_callback_event(
    ctx: dcg.Context,
) -> None:
    """Yield every queued event with its handler, target, and data."""
    handler = dcg.ClickedHandler(ctx)
    target = dcg.Button(ctx)
    events = generator_from_handlers(handler)

    handler.callback(handler, target, "first")
    handler.callback(handler, target, "second")

    assert next(events) == (handler, target, "first")
    assert next(events) == (handler, target, "second")
    events.close()


def test_async_generator_from_handlers_yields_callback_event(
    ctx: dcg.Context,
) -> None:
    """Yield callback events through the current asyncio event loop."""
    handler = dcg.ClickedHandler(ctx)
    target = dcg.Button(ctx)

    async def receive_event() -> tuple[dcg.baseHandler, dcg.baseItem, str]:
        events = async_generator_from_handlers(handler)
        next_event = asyncio.create_task(events.__anext__())
        await asyncio.sleep(0)
        handler.callback(handler, target, "payload")
        event = await next_event
        await events.aclose()
        return event

    assert asyncio.run(receive_event()) == (handler, target, "payload")


def test_handler_event_adapters_reject_missing_or_invalid_handlers() -> None:
    """Require at least one valid handler for synchronous adapters."""
    with pytest.raises(ValueError, match="At least one handler"):
        future_from_handlers()
    with pytest.raises(ValueError, match="At least one handler"):
        generator_from_handlers()
    with pytest.raises(TypeError, match="All handlers"):
        future_from_handlers(object())
    with pytest.raises(TypeError, match="All handlers"):
        generator_from_handlers(object())

    async def reject_invalid_async_handlers() -> None:
        with pytest.raises(ValueError, match="At least one handler"):
            await async_generator_from_handlers().__anext__()
        with pytest.raises(TypeError, match="All handlers"):
            await async_generator_from_handlers(object()).__anext__()

    asyncio.run(reject_invalid_async_handlers())


# image.pyx


def test_tiled_image_uses_nested_plot_clip(ctx: dcg.Context) -> None:
    """Cull tiles against the drawing clip after converting to local coordinates."""
    ctx.viewport.initialize(visible=False, width=800, height=600)
    plot = _plot(ctx)
    drawings = dcg.DrawInPlot(ctx, parent=plot)
    scale = dcg.DrawingScale(ctx, parent=drawings, origin=(10, 20), scales=(2, -3))
    clip = dcg.DrawingClip(
        ctx, parent=scale, pmin=(1, 1), pmax=(4, 4), clip_rendering=True
    )
    image = DrawTiledImage(ctx, parent=clip)
    pixels = np.full((2, 2, 4), 255, dtype=np.uint8)
    inside = image.add_tile(pixels, (2, 2), (3, 3))
    outside_clip = image.add_tile(pixels, (5, 2), (6, 3))
    reversed_inside = image.add_tile(pixels, (3, 3), (2, 2))
    hidden = image.add_tile(pixels, (2, 2), (3, 3), visible=False)
    _render(ctx)
    assert image.get_tile_data(inside)["last_frame_count"] > 0
    assert image.get_tile_data(reversed_inside)["last_frame_count"] > 0
    assert image.get_tile_data(outside_clip)["last_frame_count"] == 0
    assert image.get_tile_data(hidden)["last_frame_count"] == 0
    old_frame = image.get_tile_data(inside)["last_frame_count"]
    clip.pmin = (5, 1)
    clip.pmax = (7, 4)
    _render(ctx)
    assert image.get_tile_data(outside_clip)["last_frame_count"] > old_frame
    assert image.get_tile_data(inside)["last_frame_count"] == old_frame


def test_tiled_image_uses_nested_window_clip(ctx: dcg.Context) -> None:
    """Honor nested draw clips outside plots as well."""
    ctx.viewport.initialize(visible=False, width=800, height=600)
    window = dcg.Window(ctx, width=500, height=400)
    drawing = dcg.DrawInWindow(ctx, parent=window, width=300, height=200)
    scale = dcg.DrawingScale(ctx, parent=drawing, origin=(100, 100), scales=(-5, 5))
    clip = dcg.DrawingClip(
        ctx, parent=scale, pmin=(1, 1), pmax=(4, 4), clip_rendering=True, scale_min=-100
    )
    image = DrawTiledImage(ctx, parent=clip)
    pixels = np.full((2, 2, 4), 255, dtype=np.uint8)
    inside = image.add_tile(pixels, (2, 2), (3, 3))
    outside = image.add_tile(pixels, (5, 2), (6, 3))
    _render(ctx)
    assert image.get_tile_data(inside)["last_frame_count"] > 0
    assert image.get_tile_data(outside)["last_frame_count"] == 0


def test_tiled_image_zero_scale_does_not_cull_on_collapsed_axis(ctx: dcg.Context) -> None:
    """Avoid inventing inverse bounds for a collapsed coordinate axis."""
    ctx.viewport.initialize(visible=False, width=800, height=600)
    plot = _plot(ctx)
    drawings = dcg.DrawInPlot(ctx, parent=plot)
    scale = dcg.DrawingScale(ctx, parent=drawings, origin=(10, 10), scales=(0, 1))
    image = DrawTiledImage(ctx, parent=scale)
    pixels = np.full((2, 2, 4), 255, dtype=np.uint8)
    tile = image.add_tile(pixels, (1000, 1), (1001, 2))
    _render(ctx)
    assert image.get_tile_data(tile)["last_frame_count"] > 0


def test_tiled_image_clip_preserves_double_precision(ctx: dcg.Context) -> None:
    """Keep distinct clipping bounds for large, closely spaced coordinates."""
    ctx.viewport.initialize(visible=False, width=800, height=600)
    plot = _plot(ctx)
    plot.X1.min = 1_000_000_000
    plot.X1.max = 1_000_000_020
    drawings = dcg.DrawInPlot(ctx, parent=plot)
    image = DrawTiledImage(ctx, parent=drawings)
    pixels = np.full((2, 2, 4), 255, dtype=np.uint8)
    inside = image.add_tile(pixels, (1_000_000_005, 1), (1_000_000_010, 2))
    outside = image.add_tile(pixels, (1_000_000_040, 1), (1_000_000_045, 2))
    _render(ctx)
    assert image.get_tile_data(inside)["last_frame_count"] > 0
    assert image.get_tile_data(outside)["last_frame_count"] == 0




# widgets.py

def test_datetime_picker_initial_value_syncs_components(ctx: dcg.Context) -> None:
    """Initialize date and time components from one datetime."""
    value = datetime(2024, 3, 10, 15, 42, 17)
    picker = DateTimePicker(ctx, value=value)

    assert picker.value_as_datetime == value
    assert picker.date_picker.value_as_datetime == value
    assert picker.time_picker.value == 15 * 3600 + 42 * 60 + 17


def test_datetime_picker_value_updates_component_values(ctx: dcg.Context) -> None:
    """Update embedded picker values through the composite value setter."""
    picker = DateTimePicker(ctx, value=datetime(2024, 3, 10, 15, 42, 17))
    value = datetime(2025, 6, 12, 9, 8, 7)

    picker.value = value

    assert picker.value_as_datetime == value
    assert picker.date_picker.value_as_datetime == value
    assert picker.time_picker.value == 9 * 3600 + 8 * 60 + 7


def test_time_picker_refreshes_ampm_after_24_hour_edit(ctx: dcg.Context) -> None:
    """Keep the hidden meridiem control synchronized with 24-hour edits."""
    picker = TimePicker(ctx, value=datetime(2024, 3, 10, 15, 42, 17))
    picker.use_24hr = True
    picker._on_hour_change(None, None, SimpleNamespace(value=9))

    picker.use_24hr = False

    assert picker.value_as_datetime.hour == 9
    assert picker._am_pm.value == "AM"
    assert picker._hours.min_value == 1


def test_date_picker_uses_sunday_first_calendar_columns(ctx: dcg.Context) -> None:
    """Place a Sunday-first month's first day in the first calendar column."""
    picker = DatePicker(ctx, value=datetime(2024, 9, 1))
    table = picker._grid.children[0]

    assert table.children[7].label == "1"


def test_date_picker_navigation_stops_at_datetime_limits(ctx: dcg.Context) -> None:
    """Prevent navigation beyond Python's supported date endpoints."""
    picker = DatePicker(
        ctx,
        value=datetime(9999, 12, 31),
        max_date=datetime(9999, 12, 31),
    )

    picker._on_next_click()
    assert (picker._current_year, picker._current_month) == (9999, 11)

    picker._view_level = 2
    picker._on_next_click()
    assert picker._current_year_block == 9980


def test_date_picker_value_setter_accepts_timestamp(ctx: dcg.Context) -> None:
    """Set a date picker from a Unix timestamp."""
    picker = DatePicker(ctx, value=datetime(2024, 3, 10))
    value = datetime(2025, 6, 12, 13, 14, 15)

    picker.value = value.timestamp()

    assert picker.value_as_datetime == value

@pytest.mark.parametrize("vertical", [True, False])
def test_draggable_bar_fast_drag_uses_release_position(
    context: dcg.Context, *, vertical: bool
) -> None:
    """Move a bar even if its first drag update is already outside the grab area."""
    window = dcg.Window(context, width=600, height=400)
    bar = DraggableBar(context, parent=window, vertical=vertical, position=0.3)
    _render(context, count=5)
    center = bar.state.pos_to_viewport + bar.state.rect_size * 0.5
    context.inject_mouse_pos(center.x, center.y)
    _render(context, count=2)
    initial = bar.position
    available = window.state.rect_size - bar.state.rect_size
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    context.inject_mouse_pos(center.x + (80 if vertical else 0), center.y + (0 if vertical else 80))
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context, count=5)

    dimension = available.x if vertical else available.y
    assert bar.position == pytest.approx(initial + 80 / dimension, abs=0.01)
    assert not bar._dragging_in_grab


def test_draggable_bar_invalidation_clears_drag_state(context: dcg.Context) -> None:
    """Restore the initial position on invalidation."""
    window = dcg.Window(context, width=600, height=400)
    bar = DraggableBar(context, parent=window)
    _render(context, count=5)
    center = bar.state.pos_to_viewport + bar.state.rect_size * 0.5
    context.inject_mouse_pos(center.x, center.y)
    _render(context, count=2)
    position = bar.position
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    context.inject_mouse_pos(center.x + 30, center.y)
    _render(context)
    assert bar._dragging_in_grab
    assert bar.position != position

    handler = next(
        handler for handler in bar.handlers if isinstance(handler, dcg.MouseDragHandler)
    )
    bar._on_mouse_drag(
        handler, bar,
        dcg.MouseDragHandlerCallbackValue(
            context, dcg.MouseButton.LEFT, dcg.Coord(30, 0), center,
            is_released=False, is_invalidated=True,
        ),
    )
    assert not bar._dragging_in_grab
    assert bar.position == position
    assert bar._drawing_list.show == bar.state.hovered


def test_draggable_bar_stays_visible_when_drag_leaves_grab(context: dcg.Context) -> None:
    """Keep the bar visible after the first drag update leaves its bounds."""
    window = dcg.Window(context, width=600, height=400)
    bar = DraggableBar(context, parent=window)
    _render(context, count=5)
    center = bar.state.pos_to_viewport + bar.state.rect_size * 0.5
    context.inject_mouse_pos(center.x, center.y)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    context.inject_mouse_pos(center.x + 80, center.y)
    _render(context)
    assert bar._dragging_in_grab
    assert bar._drawing_list.show


@pytest.mark.parametrize("release_while_hidden", [False, True])
def test_draggable_bar_hidden_during_drag_handles_invalidation(
    context: dcg.Context, *, release_while_hidden: bool
) -> None:
    """Reset the bar after its handler misses frames while it is hidden."""
    window = dcg.Window(context, width=600, height=400)
    bar = DraggableBar(context, parent=window)
    _render(context, count=5)
    center = bar.state.pos_to_viewport + bar.state.rect_size * 0.5
    context.inject_mouse_pos(center.x, center.y)
    _render(context, count=2)
    position = bar.position
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    context.inject_mouse_pos(center.x + 30, center.y)
    _render(context)
    assert bar._dragging_in_grab
    assert bar.position != position
    bar.show = False
    _render(context, count=3)
    if release_while_hidden:
        context.inject_mouse_up(dcg.MouseButton.LEFT)
        _render(context)
    bar.show = True
    _render(context, count=3)
    assert not bar._dragging_in_grab
    assert bar.position == position
    if not release_while_hidden:
        context.inject_mouse_up(dcg.MouseButton.LEFT)
        _render(context)

# window.py

def test_scrolling_buffer_returns_requested_recent_values() -> None:
    """Return no more than the requested number of recent values."""
    buffer = ScrollingBuffer(scrolling_size=3, max_size=8)
    buffer.push(1.0)
    buffer.push(2.0)
    buffer.push(3.0)

    assert list(buffer.get()) == [1.0, 2.0, 3.0]
    assert list(buffer.get(2)) == [2.0, 3.0]
    assert list(buffer.get(5)) == [1.0, 2.0, 3.0]


def test_scrolling_buffer_discards_old_values_at_capacity() -> None:
    """Retain the newest values after rotating a full backing store."""
    buffer = ScrollingBuffer(scrolling_size=2, max_size=5)

    for value in range(7):
        buffer.push(float(value))

    assert list(buffer.get()) == [5.0, 6.0]


@pytest.mark.parametrize(
    ("scrolling_size", "max_size"),
    [(0, 5), (2, 0), (2, 4)],
)
def test_scrolling_buffer_rejects_invalid_sizes(
    scrolling_size: int,
    max_size: int,
) -> None:
    """Reject capacities that cannot hold the configured scroll window."""
    with pytest.raises(ValueError, match="max_size"):
        ScrollingBuffer(scrolling_size=scrolling_size, max_size=max_size)


def test_get_children_recursive_uses_depth_first_order(ctx: dcg.Context) -> None:
    """Return the root and nested items in depth-first order."""
    root = dcg.Window(ctx)
    with root:
        child = dcg.HorizontalLayout(ctx)
        with child:
            grandchild = dcg.Text(ctx, value="nested")

    assert get_children_recursive(root) == [root, child, grandchild]


def test_item_inspector_removes_installed_handlers(ctx: dcg.Context) -> None:
    """Install and remove inspection handlers on viewport items."""
    root = dcg.Window(ctx)
    item = dcg.Button(ctx, parent=root)
    inspector = ItemInspecter(ctx)

    inspector.setup_handlers()
    assert inspector._item_handler in item.handlers

    inspector.remove_handlers()

    assert inspector._item_handler not in item.handlers
    assert inspector._inspected_items == []



@pytest.mark.parametrize("fast", [False, True])
def test_item_inspector_drag_tracks_original_item_after_hover_loss(
    context: dcg.Context, *, fast: bool
) -> None:
    """Move a non-activatable item through release even after the pointer leaves it."""
    window = dcg.Window(context, width=550, height=400, x=10, y=10)
    item = dcg.Text(context, parent=window, value="Move this text")
    inspector = ItemInspecter(context, x=600, y=10)
    inspector.setup_handlers()
    _render(context, count=5)
    initial = item.state.pos_to_viewport
    start = initial + item.state.rect_size * 0.5
    context.inject_mouse_pos(start.x, start.y)
    _render(context, count=2)
    context.inject_key_down(dcg.Key.LEFTALT)
    _render(context)
    context.inject_mouse_down(dcg.MouseButton.RIGHT)
    if not fast:
        _render(context)
    context.inject_mouse_pos(start.x + 100, start.y + 60)
    if not fast:
        _render(context)
    context.inject_mouse_pos(start.x + 140, start.y + 80)
    context.inject_mouse_up(dcg.MouseButton.RIGHT)
    _render(context, count=6)

    assert _coordinates(item.state.pos_to_viewport) == pytest.approx(
        (initial.x + 140, initial.y + 80), abs=2
    )
    assert inspector._dragging_item is None
    inspector.remove_handlers()


def test_item_inspector_removal_clears_selected_drag(context: dcg.Context) -> None:
    """Detach viewport tracking and retain the last requested position on removal."""
    window = dcg.Window(context, width=550, height=400, x=10, y=10)
    item = dcg.Text(context, parent=window, value="Move this text")
    inspector = ItemInspecter(context, x=600, y=10)
    inspector.setup_handlers()
    _render(context, count=5)
    initial = item.state.pos_to_viewport
    start = initial + item.state.rect_size * 0.5
    context.inject_mouse_pos(start.x, start.y)
    _render(context, count=2)
    context.inject_key_down(dcg.Key.LEFTALT)
    _render(context)
    context.inject_mouse_down(dcg.MouseButton.RIGHT)
    _render(context)
    context.inject_mouse_pos(start.x + 80, start.y + 40)
    _render(context)
    assert inspector._dragging_item is item
    inspector.remove_handlers()
    _render(context, count=2)

    assert inspector._dragging_item is None
    assert inspector._drag_tracker not in context.viewport.handlers
    assert _coordinates(item.state.pos_to_viewport) == pytest.approx(
        (initial.x + 80, initial.y + 40), abs=2
    )


@pytest.mark.parametrize("hide_item", [False, True])
def test_item_inspector_invalidates_drag_and_restores_position(
    context: dcg.Context, *, hide_item: bool
) -> None:
    """Restore the original position after invalidation, even for a hidden item."""
    window = dcg.Window(context, width=550, height=400, x=10, y=10)
    item = dcg.Text(context, parent=window, value="Move this text")
    inspector = ItemInspecter(context, x=600, y=10)
    inspector.setup_handlers()
    _render(context, count=5)
    initial = item.state.pos_to_viewport
    start = initial + item.state.rect_size * 0.5
    context.inject_mouse_pos(start.x, start.y)
    _render(context, count=2)
    context.inject_key_down(dcg.Key.LEFTALT)
    _render(context)
    context.inject_mouse_down(dcg.MouseButton.RIGHT)
    _render(context)
    context.inject_mouse_pos(start.x + 80, start.y + 40)
    _render(context)
    assert inspector._dragging_item is item
    _render(context)
    assert _coordinates(item.state.pos_to_viewport) == pytest.approx(
        (initial.x + 80, initial.y + 40), abs=2
    )
    if hide_item:
        item.show = False
        _render(context)

    tracker = next(
        handler for handler in inspector._drag_tracker.children
        if isinstance(handler, dcg.MouseDragHandler)
    )
    tracker.threshold = 1000
    _render(context, count=2)
    assert inspector._dragging_item is None
    if hide_item:
        item.show = True
        _render(context, count=2)
    assert _coordinates(item.state.pos_to_viewport) == pytest.approx(
        _coordinates(initial), abs=2
    )
    context.inject_mouse_up(dcg.MouseButton.RIGHT)
    _render(context)
    inspector.remove_handlers()


def test_item_inspector_drag_finishes_while_target_is_hidden(context: dcg.Context) -> None:
    """Track a drag on the viewport even while the target is no longer traversed."""
    window = dcg.Window(context, width=550, height=400, x=10, y=10)
    item = dcg.Text(context, parent=window, value="Move this text")
    inspector = ItemInspecter(context, x=600, y=10)
    inspector.setup_handlers()
    _render(context, count=5)
    initial = item.state.pos_to_viewport
    start = initial + item.state.rect_size * 0.5
    context.inject_mouse_pos(start.x, start.y)
    _render(context, count=2)
    context.inject_key_down(dcg.Key.LEFTALT)
    _render(context)
    context.inject_mouse_down(dcg.MouseButton.RIGHT)
    _render(context)
    context.inject_mouse_pos(start.x + 40, start.y + 20)
    _render(context)
    item.show = False
    _render(context, count=2)
    context.inject_mouse_pos(start.x + 100, start.y + 60)
    context.inject_mouse_up(dcg.MouseButton.RIGHT)
    _render(context, count=3)
    item.show = True
    _render(context, count=3)

    assert inspector._dragging_item is None
    assert _coordinates(item.state.pos_to_viewport) == pytest.approx(
        (initial.x + 100, initial.y + 60), abs=2
    )
    inspector.remove_handlers()


def test_item_inspector_requires_alt_and_clears_plain_click(context: dcg.Context) -> None:
    """Do not move without Alt, and discard an Alt-click that does not drag."""
    window = dcg.Window(context, width=550, height=400, x=10, y=10)
    item = dcg.Text(context, parent=window, value="Move this text")
    inspector = ItemInspecter(context, x=600, y=10)
    inspector.setup_handlers()
    _render(context, count=5)
    initial = item.state.pos_to_viewport
    start = initial + item.state.rect_size * 0.5
    context.inject_mouse_pos(start.x, start.y)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.RIGHT)
    _render(context)
    context.inject_mouse_pos(start.x + 80, start.y + 40)
    context.inject_mouse_up(dcg.MouseButton.RIGHT)
    _render(context, count=3)
    assert _coordinates(item.state.pos_to_viewport) == pytest.approx(_coordinates(initial))
    assert inspector._dragging_item is None

    context.inject_mouse_pos(start.x, start.y)
    _render(context, count=2)
    context.inject_key_down(dcg.Key.LEFTALT)
    _render(context)
    context.inject_mouse_down(dcg.MouseButton.RIGHT)
    _render(context)
    assert inspector._dragging_item is item
    context.inject_mouse_up(dcg.MouseButton.RIGHT)
    _render(context)
    assert inspector._dragging_item is None
    inspector.remove_handlers()


def test_style_editor_resets_and_exports_default_theme(ctx: dcg.Context) -> None:
    """Reset style controls and produce a valid empty-theme export."""
    editor = StyleEditor(ctx)

    editor.reset_values()

    assert editor.export_to_text() == "theme = None"
