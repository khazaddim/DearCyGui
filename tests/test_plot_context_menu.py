import gc
import threading
import time
import weakref

import dearcygui as dcg
import numpy as np
import pytest


def render(context, count=1):
    for _ in range(count):
        context.viewport.render_frame()


def click(context, x, y, button):
    context.inject_mouse_pos(x, y)
    render(context, 2)
    context.inject_mouse_down(button)
    render(context)
    context.inject_mouse_up(button)
    render(context, 5)


def open_plot_menu(context, plot, button=dcg.MouseButton.RIGHT):
    x, y = plot.state.content_pos
    width, height = plot.state.content_region_avail
    click(context, x + width * 0.6, y + height * 0.4, button)


def click_item(context, item):
    assert item.state.visible
    x, y = item.state.pos_to_viewport
    width, height = item.state.rect_size
    assert width > 0 and height > 0
    click(context, x + min(width / 2, 30), y + height / 2, dcg.MouseButton.LEFT)


def open_submenu(context, menu, child):
    assert menu.state.visible
    x, y = menu.state.pos_to_viewport
    width, height = menu.state.rect_size
    context.inject_mouse_pos(x + min(width / 2, 30), y + height / 2)
    for _ in range(60):
        render(context)
        if child.state.visible:
            return
        time.sleep(0.01)
    pytest.fail(f"Submenu {menu.label!r} did not open")


@pytest.fixture
def context():
    ctx = dcg.Context()
    ctx.viewport.initialize(visible=False, width=900, height=700)
    yield ctx
    ctx.queue.shutdown(wait=True)
    ctx.viewport.destroy()


def test_menu_ownership_detach_and_collection():
    ctx = dcg.Context()
    with dcg.Plot(ctx, attach=False) as plot:
        line = dcg.PlotLine(ctx, X=[0, 1], Y=[0, 1])
        with dcg.Menu(ctx, label="Application") as menu:
            item = dcg.MenuItem(ctx, label="Action")
        direct = dcg.MenuItem(ctx, label="Direct action")

    assert line.parent is plot
    assert menu.parent is plot
    assert item.parent is menu
    assert direct.parent is plot
    menu.parent = None
    assert menu.parent is None
    assert menu not in plot.children
    menu.parent = plot
    refs = [weakref.ref(value) for value in (plot, menu, item, direct, line)]
    del plot, menu, item, direct, line
    gc.collect()
    assert all(ref() is None for ref in refs)


@pytest.mark.parametrize("layout", ["plots", "subplots", "shared"])
def test_checkable_items_are_isolated_and_callbacks_receive_state(context, layout):
    calls = []
    callback_event = threading.Event()

    def on_toggle(sender, target, checked):
        calls.append((sender, target, checked))
        callback_event.set()

    def make_plots():
        plots = []
        items = []
        for label in ("A", "B"):
            with dcg.Plot(context, label=label, width=800, height=260) as plot:
                dcg.PlotLine(context, label=f"Series {label}", X=[0, 1], Y=[0, 1])
                items.append(dcg.MenuItem(context, label=f"Toggle {label}", check=True, callback=on_toggle))
            plots.append(plot)
        return plots, items

    with dcg.Window(context, label="Menus", primary=True):
        if layout == "plots":
            plots, items = make_plots()
        else:
            with dcg.Subplots(
                context, rows=1, cols=2, width=850, height=360,
                share_legends=(layout == "shared")
            ):
                plots, items = make_plots()
    render(context, 5)
    assert not items[0].state.visible
    assert not items[1].state.visible

    for index, expected in ((0, True), (0, False), (1, True)):
        open_plot_menu(context, plots[index])
        assert items[index].state.visible
        assert not items[1 - index].state.visible
        callback_event.clear()
        click_item(context, items[index])
        assert callback_event.wait(2), "Menu item callback was not invoked"
        assert items[index].value is expected
        assert calls[-1] == (items[index], items[index], expected)
        assert not items[index].state.visible
    assert [call[2] for call in calls] == [True, False, True]
    assert items[0].value is False
    assert items[1].value is True


