import pytest

import dearcygui as dcg


@pytest.fixture
def ctx():
    return dcg.Context()


def test_gamepad_slots_are_stable(ctx):
    pads = ctx.viewport.gamepads
    assert isinstance(pads, tuple)
    assert len(pads) == 8
    assert [pad.slot for pad in pads] == list(range(8))
    assert all(first is second for first, second in zip(pads, ctx.viewport.gamepads))


def test_disconnected_gamepad_state_is_empty(ctx):
    for pad in ctx.viewport.gamepads:
        if pad.connected:
            continue
        assert pad.name == ""
        for button in dcg.GamepadButton:
            assert not pad.is_button_down(button)
            assert not pad.is_button_pressed(button)
            assert not pad.is_button_released(button)
        for axis in dcg.GamepadAxis:
            assert pad.get_axis(axis) == 0.0


@pytest.mark.parametrize("handler_type", [dcg.GamepadButtonHandler, dcg.GamepadAxisHandler])
def test_gamepad_handler_slot_configuration(ctx, handler_type):
    handler = handler_type(ctx)
    assert handler.controller == -1
    for slot in range(8):
        handler.controller = slot
        assert handler.controller == slot
    handler.controller = None
    assert handler.controller == -1
    for slot in (-2, 8):
        with pytest.raises(ValueError, match="controller must be"):
            handler.controller = slot
        assert handler.controller == -1


def test_gamepad_button_handler_defaults(ctx):
    handler = dcg.GamepadButtonHandler(ctx)
    assert handler.button == dcg.GamepadButton.SOUTH
    assert isinstance(handler.button, dcg.GamepadButton)
    assert handler.on_press is True
    handler.on_press = False
    assert handler.on_press is False


def test_gamepad_axis_handler_defaults(ctx):
    handler = dcg.GamepadAxisHandler(ctx)
    assert handler.axis == dcg.GamepadAxis.LEFT_X
    assert isinstance(handler.axis, dcg.GamepadAxis)
    assert handler.deadzone == pytest.approx(0.15)


@pytest.mark.parametrize("horizontal", [False, True])
@pytest.mark.parametrize("value_space", ["data", "normalized"])
@pytest.mark.parametrize("anchor", ["baseline", "axis_min", "axis_max"])
def test_plot_color_bars_configuration(ctx, horizontal, value_space, anchor):
    with dcg.Plot(ctx):
        bars = dcg.PlotColorBars(
            ctx,
            X=[0.25, 0.75],
            Y=[0.5, 1.0],
            colors=[(255, 0, 0, 255), (0, 255, 0, 255)],
            line_colors=[(0, 0, 255, 255)],
            horizontal=horizontal,
            value_space=value_space,
            normalized_max_fraction=0.2,
            anchor=anchor,
            anchor_value=2.0,
            ignore_fit=True,
            weight=0.5,
        )
    assert list(bars.X) == [0.25, 0.75]
    assert list(bars.Y) == [0.5, 1.0]
    assert bars.horizontal is horizontal
    assert bars.value_space == value_space
    assert bars.normalized_max_fraction == pytest.approx(0.2)
    assert bars.anchor == anchor
    assert bars.anchor_value == 2.0
    assert bars.ignore_fit is True
    assert bars.weight == 0.5
    assert len(bars.colors) == 2
    assert len(bars.line_colors) == 1


def test_plot_color_bars_default_value_space(ctx):
    assert dcg.PlotColorBars(ctx).value_space == "data"


@pytest.mark.parametrize(
    "configuration",
    [
        {"weight": 0.0},
        {"weight": -1.0},
        {"anchor": "invalid"},
        {"value_space": "invalid"},
        {"normalized_max_fraction": 0.0},
        {"normalized_max_fraction": 1.01},
    ],
)
def test_plot_color_bars_rejects_invalid_configuration(ctx, configuration):
    with pytest.raises(ValueError):
        dcg.PlotColorBars(ctx, **configuration)
