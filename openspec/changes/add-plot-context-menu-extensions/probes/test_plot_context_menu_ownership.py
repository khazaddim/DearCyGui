"""Ownership contract for the proposed plot context-menu widget children."""

import gc
import weakref

import dearcygui as dcg


def test_baseline_plot_keeps_plot_elements():
    context = dcg.Context()
    with dcg.Plot(context, attach=False) as plot:
        line = dcg.PlotLine(context, X=[0, 1], Y=[0, 1])
    assert line.parent is plot
    assert line in plot.children


def test_extension_menu_children_can_attach_and_detach():
    context = dcg.Context()
    with dcg.Plot(context, attach=False) as plot:
        line = dcg.PlotLine(context, X=[0, 1], Y=[0, 1])
        with dcg.Menu(context, label="Application") as menu:
            item = dcg.MenuItem(context, label="Action")
        direct = dcg.MenuItem(context, label="Direct action")

    assert line.parent is plot
    assert menu.parent is plot
    assert item.parent is menu
    assert direct.parent is plot
    assert menu in plot.children
    menu.parent = None
    assert menu.parent is None
    assert menu not in plot.children
    assert direct.parent is plot


def test_extension_plot_and_menu_children_are_collectable():
    context = dcg.Context()
    with dcg.Plot(context, attach=False) as plot:
        with dcg.Menu(context, label="Application") as menu:
            item = dcg.MenuItem(context, label="Action")
    assert menu.parent is plot
    assert item.parent is menu
    refs = [weakref.ref(value) for value in (plot, menu, item)]
    del plot, menu, item
    gc.collect()
    assert all(ref() is None for ref in refs)