def test_nested_menu_action_and_hidden_state(context):
    calls = []
    callback_event = threading.Event()

    def on_action(sender, target, value):
        calls.append(sender)
        callback_event.set()

    with dcg.Window(context, label="Nested menu", primary=True):
        with dcg.Plot(context, label="Plot", width=700, height=400) as plot:
            dcg.PlotLine(context, X=[0, 1], Y=[0, 1])
            with dcg.Menu(context, label="Application") as outer:
                with dcg.Menu(context, label="Advanced") as inner:
                    item = dcg.MenuItem(context, label="Action", callback=on_action)

    render(context, 5)
    open_plot_menu(context, plot)
    open_submenu(context, outer, inner)
    open_submenu(context, inner, item)
    click_item(context, item)
    assert callback_event.wait(2), "Nested action callback was not invoked"
    assert calls == [item]
    assert not outer.state.visible
    assert not inner.state.visible
    assert not item.state.visible


def test_menu_button_and_no_menus(context):
    with dcg.Window(context, label="Menu button", primary=True):
        with dcg.Plot(context, label="Plot", width=700, height=400,
                      menu_button=dcg.MouseButton.MIDDLE) as plot:
            dcg.PlotLine(context, X=[0, 1], Y=[0, 1])
            item = dcg.MenuItem(context, label="Action")
    render(context, 5)

    open_plot_menu(context, plot, dcg.MouseButton.RIGHT)
    assert not item.state.visible
    open_plot_menu(context, plot, dcg.MouseButton.MIDDLE)
    assert item.state.visible
    click_item(context, item)
    assert not item.state.visible

    plot.no_menus = True
    open_plot_menu(context, plot, dcg.MouseButton.MIDDLE)
    assert not item.state.visible


def test_removing_and_replacing_a_menu_child(context):
    with dcg.Window(context, label="Menu replacement", primary=True):
        with dcg.Plot(context, label="Plot", width=700, height=400) as plot:
            dcg.PlotLine(context, X=[0, 1], Y=[0, 1])
            first = dcg.MenuItem(context, label="First")
    render(context, 5)
    open_plot_menu(context, plot)
    assert first.state.visible

    first.parent = None
    second = dcg.MenuItem(context, parent=plot, label="Second")
    render(context, 5)
    assert not first.state.visible
    assert second.state.visible

    plot.delete_item()
    render(context, 5)
    assert second.parent is None


def test_hidden_menu_child_does_not_add_separator():
    ctx = dcg.Context()
    ctx.viewport.initialize(
        visible=False, width=900, height=700,
        retrieve_framebuffer=True, always_submit_to_gpu=True,
    )
    try:
        with dcg.Window(ctx, label="Hidden menu", primary=True):
            with dcg.Plot(ctx, label="Plot", width=700, height=400) as plot:
                dcg.PlotLine(ctx, X=[0, 1], Y=[0, 1])
                item = dcg.MenuItem(ctx, label="Hidden", show=False)
        render(ctx, 5)
        open_plot_menu(ctx, plot)
        before = np.asarray(ctx.viewport.framebuffer.read()).copy()

        item.parent = None
        render(ctx, 5)
        after = np.asarray(ctx.viewport.framebuffer.read()).copy()
        assert np.array_equal(before, after)
    finally:
        ctx.queue.shutdown(wait=True)
        ctx.viewport.destroy()


def test_checkmark_changes_the_rendered_menu_item():
    ctx = dcg.Context()
    ctx.viewport.initialize(
        visible=False, width=900, height=700,
        retrieve_framebuffer=True, always_submit_to_gpu=True,
    )
    try:
        with dcg.Window(ctx, label="Checkmark", primary=True):
            with dcg.Plot(ctx, label="Plot", width=700, height=400) as plot:
                dcg.PlotLine(ctx, X=[0, 1], Y=[0, 1])
                item = dcg.MenuItem(ctx, label="Toggle", check=True)
        render(ctx, 5)
        open_plot_menu(ctx, plot)
        x, y = item.state.pos_to_viewport
        width, height = item.state.rect_size
        unchecked = np.asarray(ctx.viewport.framebuffer.read())[::-1].copy()

        click_item(ctx, item)
        assert item.value is True
        open_plot_menu(ctx, plot)
        checked = np.asarray(ctx.viewport.framebuffer.read())[::-1].copy()
        left, top = int(x), int(y)
        right, bottom = int(x + width), int(y + height)
        assert right > left and bottom > top
        assert not np.array_equal(
            unchecked[top:bottom, left:right],
            checked[top:bottom, left:right],
        )

        click_item(ctx, item)
        assert item.value is False
        open_plot_menu(ctx, plot)
        unchecked_again = np.asarray(ctx.viewport.framebuffer.read())[::-1].copy()
        assert np.array_equal(
            unchecked[top:bottom, left:right],
            unchecked_again[top:bottom, left:right],
        )
    finally:
        ctx.queue.shutdown(wait=True)
        ctx.viewport.destroy()
