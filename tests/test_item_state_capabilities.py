"""Exercise advertised item states through representative interactions.

An unobserved state is evidence that the tested interaction failed, not proof
that every possible interaction fails. Compound items use an appropriate child
or item-specific configuration instead of assuming their entire rectangle is
an interactive control.
"""

import gc
from collections.abc import Iterator
from concurrent.futures import Executor
import time

import dearcygui as dcg
import pytest


_WIDGETS: tuple[str, ...] = (
    "Button",
    "Checkbox",
    "ChildWindow",
    "CollapsingHeader",
    "ColorButton",
    "ColorEdit",
    "ColorPicker",
    "Combo",
    "DrawInWindow",
    "HorizontalLayout",
    "Image",
    "InputText",
    "InputValue",
    "Layout",
    "ListBox",
    "MarkDownText",
    "Menu",
    "MenuBar",
    "MenuItem",
    "Plot",
    "ProgressBar",
    "RadioButton",
    "Separator",
    "Selectable",
    "SimplePlot",
    "Slider",
    "Spacer",
    "Subplots",
    "Tab",
    "TabBar",
    "TabButton",
    "Table",
    "Text",
    "TextValue",
    "TreeNode",
    "VerticalLayout",
    "Window",
)

_CAPABILITIES: tuple[str, ...] = (
    "hovered", "clicked", "double_clicked", "active", "focused", "dragging",
)

_KNOWN_UNOBSERVABLE: dict[tuple[str, str], str] = {
    ("Subplots", "dragging"): "Drag on the child plot does not reach the subplot handler",
}


@pytest.fixture
def context() -> Iterator[dcg.Context]:
    """Create an isolated viewport for a state-capability scenario."""
    ctx = dcg.Context()
    ctx.viewport.initialize(visible=False, width=800, height=600)
    ctx.viewport.vsync = False
    yield ctx
    assert isinstance(ctx.queue, Executor)
    ctx.queue.shutdown(wait=True)
    ctx.viewport.children = []
    gc.collect()
    deadline = time.monotonic() + 5
    while True:
        try:
            gc.collect()
            ctx.viewport.destroy()
            break
        except RuntimeError as error:
            if "resources are in use" not in str(error) or time.monotonic() >= deadline:
                raise
            time.sleep(0.01)
    gc.collect()


def _render(context: dcg.Context, *, count: int = 1) -> None:
    """Advance the requested number of frames."""
    for _ in range(count):
        context.viewport.render_frame()


def _make_widget(
    context: dcg.Context, *, name: str
) -> tuple[dcg.uiItem, dcg.uiItem]:
    """Create a subject and an interaction target inside a visible window."""
    window = dcg.Window(context, width=700, height=500)
    if name == "Window":
        subject = window
        target = dcg.Button(context, parent=window, label="Child", width=120, height=50)
    elif name in ("Layout", "HorizontalLayout", "VerticalLayout"):
        subject = getattr(dcg, name)(context, parent=window)
        target = dcg.Button(context, parent=subject, label="Child", width=120, height=50)
    elif name == "ChildWindow":
        subject = dcg.ChildWindow(context, parent=window, width=250, height=150)
        target = subject
    elif name == "DrawInWindow":
        subject = dcg.DrawInWindow(context, parent=window, width=250, height=150, button=True)
        target = subject
    elif name == "Image":
        texture = dcg.Texture(context, [[255] * 64 for _ in range(64)])
        subject = dcg.Image(context, parent=window, texture=texture, button=True)
        target = subject
    elif name == "Table":
        subject = dcg.Table(context, parent=window)
        target = dcg.Button(context, label="Cell", width=120, height=50)
        subject.append_row([target])
    elif name == "Subplots":
        subject = dcg.Subplots(context, parent=window, label="Widget", width=400, height=300)
        target = dcg.Plot(context, parent=subject, label="Plot")
    elif name in ("Menu", "MenuBar", "MenuItem"):
        bar = dcg.MenuBar(context, parent=window)
        menu = dcg.Menu(context, parent=bar, label="Menu")
        item = dcg.MenuItem(context, parent=menu, label="Choice", check=True)
        subject = {"Menu": menu, "MenuBar": bar, "MenuItem": item}[name]
        target = item if name == "MenuItem" else menu
    elif name in ("Tab", "TabBar", "TabButton"):
        tab_bar = dcg.TabBar(context, parent=window)
        tab = dcg.Tab(context, parent=tab_bar, label="Tab")
        if name == "TabBar":
            subject = tab_bar
            target = tab
        elif name == "Tab":
            subject = tab
            target = tab
        else:
            subject = dcg.TabButton(context, parent=tab_bar, label="TabButton")
            target = subject
    elif name in ("Combo", "ListBox", "RadioButton"):
        subject = getattr(dcg, name)(context, parent=window, label="Widget",
                                     items=["One", "Two"])
        target = subject
    elif name in ("Text", "MarkDownText"):
        subject = getattr(dcg, name)(context, parent=window, value="Example text")
        target = subject
    elif name == "TextValue":
        subject = dcg.TextValue(context, parent=window, value=42)
        target = subject
    elif name == "Spacer":
        subject = dcg.Spacer(context, parent=window, width=120, height=20)
        target = subject
    else:
        subject = getattr(dcg, name)(context, parent=window, label="Widget")
        target = subject
    return subject, target


def _open_menu(context: dcg.Context, menu: dcg.Menu) -> None:
    """Open a rendered menu with a mouse click."""
    x, y = menu.state.pos_to_viewport
    width, height = menu.state.rect_size
    context.inject_mouse_pos(x + width / 2, y + height / 2)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context, count=2)


@pytest.mark.parametrize(
    ("name", "capability"),
    (
        ("Text", "active"),
        ("Text", "focused"),
        ("ProgressBar", "focused"),
        ("MenuBar", "focused"),
        ("TabBar", "focused"),
        ("Combo", "deactivated_after_edited"),
        ("Layout", "toggled"),
        ("HorizontalLayout", "toggled"),
        ("VerticalLayout", "toggled"),
    ),
)
def test_unavailable_state_is_not_advertised(
    context: dcg.Context, *, name: str, capability: str
) -> None:
    """Prevent restored advertising of states unsupported by the underlying item."""
    subject, _ = _make_widget(context, name=name)
    with pytest.raises(AttributeError):
        getattr(subject.state, capability)


def test_time_watcher_does_not_advertise_item_state(context: dcg.Context) -> None:
    """Verify that the non-rendering time watcher exposes no item-state view."""
    watcher = dcg.TimeWatcher(context)
    with pytest.raises(AttributeError, match="does not support any state view properties"):
        _ = watcher.state


@pytest.mark.parametrize("name", _WIDGETS)
@pytest.mark.parametrize("capability", _CAPABILITIES)
def test_advertised_mouse_state_is_observable(
    context: dcg.Context, *, name: str, capability: str
) -> None:
    """Observe supported mouse states using the widget's appropriate target."""
    subject, target = _make_widget(context, name=name)
    events: list[bool] = []
    if capability == "dragging":
        def on_dragging(
            sender: dcg.DraggingHandler,
            item: dcg.baseItem,
            data: dcg.DraggingHandlerCallbackValue,
        ) -> None:
            """Record a drag callback."""
            events.append(True)

        handlers = [
            dcg.DraggingHandler(context, button=button, callback=on_dragging)
            for button in dcg.MouseButton
        ]
        try:
            subject.handlers = handlers
        except TypeError:
            pytest.skip(f"{name} does not advertise dragging")
    elif not hasattr(subject.state, capability):
        pytest.skip(f"{name} does not advertise {capability}")

    _render(context, count=5)
    if name == "MenuItem":
        menu = subject.parent
        assert isinstance(menu, dcg.Menu)
        _open_menu(context, menu)
    assert target.state.visible, f"{name}: interaction target is not visible"
    x, y = target.state.pos_to_viewport
    width, height = target.state.rect_size
    assert width > 10 and height > 10, f"{name}: invalid target size {(width, height)}"

    # A RadioButton is a group: target the first row rather than the gap.
    fractions = ((0.15, 0.2), (0.5, 0.2), (0.85, 0.2)) if name == "RadioButton" else (
        (0.15, 0.5), (0.5, 0.5), (0.85, 0.5)
    )
    observed = False
    target_hovered = False
    if capability == "dragging":
        buttons = list(dcg.MouseButton)
    elif capability == "double_clicked":
        buttons = [dcg.MouseButton.RIGHT]
    elif capability == "clicked":
        buttons = [dcg.MouseButton.LEFT, dcg.MouseButton.RIGHT]
    else:
        buttons = [dcg.MouseButton.LEFT]
    for button in buttons:
        for fx, fy in fractions:
            px = x + max(2, width * fx)
            py = y + max(2, height * fy)
            context.inject_mouse_pos(px, py)
            _render(context, count=2)
            if name in ("Menu", "MenuBar", "MenuItem"):
                target_hovered |= target.state.hovered
            if capability != "dragging":
                value = getattr(subject.state, capability)
                observed |= any(value) if capability in ("clicked", "double_clicked") else value
            context.inject_mouse_down(button)
            _render(context)
            if capability == "double_clicked":
                context.inject_mouse_up(button)
                _render(context)
                context.inject_mouse_down(button)
                _render(context)
                observed |= any(subject.state.double_clicked)
            if capability != "dragging":
                value = getattr(subject.state, capability)
                observed |= any(value) if capability in ("clicked", "double_clicked") else value
            context.inject_mouse_pos(px + 15, py)
            _render(context)
            if capability != "dragging":
                value = getattr(subject.state, capability)
                observed |= any(value) if capability in ("clicked", "double_clicked") else value
            context.inject_mouse_up(button)
            _render(context)
            if capability != "dragging":
                value = getattr(subject.state, capability)
                observed |= any(value) if capability in ("clicked", "double_clicked") else value
    if capability == "dragging":
        context.queue.submit(lambda: None).result(timeout=5)
        observed = bool(events)
    if name in ("Menu", "MenuBar", "MenuItem"):
        assert target_hovered, f"{name}: the test did not hover the intended menu entry"
    if not observed and (name, capability) in _KNOWN_UNOBSERVABLE:
        pytest.xfail(_KNOWN_UNOBSERVABLE[name, capability])
    assert observed, f"{name} advertises {capability}, but the interaction did not produce it"


@pytest.mark.parametrize(
    "name",
    ("Button", "Combo", "Layout", "HorizontalLayout", "VerticalLayout", "RadioButton",
     "Selectable"),
)
def test_advertised_activation_transitions(context: dcg.Context, *, name: str) -> None:
    """Observe activation and deactivation on a held and released mouse button."""
    subject, target = _make_widget(context, name=name)
    if not hasattr(subject.state, "active"):
        pytest.skip(f"{name} does not advertise active")
    _render(context, count=5)
    x, y = target.state.pos_to_viewport
    width, height = target.state.rect_size
    py = y + height * (0.2 if name == "RadioButton" else 0.5)
    context.inject_mouse_pos(x + min(10, width / 2), py)
    _render(context, count=2)
    assert not subject.state.active
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    assert subject.state.active, f"{name}: the test did not activate the subject"
    assert subject.state.activated, f"{name}: activation transition was not reported"
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)
    assert not subject.state.active, f"{name}: the test did not deactivate the subject"
    assert subject.state.deactivated, f"{name}: deactivation transition was not reported"


@pytest.mark.parametrize("layout_name", ("InputText", "Layout", "HorizontalLayout", "VerticalLayout"))
@pytest.mark.parametrize("capability", ("edited", "deactivated_after_edited"))
def test_layout_advertised_edit_state_tracks_child(
    context: dcg.Context, *, layout_name: str, capability: str
) -> None:
    """Verify group edit states while a child input is edited and deactivated."""
    window = dcg.Window(context, width=700, height=500)
    if layout_name == "InputText":
        child = dcg.InputText(context, parent=window, value="Example", width=250)
        layout = child
    else:
        layout = getattr(dcg, layout_name)(context, parent=window)
        child = dcg.InputText(context, parent=layout, value="Example", width=250)
    _render(context, count=5)
    if not hasattr(layout.state, capability):
        pytest.skip(f"{layout_name} does not advertise {capability}")
    x, y = child.state.pos_to_viewport
    width, height = child.state.rect_size
    context.inject_mouse_pos(x + width / 2, y + height / 2)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)
    assert child.state.active, "the input must be active before editing"

    context.inject_key_down(dcg.Key.BACKSPACE)
    _render(context)
    child_edited = child.state.edited
    layout_edited = layout.state.edited
    context.inject_key_up(dcg.Key.BACKSPACE)
    _render(context)
    context.inject_key_down(dcg.Key.ENTER)
    _render(context)
    child_deactivated = child.state.deactivated_after_edited
    layout_deactivated = layout.state.deactivated_after_edited
    context.inject_key_up(dcg.Key.ENTER)
    _render(context)
    assert child_edited, "the child must actually be edited"
    if capability == "edited":
        assert layout_edited, f"{layout_name} advertises edited but did not report the child's edit"
    else:
        assert child_deactivated, "the child must actually deactivate after an edit"
        assert layout_deactivated, (
            f"{layout_name} advertises deactivated_after_edited but did not report the transition"
        )


@pytest.mark.parametrize("layout_name", ("InputText", "Layout", "HorizontalLayout", "VerticalLayout"))
@pytest.mark.parametrize("edit", (False, True))
def test_advertised_deactivation_after_edit_across_frames(
    context: dcg.Context, *, layout_name: str, edit: bool
) -> None:
    """Track a text edit followed by idle active frames and a later deactivation."""
    window = dcg.Window(context, width=700, height=500)
    if layout_name == "InputText":
        child = dcg.InputText(context, parent=window, value="Example", width=250)
        subject = child
    else:
        subject = getattr(dcg, layout_name)(context, parent=window)
        child = dcg.InputText(context, parent=subject, value="Example", width=250)
    if not hasattr(subject.state, "deactivated_after_edited"):
        pytest.skip(f"{layout_name} does not advertise deactivated_after_edited")
    events: list[bool] = []

    def on_deactivated(
        sender: dcg.DeactivatedAfterEditHandler,
        item: dcg.baseItem,
        data: dcg.DeactivatedAfterEditHandlerCallbackValue,
    ) -> None:
        """Record a completed edit."""
        events.append(True)

    subject.handlers = [dcg.DeactivatedAfterEditHandler(context, callback=on_deactivated)]

    _render(context, count=5)
    x, y = child.state.pos_to_viewport
    width, height = child.state.rect_size
    context.inject_mouse_pos(x + width / 2, y + height / 2)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)
    assert child.state.active and subject.state.active
    before = child.value

    if edit:
        context.inject_key_down(dcg.Key.BACKSPACE)
        _render(context)
        assert child.value != before and child.state.edited
        assert subject.state.edited and subject.state.active
        assert not subject.state.deactivated_after_edited
        context.inject_key_up(dcg.Key.BACKSPACE)

    for _ in range(5):
        _render(context)
        assert child.state.active and subject.state.active
        assert not child.state.edited and not subject.state.edited
        assert not child.state.deactivated_after_edited
        assert not subject.state.deactivated_after_edited

    context.inject_key_down(dcg.Key.ENTER)
    _render(context)
    assert not child.state.active and not subject.state.active
    assert child.state.deactivated_after_edited == edit
    assert subject.state.deactivated_after_edited == edit
    context.inject_key_up(dcg.Key.ENTER)
    _render(context)
    assert not child.state.deactivated_after_edited
    assert not subject.state.deactivated_after_edited
    context.queue.submit(lambda: None).result(timeout=5)
    assert len(events) == int(edit), f"{layout_name}: unexpected edit completion callbacks"


@pytest.mark.parametrize("layout_name", ("Layout", "HorizontalLayout", "VerticalLayout"))
def test_layout_advertised_toggle_tracks_child(context: dcg.Context, *, layout_name: str) -> None:
    """Exercise an advertised group toggle using an expandable child."""
    window = dcg.Window(context, width=700, height=500)
    layout = getattr(dcg, layout_name)(context, parent=window)
    child = dcg.TreeNode(context, parent=layout, label="Tree")
    _render(context, count=5)
    if not hasattr(layout.state, "toggled"):
        pytest.skip(f"{layout_name} does not advertise toggled")
    x, y = child.state.pos_to_viewport
    width, height = child.state.rect_size
    context.inject_mouse_pos(x + min(10, width / 2), y + height / 2)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    child_toggled = child.state.toggled
    layout_toggled = layout.state.toggled
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)
    child_toggled |= child.state.toggled
    layout_toggled |= layout.state.toggled
    assert child_toggled, "the child must actually toggle open"
    assert layout_toggled, f"{layout_name} advertises toggled but did not report the child toggle"


@pytest.mark.parametrize("name", ("Combo", "Menu", "TreeNode", "CollapsingHeader"))
def test_advertised_toggle_is_observable(context: dcg.Context, *, name: str) -> None:
    """Observe an advertised toggle during the widget's normal opening gesture."""
    subject, target = _make_widget(context, name=name)
    if not hasattr(subject.state, "toggled"):
        pytest.skip(f"{name} does not advertise toggled")
    _render(context, count=5)
    assert target.state.visible
    x, y = target.state.pos_to_viewport
    width, height = target.state.rect_size
    context.inject_mouse_pos(x + min(10, width / 2), y + height / 2)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    observed = subject.state.toggled
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)
    observed |= subject.state.toggled
    assert observed, f"{name} advertises toggled but did not report opening"


@pytest.mark.parametrize(
    "name", ("Checkbox", "Slider", "InputValue", "Selectable", "RadioButton", "ListBox")
)
def test_advertised_edit_state_is_observable(context: dcg.Context, *, name: str) -> None:
    """Verify edited state when a real user interaction changes a widget's value."""
    subject, target = _make_widget(context, name=name)
    if not hasattr(subject.state, "edited"):
        pytest.skip(f"{name} does not advertise edited")
    if name == "InputValue":
        subject.value = 123
        subject.width = 250
    _render(context, count=5)
    assert target.state.visible
    before = subject.value
    x, y = target.state.pos_to_viewport
    width, height = target.state.rect_size
    if name == "RadioButton":
        px, py = x + 10, y + height * 0.2
    elif name == "ListBox":
        px, py = x + 15, y + min(15, height / 2)
    elif name == "InputValue":
        px, py = x + width * 0.68, y + height / 2
    else:
        px, py = x + width * 0.2, y + height / 2
    context.inject_mouse_pos(px, py)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    observed = subject.state.edited
    context.inject_mouse_pos(x + width * 0.8 if name == "Slider" else px + 20, py)
    _render(context)
    observed |= subject.state.edited
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)
    observed |= subject.state.edited
    if name == "InputValue" and subject.value == before:
        for fraction in (0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85):
            context.inject_mouse_pos(x + width * fraction, py)
            _render(context, count=2)
            context.inject_mouse_down(dcg.MouseButton.LEFT)
            _render(context)
            observed |= subject.state.edited
            context.inject_mouse_up(dcg.MouseButton.LEFT)
            _render(context)
            observed |= subject.state.edited
            if subject.value != before:
                break
    assert subject.value != before, f"{name}: the test did not change the value"
    assert observed, f"{name} advertises edited but did not report the value change"


@pytest.mark.parametrize("name", ("RadioButton", "Selectable"))
@pytest.mark.parametrize("held_frames", (1, 5))
def test_advertised_deactivation_after_edit_on_selection(
    context: dcg.Context, *, name: str, held_frames: int
) -> None:
    """Observe selection edits and deactivation on release after a short or long hold."""
    subject, _ = _make_widget(context, name=name)
    if not hasattr(subject.state, "deactivated_after_edited"):
        pytest.skip(f"{name} does not advertise deactivated_after_edited")
    _render(context, count=5)
    before = subject.value
    x, y = subject.state.pos_to_viewport
    width, height = subject.state.rect_size
    py = y + height * (0.2 if name == "RadioButton" else 0.5)
    context.inject_mouse_pos(x + min(10, width / 2), py)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    for _ in range(held_frames):
        _render(context)
        assert subject.state.active, f"{name}: the test did not keep the control active"
        assert subject.value == before, f"{name}: the selection changed before release"
        assert not subject.state.edited, f"{name}: an edit was reported before release"
        assert not subject.state.deactivated_after_edited
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)
    assert subject.value != before, f"{name}: the test did not change the selection"
    assert subject.state.edited, f"{name}: the selection change was not reported as edited"
    assert subject.state.deactivated_after_edited, (
        f"{name} advertises deactivated_after_edited but did not report the selection change"
    )
    _render(context)
    assert not subject.state.deactivated_after_edited, f"{name}: deactivation repeated"


@pytest.mark.parametrize("name", ("RadioButton", "Selectable"))
def test_advertised_deactivation_after_edit_on_cancelled_selection(
    context: dcg.Context, *, name: str
) -> None:
    """Do not report an edit when a held selection is released outside its control."""
    subject, _ = _make_widget(context, name=name)
    if not hasattr(subject.state, "deactivated_after_edited"):
        pytest.skip(f"{name} does not advertise deactivated_after_edited")
    _render(context, count=5)
    before = subject.value
    x, y = subject.state.pos_to_viewport
    width, height = subject.state.rect_size
    context.inject_mouse_pos(x + min(10, width / 2), y + height * 0.2)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context, count=5)
    assert subject.state.active, f"{name}: the control must be active before cancellation"
    context.inject_mouse_pos(x + width + 60, y + height + 60)
    _render(context, count=2)
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)
    assert not subject.state.active, f"{name}: the control must deactivate after release"
    assert subject.value == before, f"{name}: the cancelled interaction changed the value"
    assert not subject.state.edited
    assert not subject.state.deactivated_after_edited


def test_radio_button_advertised_deactivation_after_keyboard_edit(
    context: dcg.Context,
) -> None:
    """Report a keyboard edit when the active radio button is released frames later."""
    subject, _ = _make_widget(context, name="RadioButton")
    if not hasattr(subject.state, "deactivated_after_edited"):
        pytest.skip("RadioButton does not advertise deactivated_after_edited")
    context.viewport.keyboard_navigation = True
    _render(context, count=5)
    x, y = subject.state.pos_to_viewport
    _, height = subject.state.rect_size
    context.inject_mouse_pos(x + 10, y + height * 0.2)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)
    assert subject.value == "One", "the first radio button must be selected"

    context.inject_mouse_pos(x + 300, y + height + 100)
    _render(context)
    context.inject_key_down(dcg.Key.DOWNARROW)
    _render(context, count=3)
    context.inject_key_up(dcg.Key.DOWNARROW)
    _render(context, count=2)
    context.inject_key_down(dcg.Key.SPACE)
    _render(context)
    assert subject.value == "Two", "keyboard activation must change the selection"
    assert subject.state.active and subject.state.edited
    assert not subject.state.deactivated_after_edited

    for _ in range(4):
        _render(context)
        assert subject.state.active and not subject.state.edited
        assert not subject.state.deactivated_after_edited
    context.inject_key_up(dcg.Key.SPACE)
    _render(context)
    assert not subject.state.active and not subject.state.edited
    assert subject.state.deactivated_after_edited, (
        "RadioButton did not report deactivation after its earlier keyboard edit"
    )
    _render(context)
    assert not subject.state.deactivated_after_edited


def test_radio_button_no_deactivation_after_unchanged_selection(context: dcg.Context) -> None:
    """Do not report an edit when a selected radio button is pressed again."""
    subject, _ = _make_widget(context, name="RadioButton")
    if not hasattr(subject.state, "deactivated_after_edited"):
        pytest.skip("RadioButton does not advertise deactivated_after_edited")
    subject.value = "One"
    _render(context, count=5)
    x, y = subject.state.pos_to_viewport
    _, height = subject.state.rect_size
    context.inject_mouse_pos(x + 10, y + height * 0.2)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context, count=5)
    assert subject.state.active and subject.value == "One"
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)
    assert not subject.state.active and subject.value == "One"
    assert not subject.state.edited
    assert not subject.state.deactivated_after_edited


def test_menu_item_deactivation_after_keyboard_edit(context: dcg.Context) -> None:
    """Observe keyboard menu edits, including popup closure while the key is held."""
    context.viewport.keyboard_navigation = True
    window = dcg.Window(context, width=700, height=500)
    bar = dcg.MenuBar(context, parent=window)
    menu = dcg.Menu(context, parent=bar, label="File")
    item = dcg.MenuItem(context, parent=menu, label="Choice", check=True)
    if not hasattr(item.state, "deactivated_after_edited"):
        pytest.skip("MenuItem does not advertise deactivated_after_edited")
    _render(context, count=5)
    _open_menu(context, menu)
    assert item.state.visible
    x, y = item.state.pos_to_viewport
    width, height = item.state.rect_size
    context.inject_mouse_pos(x + width / 2, y + height / 2)
    _render(context, count=2)
    context.inject_key_down(dcg.Key.DOWNARROW)
    _render(context)
    context.inject_key_up(dcg.Key.DOWNARROW)
    _render(context, count=2)
    before = item.value
    context.inject_key_down(dcg.Key.SPACE)
    _render(context)
    assert item.value != before and item.state.edited
    assert item.state.deactivated_after_edited
    for _ in range(4):
        _render(context)
        assert not item.state.deactivated_after_edited
    context.inject_key_up(dcg.Key.SPACE)
    _render(context)
    assert not item.state.deactivated_after_edited


@pytest.mark.parametrize("capability", ("edited", "deactivated_after_edited"))
def test_combo_advertised_edit_state_on_popup_selection(
    context: dcg.Context, *, capability: str
) -> None:
    """Observe edit states while selecting a different entry in the popup."""
    subject, _ = _make_widget(context, name="Combo")
    if not hasattr(subject.state, capability):
        pytest.skip(f"Combo does not advertise {capability}")
    subject.value = "One"
    _render(context, count=5)
    x, y = subject.state.pos_to_viewport
    width, height = subject.state.rect_size

    context.inject_mouse_pos(x + min(30, width / 2), y + height / 2)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    opened = subject.state.toggled
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)
    opened |= subject.state.toggled
    assert opened, "the combo popup must open before selecting an entry"
    _render(context)

    context.inject_mouse_pos(x + 15, y + height + 40)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    observed = getattr(subject.state, capability)
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)
    observed |= getattr(subject.state, capability)
    assert subject.value == "Two", "the test must select a different popup entry"
    assert observed, f"Combo advertises {capability} but did not report the selection change"


@pytest.mark.parametrize("capability", ("edited", "deactivated_after_edited"))
def test_menu_item_advertised_edit_state_on_selection(
    context: dcg.Context, *, capability: str
) -> None:
    """Observe menu item edit states after a user changes its checked value."""
    window = dcg.Window(context, width=700, height=500)
    bar = dcg.MenuBar(context, parent=window)
    menu = dcg.Menu(context, parent=bar, label="File")
    item = dcg.MenuItem(context, parent=menu, label="Choice", check=True)
    if not hasattr(item.state, capability):
        pytest.skip(f"MenuItem does not advertise {capability}")
    _render(context, count=5)
    _open_menu(context, menu)
    assert item.state.visible, "the menu item must be visible before selection"

    before = item.value
    x, y = item.state.pos_to_viewport
    width, height = item.state.rect_size
    context.inject_mouse_pos(x + width / 2, y + height / 2)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    observed = getattr(item.state, capability)
    for _ in range(4):
        _render(context)
        assert item.value == before, "the menu item must not change before mouse release"
        assert not getattr(item.state, capability)
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)
    observed |= getattr(item.state, capability)
    assert item.value != before, "the menu selection must change the checked value"
    assert observed, f"MenuItem advertises {capability} but did not report the edit"


@pytest.mark.parametrize("capability", ("edited", "deactivated_after_edited"))
def test_tab_button_advertised_edit_state_on_press(
    context: dcg.Context, *, capability: str
) -> None:
    """Check advertised edit states for a successfully pressed tab button."""
    subject, _ = _make_widget(context, name="TabButton")
    if not hasattr(subject.state, capability):
        pytest.skip(f"TabButton does not advertise {capability}")
    presses: list[bool] = []
    subject.callback = lambda: presses.append(True)
    _render(context, count=5)
    tab_bar = subject.parent
    assert isinstance(tab_bar, dcg.TabBar)
    first_tab = tab_bar.children[0]
    assert isinstance(first_tab, dcg.Tab)
    x, y = tab_bar.state.pos_to_viewport
    x += first_tab.state.rect_size.x
    width, height = subject.state.rect_size
    context.inject_mouse_pos(x + width / 2, y + height / 2)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    observed = getattr(subject.state, capability)
    for _ in range(4):
        _render(context)
        assert subject.state.active, "the tab button must remain active while held"
        assert not getattr(subject.state, capability)
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)
    observed |= getattr(subject.state, capability)
    context.queue.submit(lambda: None).result(timeout=5)
    assert presses, "the tab button must actually be pressed"
    assert observed, f"TabButton advertises {capability} but did not report the press"


def test_tab_advertised_toggle_on_selection(context: dcg.Context) -> None:
    """Observe the second tab opening when selected through its header."""
    window = dcg.Window(context, width=700, height=500)
    bar = dcg.TabBar(context, parent=window)
    first = dcg.Tab(context, parent=bar, label="First")
    second = dcg.Tab(context, parent=bar, label="Second")
    if not hasattr(second.state, "toggled"):
        pytest.skip("Tab does not advertise toggled")
    _render(context, count=5)
    assert first.value and not second.value, "the first tab must initially be selected"
    x, y = bar.state.pos_to_viewport
    x += first.state.rect_size.x
    width, height = second.state.rect_size
    context.inject_mouse_pos(x + width / 2, y + height / 2)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    observed = second.state.toggled
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)
    observed |= second.state.toggled
    assert second.value, "the test must select the second tab"
    assert observed, "Tab advertises toggled but did not report selection"


@pytest.mark.parametrize("name", ("Tab", "TabButton"))
def test_tab_header_position_and_focus(context: dcg.Context, *, name: str) -> None:
    """Track the header rectangle and its focus independently of other widgets."""
    context.viewport.keyboard_navigation = True
    window = dcg.Window(context, width=700, height=500)
    other = dcg.Button(context, parent=window, label="Other")
    bar = dcg.TabBar(context, parent=window)
    first = dcg.Tab(context, parent=bar, label="First", closable=True)
    target = (dcg.Tab(context, parent=bar, label="Second") if name == "Tab"
              else dcg.TabButton(context, parent=bar, label="Second"))
    _render(context, count=6)

    x, y = target.state.pos_to_viewport
    width, height = target.state.rect_size
    first_x, first_y = first.state.pos_to_viewport
    bar_x, bar_y = bar.state.pos_to_viewport
    assert first_x >= bar_x and first_y == pytest.approx(bar_y)
    assert x >= first_x + first.state.rect_size.x - 1
    assert y == pytest.approx(bar_y)
    context.inject_mouse_pos(x + width / 2, y + height / 2)
    _render(context, count=3)
    assert target.state.hovered
    assert not first.state.hovered
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    assert target.state.focused
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context, count=2)
    assert target.state.focused

    x, y = other.state.pos_to_viewport
    width, height = other.state.rect_size
    context.inject_mouse_pos(x + width / 2, y + height / 2)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    assert other.state.focused and not target.state.focused
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)


@pytest.mark.parametrize("name", ("MenuBar", "TabBar"))
def test_bar_states_are_not_previous_item_states(context: dcg.Context, *, name: str) -> None:
    """Use bar geometry and mouse interactions rather than a preceding item."""
    window = dcg.Window(context, width=700, height=500)
    if name == "MenuBar":
        bar = dcg.MenuBar(context, parent=window)
        target = dcg.Menu(context, parent=bar, label="File")
        previous = dcg.Button(context, parent=window, label="Other", width=90, height=30)
    else:
        previous = dcg.Button(context, parent=window, label="Other", width=90, height=30)
        bar = dcg.TabBar(context, parent=window)
        tab = dcg.Tab(context, parent=bar, label="First")
        target = tab
        dcg.Button(context, parent=tab, label="Content", height=100)
    _render(context, count=6)
    with pytest.raises(TypeError):
        bar.handlers = [dcg.FocusHandler(context, callback=lambda: None)]
    x, y = bar.state.pos_to_viewport
    width, height = bar.state.rect_size
    assert bar.state.visible
    assert x > 0 and y > 0 and width > 0 and height > 0
    if name == "MenuBar":
        assert width == pytest.approx(target.state.rect_size.x)
    else:
        assert height > 100

    px, py = previous.state.pos_to_viewport
    pw, ph = previous.state.rect_size
    context.inject_mouse_pos(px + pw / 2, py + ph / 2)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    assert previous.state.hovered
    assert not bar.state.hovered and not any(bar.state.clicked)
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)

    x, y = target.state.pos_to_viewport
    width, height = target.state.rect_size
    context.inject_mouse_pos(x + width / 2, y + height / 2)
    _render(context, count=2)
    assert bar.state.hovered
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    assert bar.state.clicked[0]
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)


def test_menu_popup_focus_and_mouse_scope(context: dcg.Context) -> None:
    """Track focus and mouse clicks over the menu's open popup."""
    context.viewport.keyboard_navigation = True
    window = dcg.Window(context, width=700, height=500)
    bar = dcg.MenuBar(context, parent=window)
    menu = dcg.Menu(context, parent=bar, label="File")
    item = dcg.MenuItem(context, parent=menu, label="Choice", check=True)
    _render(context, count=5)
    _open_menu(context, menu)
    assert menu.value and menu.state.focused and item.state.visible
    assert tuple(bar.state.pos_to_viewport) == pytest.approx(tuple(menu.state.pos_to_viewport))
    assert tuple(bar.state.rect_size) == pytest.approx(tuple(menu.state.rect_size))
    x, y = item.state.pos_to_viewport
    width, height = item.state.rect_size
    context.inject_mouse_pos(x + width / 2, y + height / 2)
    _render(context, count=2)
    assert menu.state.hovered and item.state.hovered
    context.inject_key_down(dcg.Key.DOWNARROW)
    _render(context)
    context.inject_key_up(dcg.Key.DOWNARROW)
    _render(context, count=2)
    assert item.state.focused
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    assert menu.state.clicked[0] and item.state.clicked[0]
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context, count=2)
    assert not menu.value


def test_tab_focus_handlers_follow_focus_transitions(context: dcg.Context) -> None:
    """Deliver focus transitions for the header rather than preceding widgets."""
    context.viewport.keyboard_navigation = True
    window = dcg.Window(context, width=700, height=500)
    other = dcg.Button(context, parent=window, label="Other")
    bar = dcg.TabBar(context, parent=window)
    dcg.Tab(context, parent=bar, label="First")
    target = dcg.TabButton(context, parent=bar, label="Action")
    events: list[str] = []
    target.handlers = [
        dcg.GotFocusHandler(context, callback=lambda: events.append("got")),
        dcg.LostFocusHandler(context, callback=lambda: events.append("lost")),
    ]
    _render(context, count=6)
    for widget in (target, other):
        x, y = widget.state.pos_to_viewport
        width, height = widget.state.rect_size
        context.inject_mouse_pos(x + width / 2, y + height / 2)
        _render(context, count=2)
        context.inject_mouse_down(dcg.MouseButton.LEFT)
        _render(context)
        context.inject_mouse_up(dcg.MouseButton.LEFT)
        _render(context, count=2)
    context.queue.submit(lambda: None).result(timeout=5)
    assert events == ["got", "lost"]


def test_tab_headers_receive_keyboard_focus(context: dcg.Context) -> None:
    """Navigate from a button through both kinds of tab header using Tab."""
    context.viewport.keyboard_navigation = True
    window = dcg.Window(context, width=700, height=500)
    other = dcg.Button(context, parent=window, label="Other")
    bar = dcg.TabBar(context, parent=window)
    tab = dcg.Tab(context, parent=bar, label="First")
    button = dcg.TabButton(context, parent=bar, label="Action")
    _render(context, count=6)
    x, y = other.state.pos_to_viewport
    width, height = other.state.rect_size
    context.inject_mouse_pos(x + width / 2, y + height / 2)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context, count=2)
    assert other.state.focused

    observed: set[str] = set()
    for _ in range(5):
        context.inject_key_down(dcg.Key.TAB)
        _render(context)
        context.inject_key_up(dcg.Key.TAB)
        _render(context, count=2)
        if tab.state.focused:
            observed.add("tab")
        if button.state.focused:
            observed.add("button")
    assert observed == {"tab", "button"}


def test_main_menu_bar_rectangle_and_mouse(context: dcg.Context) -> None:
    """Capture the viewport menu bar without borrowing a window item."""
    bar = dcg.MenuBar(context, parent=context.viewport)
    menu = dcg.Menu(context, parent=bar, label="File")
    dcg.MenuItem(context, parent=menu, label="Choice")
    dcg.Window(context, width=400, height=300)
    _render(context, count=6)
    x, y = bar.state.pos_to_viewport
    width, height = bar.state.rect_size
    assert bar.state.visible and x >= 0 and y >= 0
    assert width == pytest.approx(menu.state.rect_size.x) and height > 0
    assert (bar.state.content_pos.x + bar.state.content_region_avail.x
            == pytest.approx(800 - bar.state.content_pos.x))
    x, y = menu.state.pos_to_viewport
    width, height = menu.state.rect_size
    context.inject_mouse_pos(x + width / 2, y + height / 2)
    _render(context, count=2)
    assert bar.state.hovered and menu.state.hovered
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    assert bar.state.clicked[0] and menu.state.clicked[0]
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)


@pytest.mark.parametrize("parent_kind", ("Window", "ChildWindow", "Viewport"))
def test_menu_bars_share_right_edge_but_not_mouse_states(
    context: dcg.Context, *, parent_kind: str
) -> None:
    """Keep independently appended bars bounded to their own children."""
    if parent_kind == "Viewport":
        parent = context.viewport
    else:
        window = dcg.Window(context, width=700, height=500)
        parent = (window if parent_kind == "Window"
                  else dcg.ChildWindow(context, parent=window, width=500, height=250))
    first = dcg.MenuBar(context, parent=parent)
    left = dcg.Menu(context, parent=first, label="File")
    second = dcg.MenuBar(context, parent=parent)
    right = dcg.Menu(context, parent=second, label="Edit")
    _render(context, count=8)
    assert first.state.visible and second.state.visible
    assert tuple(first.state.pos_to_viewport) == pytest.approx(tuple(left.state.pos_to_viewport))
    assert tuple(first.state.rect_size) == pytest.approx(tuple(left.state.rect_size))
    assert tuple(second.state.pos_to_viewport) == pytest.approx(tuple(right.state.pos_to_viewport))
    assert tuple(second.state.rect_size) == pytest.approx(tuple(right.state.rect_size))
    assert second.state.content_pos.x > first.state.content_pos.x
    assert second.state.content_region_avail.x < first.state.content_region_avail.x
    assert (second.state.content_pos.x + second.state.content_region_avail.x
            == pytest.approx(first.state.content_pos.x + first.state.content_region_avail.x))

    x, y = left.state.pos_to_viewport
    width, height = left.state.rect_size
    context.inject_mouse_pos(x + width / 2, y + height / 2)
    _render(context, count=2)
    assert first.state.hovered and not second.state.hovered
    context.inject_mouse_down(dcg.MouseButton.RIGHT)
    _render(context)
    assert first.state.clicked[1] and not any(second.state.clicked)
    context.inject_mouse_up(dcg.MouseButton.RIGHT)
    _render(context)


@pytest.mark.parametrize("parent_kind", ("Window", "ChildWindow", "Viewport"))
@pytest.mark.parametrize("item_kind", ("Menu", "MenuItem", "Button"))
@pytest.mark.parametrize("item_spacing", ((8, 4), (7, 5)))
def test_menu_bar_first_item_uses_native_cursor(
    context: dcg.Context, *, parent_kind: str, item_kind: str, item_spacing: tuple[int, int]
) -> None:
    """Keep the original cursor and the expanded menu interaction rectangle."""
    theme = dcg.ThemeStyleImGui(context, item_spacing=item_spacing)
    if parent_kind == "Viewport":
        parent = context.viewport
    else:
        window = dcg.Window(context, width=700, height=500)
        parent = (window if parent_kind == "Window"
                  else dcg.ChildWindow(context, parent=window, width=500, height=250))
    bar = dcg.MenuBar(context, parent=parent, theme=theme)
    item = getattr(dcg, item_kind)(context, parent=bar, label="First")
    _render(context, count=8)
    if item_kind == "Button":
        assert tuple(item.state.pos_to_parent) == pytest.approx((0, 0))
    else:
        assert item.state.pos_to_parent.x == pytest.approx(
            item_spacing[0] // 2 - item_spacing[0]
        )
        assert item.state.pos_to_parent.y == pytest.approx(3 - item_spacing[1] // 2)


@pytest.mark.parametrize("item_kind", ("Menu", "MenuItem"))
def test_menu_popup_first_item_starts_at_content_origin(
    context: dcg.Context, *, item_kind: str
) -> None:
    """Align the first popup item rectangle with its parent content origin."""
    window = dcg.Window(context, width=700, height=500)
    bar = dcg.MenuBar(context, parent=window)
    menu = dcg.Menu(context, parent=bar, label="File")
    item = getattr(dcg, item_kind)(context, parent=menu, label="First")
    _render(context, count=5)
    _open_menu(context, menu)
    assert item.state.visible
    assert tuple(item.state.pos_to_viewport) == pytest.approx(tuple(menu.state.content_pos))
    assert tuple(item.state.pos_to_parent) == pytest.approx((0, 0))


@pytest.mark.parametrize("item_spacing", ((8, 4), (7, 5)))
def test_menu_bar_mixed_siblings_stay_on_same_line(
    context: dcg.Context, *, item_spacing: tuple[int, int]
) -> None:
    """Keep later siblings aligned after compensating menu item padding."""
    window = dcg.Window(context, width=700, height=500)
    theme = dcg.ThemeStyleImGui(context, item_spacing=item_spacing)
    bar = dcg.MenuBar(context, parent=window, theme=theme)
    items = (
        dcg.Menu(context, parent=bar, label="First"),
        dcg.MenuItem(context, parent=bar, label="Second"),
        dcg.Button(context, parent=bar, label="Third"),
        dcg.Menu(context, parent=bar, label="Fourth"),
    )
    dcg.MenuItem(context, parent=items[0], label="Popup child")
    _render(context, count=8)
    for open_menu in (False, True):
        if open_menu:
            _open_menu(context, items[0])
        assert items[2].state.pos_to_viewport.y == pytest.approx(bar.state.content_pos.y)
        for item in (items[0], items[1], items[3]):
            assert item.state.pos_to_viewport.y == pytest.approx(
                bar.state.content_pos.y + 3 - item_spacing[1] // 2
            )
        for left, right in zip(items, items[1:]):
            assert (right.state.pos_to_viewport.x >=
                    left.state.pos_to_viewport.x + left.state.rect_size.x)


@pytest.mark.parametrize("item_spacing", ((8, 4), (7, 5)))
@pytest.mark.parametrize("split_bars", (False, True))
def test_consecutive_menu_entries_preserve_tight_layout(
    context: dcg.Context, *, item_spacing: tuple[int, int], split_bars: bool
) -> None:
    """Keep adjacent menu entry rectangles contiguous as in ImGui."""
    window = dcg.Window(context, width=700, height=500)
    theme = dcg.ThemeStyleImGui(context, item_spacing=item_spacing)
    first_bar = dcg.MenuBar(context, parent=window, theme=theme)
    second_bar = dcg.MenuBar(context, parent=window, theme=theme) if split_bars else first_bar
    items = (
        dcg.Menu(context, parent=first_bar, label="First"),
        dcg.MenuItem(context, parent=first_bar, label="Second"),
        dcg.Menu(context, parent=second_bar, label="Third"),
        dcg.MenuItem(context, parent=second_bar, label="Fourth"),
    )
    _render(context, count=8)
    # These are the original ImGui positions for the default window style.
    assert (items[0].state.pos_to_viewport.x - window.state.pos_to_viewport.x,
            items[0].state.pos_to_viewport.y - window.state.pos_to_viewport.y
            ) == pytest.approx((4, 31))
    for left, right in zip(items, items[1:]):
        assert right.state.pos_to_viewport.x == pytest.approx(
            left.state.pos_to_viewport.x + left.state.rect_size.x
        )


@pytest.mark.parametrize("item_spacing", ((8, 4), (7, 5)))
@pytest.mark.parametrize("split_bars", (False, True))
@pytest.mark.parametrize("frame_padding", ((4, 3), (6, 5)))
def test_menu_bar_mixed_entries_preserve_native_spacing(
    context: dcg.Context, *, item_spacing: tuple[int, int], split_bars: bool,
    frame_padding: tuple[int, int]
) -> None:
    """Keep native gaps and baseline for the demo's mixed entry sequence."""
    window = dcg.Window(context, primary=True)
    theme = dcg.ThemeStyleImGui(
        context, item_spacing=item_spacing, frame_padding=frame_padding
    )
    first_bar = dcg.MenuBar(context, parent=window, theme=theme)
    second_bar = dcg.MenuBar(context, parent=window, theme=theme) if split_bars else first_bar
    items = (
        dcg.Menu(context, parent=first_bar, label="Documentation"),
        dcg.Menu(context, parent=first_bar, label="p"),
        dcg.Button(context, parent=first_bar, label="Button"),
        dcg.Menu(context, parent=second_bar, label="AM"),
        dcg.MenuItem(context, parent=second_bar, label="Item"),
        dcg.Button(context, parent=second_bar, label="SButton", small=True),
    )
    _render(context, count=8)
    gaps = tuple(
        right.state.pos_to_viewport.x - left.state.pos_to_viewport.x - left.state.rect_size.x
        for left, right in zip(items, items[1:])
    )
    half = item_spacing[0] // 2
    assert gaps == pytest.approx((0, item_spacing[0] - half, half, 0,
                                  item_spacing[0] - half))
    menu_text_y = items[0].state.pos_to_viewport.y + item_spacing[1] // 2
    assert items[2].state.pos_to_viewport.y + frame_padding[1] == pytest.approx(menu_text_y)
    assert items[5].state.pos_to_viewport.y == pytest.approx(menu_text_y)


@pytest.mark.parametrize("height", (0, "filly"))
def test_menu_bar_progress_bar_fits_physical_bar(
    context: dcg.Context, *, height: int | str
) -> None:
    """Keep normal-height and fill-height progress bars inside a primary bar."""
    window = dcg.Window(context, primary=True)
    bar = dcg.MenuBar(context, parent=window)
    dcg.Menu(context, parent=bar, label="File")
    layout = dcg.HorizontalLayout(context, parent=bar, alignment_mode=dcg.Alignment.RIGHT)
    progress = dcg.ProgressBar(context, parent=layout, width=100, height=height)
    _render(context, count=8)
    right_edge = bar.state.content_pos.x + bar.state.content_region_avail.x
    bottom = bar.state.content_pos.y + bar.state.content_region_avail.y
    assert progress.state.pos_to_viewport.y == pytest.approx(bar.state.content_pos.y)
    assert progress.state.pos_to_viewport.y + progress.state.rect_size.y == pytest.approx(bottom)
    assert progress.state.pos_to_viewport.x + progress.state.rect_size.x == pytest.approx(right_edge)


@pytest.mark.parametrize("parent_kind", ("Window", "ChildWindow", "Viewport"))
def test_menu_bar_content_margins_are_symmetric(
    context: dcg.Context, *, parent_kind: str
) -> None:
    """Keep the shared logical right edge symmetric with the content cursor."""
    if parent_kind == "Viewport":
        parent = context.viewport
    else:
        window = dcg.Window(context, width=700, height=500)
        parent = (window if parent_kind == "Window"
                  else dcg.ChildWindow(context, parent=window, width=500, height=250))
    first = dcg.MenuBar(context, parent=parent)
    dcg.Menu(context, parent=first, label="First")
    second = dcg.MenuBar(context, parent=parent)
    dcg.MenuItem(context, parent=second, label="Second")
    _render(context, count=8)
    left = 0 if parent_kind == "Viewport" else parent.state.pos_to_viewport.x
    right = 800 if parent_kind == "Viewport" else left + parent.state.rect_size.x
    first_edge = first.state.content_pos.x + first.state.content_region_avail.x
    second_edge = second.state.content_pos.x + second.state.content_region_avail.x
    assert first.state.content_pos.x - left == pytest.approx(right - first_edge)
    assert second_edge == pytest.approx(first_edge)


@pytest.mark.parametrize("item_spacing", ((8, 4), (7, 5), (12, 4)))
@pytest.mark.parametrize("split_bars", (False, True))
def test_menu_bar_demo_widget_margins_are_symmetric(
    context: dcg.Context, *, item_spacing: tuple[int, int], split_bars: bool
) -> None:
    """Match the first Button's margin with the right-aligned ProgressBar's."""
    window = dcg.Window(context, primary=True)
    theme = dcg.ThemeStyleImGui(context, item_spacing=item_spacing)
    first = dcg.MenuBar(context, parent=window, theme=theme)
    docs = dcg.Layout(context, parent=first)
    button = dcg.Button(context, parent=docs, label="Documentation")
    last = dcg.MenuBar(context, parent=window, theme=theme) if split_bars else first
    status = dcg.HorizontalLayout(
        context, parent=last, alignment_mode=dcg.Alignment.RIGHT, no_wrap=True
    )
    progress = dcg.ProgressBar(context, parent=status, width=100)
    _render(context, count=10)
    left = window.state.pos_to_viewport.x
    right = left + window.state.rect_size.x
    assert button.state.pos_to_viewport.x - left == pytest.approx(
        right - progress.state.pos_to_viewport.x - progress.state.rect_size.x
    )
    assert (last.state.content_pos.x + last.state.content_region_avail.x
            == pytest.approx(first.state.content_pos.x + first.state.content_region_avail.x))


def test_menu_popup_mixed_siblings_do_not_overlap(context: dcg.Context) -> None:
    """Keep vertical cursor advancement correct after padded menu entries."""
    window = dcg.Window(context, width=700, height=500)
    bar = dcg.MenuBar(context, parent=window)
    menu = dcg.Menu(context, parent=bar, label="File")
    items = (
        dcg.MenuItem(context, parent=menu, label="First"),
        dcg.MenuItem(context, parent=menu, label="Second"),
        dcg.Button(context, parent=menu, label="Third"),
        dcg.Menu(context, parent=menu, label="Fourth"),
    )
    _render(context, count=5)
    _open_menu(context, menu)
    for item in items:
        assert item.state.visible
        assert item.state.pos_to_viewport.x == pytest.approx(menu.state.content_pos.x)
    assert items[1].state.pos_to_viewport.y == pytest.approx(
        items[0].state.pos_to_viewport.y + items[0].state.rect_size.y
    )
    for top, bottom in zip(items, items[1:]):
        assert (bottom.state.pos_to_viewport.y >=
                top.state.pos_to_viewport.y + top.state.rect_size.y)


@pytest.mark.parametrize("item_kind", ("Menu", "MenuItem"))
def test_menu_bar_item_string_position_aligns_actual_rect(
    context: dcg.Context, *, item_kind: str
) -> None:
    """Place the padded rectangle at the requested parent-relative position."""
    window = dcg.Window(context, width=700, height=500)
    bar = dcg.MenuBar(context, parent=window)
    item = getattr(dcg, item_kind)(
        context, parent=bar, label="Item", x="parent.x1+40", y="parent.y1+5"
    )
    _render(context, count=8)
    assert tuple(item.state.pos_to_parent) == pytest.approx((40, 5))


@pytest.mark.parametrize("item_kind", ("Menu", "MenuItem"))
@pytest.mark.parametrize("in_popup", (False, True))
def test_menu_item_hover_uses_aligned_rectangle(
    context: dcg.Context, *, item_kind: str, in_popup: bool
) -> None:
    """Make the reported content-origin corner part of the actual hit area."""
    window = dcg.Window(context, width=700, height=500)
    bar = dcg.MenuBar(context, parent=window)
    parent = dcg.Menu(context, parent=bar, label="File") if in_popup else bar
    item = getattr(dcg, item_kind)(context, parent=parent, label="Item")
    _render(context, count=5)
    if in_popup:
        _open_menu(context, parent)
    x, y = item.state.pos_to_viewport
    context.inject_mouse_pos(x + 1, y + 1)
    _render(context, count=2)
    assert item.state.hovered


@pytest.mark.parametrize("item_kind", ("Menu", "MenuItem"))
def test_menu_bar_item_right_alignment_uses_actual_rect(
    context: dcg.Context, *, item_kind: str
) -> None:
    """Align the interaction rectangle with the shared bar's logical edge."""
    window = dcg.Window(context, width=700, height=500)
    bar = dcg.MenuBar(context, parent=window)
    item = getattr(dcg, item_kind)(
        context, parent=bar, label="Item", x="parent.x2-self.width"
    )
    _render(context, count=10)
    right_edge = bar.state.content_pos.x + bar.state.content_region_avail.x
    assert item.state.pos_to_viewport.x + item.state.rect_size.x == pytest.approx(right_edge)


def test_menu_bar_right_alignment_converges_with_preceding_bar(
    context: dcg.Context,
) -> None:
    """Keep right-aligned grouped children inside the physical bar."""
    window = dcg.Window(context, width=700, height=500)
    first = dcg.MenuBar(context, parent=window)
    dcg.Menu(context, parent=first, label="First")
    second = dcg.MenuBar(context, parent=window)
    group = dcg.HorizontalLayout(context, parent=second, x="parent.x2-self.width")
    dcg.Menu(context, parent=group, label="One")
    dcg.Menu(context, parent=group, label="Two")
    positions: list[float] = []
    for _ in range(10):
        _render(context)
        positions.append(group.state.pos_to_viewport.x)
    right_edge = first.state.content_pos.x + first.state.content_region_avail.x
    assert positions[-4:] == pytest.approx([positions[-1]] * 4)
    assert group.state.pos_to_viewport.x + group.state.rect_size.x == pytest.approx(
        right_edge, abs=1
    )
    assert group.state.pos_to_viewport.x > second.state.content_pos.x
    assert tuple(second.state.pos_to_viewport) == pytest.approx(tuple(group.state.pos_to_viewport))
    assert tuple(second.state.rect_size) == pytest.approx(tuple(group.state.rect_size))
    assert second.state.content_pos.x + second.state.content_region_avail.x == pytest.approx(
        right_edge
    )


def test_menu_bar_child_bounds_update_on_hide_and_reposition(context: dcg.Context) -> None:
    """Include repositioned children and drop hidden children from bounds."""
    window = dcg.Window(context, width=700, height=500)
    bar = dcg.MenuBar(context, parent=window)
    first = dcg.Button(context, parent=bar, label="First", width=60)
    second = dcg.Button(context, parent=bar, label="Second", width=80, x="parent.x1-30")
    _render(context, count=8)
    left = min(first.state.pos_to_viewport.x, second.state.pos_to_viewport.x)
    right = max(
        first.state.pos_to_viewport.x + first.state.rect_size.x,
        second.state.pos_to_viewport.x + second.state.rect_size.x,
    )
    assert bar.state.pos_to_viewport.x == pytest.approx(left)
    assert bar.state.rect_size.x == pytest.approx(right - left)
    second.show = False
    _render(context, count=3)
    assert bar.state.pos_to_viewport.x == pytest.approx(first.state.pos_to_viewport.x)
    assert bar.state.rect_size.x == pytest.approx(first.state.rect_size.x)
    first.show = False
    _render(context, count=3)
    assert bar.state.rect_size.x == 0 and not bar.state.hovered


def test_menu_bar_without_children_has_empty_bounds(context: dcg.Context) -> None:
    """Keep an empty contribution at the menu bar insertion point."""
    window = dcg.Window(context, width=700, height=500)
    bar = dcg.MenuBar(context, parent=window)
    _render(context, count=5)
    assert tuple(bar.state.rect_size) == pytest.approx((0, 0))
    assert tuple(bar.state.pos_to_viewport) == pytest.approx(tuple(bar.state.content_pos))
    assert not bar.state.hovered


def test_menu_bar_remaining_area_updates_when_previous_bar_resizes(context: dcg.Context) -> None:
    """Keep the shared right edge stable as preceding items change width."""
    window = dcg.Window(context, width=700, height=500)
    first = dcg.MenuBar(context, parent=window)
    preceding = dcg.Button(context, parent=first, label="First", width=60)
    second = dcg.MenuBar(context, parent=window)
    target = dcg.Button(context, parent=second, label="Right", width=80, x="parent.x2-self.width")
    _render(context, count=8)
    old_start = second.state.content_pos.x
    old_x = target.state.pos_to_viewport.x
    preceding.width = 160
    _render(context, count=8)
    assert second.state.content_pos.x > old_start + 90
    assert target.state.pos_to_viewport.x == pytest.approx(old_x)
    assert target.state.pos_to_viewport.x + target.state.rect_size.x == pytest.approx(
        second.state.content_pos.x + second.state.content_region_avail.x, abs=1
    )


def test_tab_bar_rect_includes_selected_content(context: dcg.Context) -> None:
    """Track selected content size without making it part of header hover."""
    window = dcg.Window(context, width=700, height=500)
    bar = dcg.TabBar(context, parent=window)
    first = dcg.Tab(context, parent=bar, label="First")
    content = dcg.Button(context, parent=first, label="Content", width=170, height=140)
    second = dcg.Tab(context, parent=bar, label="Second")
    dcg.Button(context, parent=second, label="Small", width=70, height=25)
    _render(context, count=8)
    x, y = bar.state.pos_to_viewport
    width, height = bar.state.rect_size
    assert x <= content.state.pos_to_viewport.x
    assert x + width >= content.state.pos_to_viewport.x + content.state.rect_size.x
    assert y + height >= content.state.pos_to_viewport.y + content.state.rect_size.y
    context.inject_mouse_pos(
        content.state.pos_to_viewport.x + 10, content.state.pos_to_viewport.y + 10
    )
    _render(context, count=2)
    assert content.state.hovered and not bar.state.hovered
    second.value = True
    _render(context, count=8)
    assert second.value and bar.state.rect_size.y < height


def test_tab_bar_rect_uses_group_origin_for_repositioned_content(context: dcg.Context) -> None:
    """Keep the group origin when selected content extends above and left."""
    window = dcg.Window(context, width=700, height=500)
    bar = dcg.TabBar(context, parent=window)
    tab = dcg.Tab(context, parent=bar, label="Tab")
    content = dcg.Button(
        context, parent=tab, label="Content", width=80, x="parent.x0-30", y="parent.y0-40"
    )
    other_tab = dcg.Tab(context, parent=bar, label="Other")
    dcg.Button(context, parent=other_tab, label="Other content")
    _render(context, count=8)
    assert content.state.pos_to_viewport.x < tab.state.pos_to_viewport.x
    assert content.state.pos_to_viewport.y < tab.state.pos_to_viewport.y
    origin = tuple(bar.state.pos_to_viewport)
    assert origin[0] > content.state.pos_to_viewport.x
    assert origin[1] > content.state.pos_to_viewport.y
    other_tab.value = True
    _render(context, count=8)
    assert other_tab.value
    assert tuple(bar.state.pos_to_viewport) == pytest.approx(origin)


def test_tab_bar_hidden_table_column_propagates_once(context: dcg.Context) -> None:
    """Clear descendant render states once when a table column skips its items."""
    window = dcg.Window(context, width=700, height=500)
    table = dcg.Table(context, parent=window)
    bar = dcg.TabBar(context)
    tab = dcg.Tab(context, parent=bar, label="Tab")
    content = dcg.Button(context, parent=tab, label="Content")
    table.append_row([bar, "Other column"])
    events: list[str] = []
    tab.handlers = [dcg.LostRenderHandler(context, callback=lambda: events.append("tab"))]
    content.handlers = [dcg.LostRenderHandler(context, callback=lambda: events.append("content"))]
    _render(context, count=8)
    assert bar.state.visible and tab.state.visible and content.state.visible

    table.col_config[0].show = False
    _render(context, count=5)
    context.queue.submit(lambda: None).result(timeout=5)
    assert not bar.state.visible and not tab.state.visible and not content.state.visible
    assert sorted(events) == ["content", "tab"]

    table.col_config[0].show = True
    _render(context, count=8)
    assert bar.state.visible and tab.state.visible and content.state.visible


def test_tab_bar_skipped_after_clipping_clears_children(context: dcg.Context) -> None:
    """Clear traversed tab states even when the bar was already clipped."""
    window = dcg.Window(context, width=700, height=500)
    table = dcg.Table(context, parent=window)
    bar = dcg.TabBar(context, x="parent.x0+1000")
    tab = dcg.Tab(context, parent=bar, label="Tab")
    table.append_row([bar, "Other column"])
    _render(context, count=8)
    assert not bar.state.visible
    assert tab.state.pos_to_viewport.x > 0

    table.col_config[0].show = False
    _render(context, count=5)
    assert tuple(tab.state.pos_to_viewport) == pytest.approx((0, 0))


@pytest.mark.parametrize("axis", ("x", "y"))
def test_fill_position_uses_remaining_length(
    context: dcg.Context, *, axis: str
) -> None:
    """Keep fill as a remaining length even when used in a position."""
    window = dcg.Window(context, width=700, height=500)
    target = dcg.Button(context, parent=window, label="Target", width=80, height=30)
    _render(context, count=5)
    index = 0 if axis == "x" else 1
    expected = window.state.content_region_avail[index] - target.state.pos_to_parent[index]
    expression = dcg.parse_size("fillx" if axis == "x" else "filly")
    setattr(target, axis, expression)
    _render(context)
    assert expression.value == pytest.approx(expected)


@pytest.mark.parametrize("input_method", ("mouse", "keyboard"))
def test_menu_item_activation_for_mouse_and_keyboard(
    context: dcg.Context, *, input_method: str
) -> None:
    """Report one activation for a menu command selected with either input."""
    context.viewport.keyboard_navigation = True
    window = dcg.Window(context, width=700, height=500)
    bar = dcg.MenuBar(context, parent=window)
    menu = dcg.Menu(context, parent=bar, label="File")
    item = dcg.MenuItem(context, parent=menu, label="Choice", check=True)
    events: list[str] = []
    item.handlers = [dcg.ActivatedHandler(context, callback=lambda: events.append("activated"))]
    _render(context, count=6)
    _open_menu(context, menu)
    x, y = item.state.pos_to_viewport
    width, height = item.state.rect_size
    context.inject_mouse_pos(x + width / 2, y + height / 2)
    _render(context, count=2)
    if input_method == "mouse":
        context.inject_mouse_down(dcg.MouseButton.LEFT)
        _render(context)
        assert not item.state.active
        context.inject_mouse_up(dcg.MouseButton.LEFT)
    else:
        context.inject_key_down(dcg.Key.DOWNARROW)
        _render(context)
        context.inject_key_up(dcg.Key.DOWNARROW)
        _render(context, count=2)
        assert item.state.focused
        context.inject_key_down(dcg.Key.SPACE)
    _render(context)
    assert item.value and item.state.active
    context.queue.submit(lambda: None).result(timeout=5)
    assert events == ["activated"]
    if input_method == "keyboard":
        context.inject_key_up(dcg.Key.SPACE)
        _render(context)


def test_window_advertised_toggle_on_expand(context: dcg.Context) -> None:
    """Observe a collapsed window expanding through its title-bar control."""
    window = dcg.Window(context, width=400, height=300, label="Window")
    if not hasattr(window.state, "toggled"):
        pytest.skip("Window does not advertise toggled")
    _render(context, count=5)
    x, y = window.state.pos_to_viewport
    context.inject_mouse_pos(x + 12, y + 12)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context, count=2)
    assert window.collapsed, "the title-bar interaction must collapse the window"
    x, y = window.state.pos_to_viewport
    context.inject_mouse_pos(x + 100, y + 100)
    _render(context, count=2)
    context.inject_mouse_pos(x + 12, y + 12)
    _render(context, count=2)
    context.inject_mouse_down(dcg.MouseButton.LEFT)
    _render(context)
    observed = window.state.toggled
    context.inject_mouse_up(dcg.MouseButton.LEFT)
    _render(context)
    observed |= window.state.toggled
    _render(context)
    observed |= window.state.toggled
    assert not window.collapsed, "the title-bar interaction must expand the window"
    assert observed, "Window advertises toggled but did not report expansion"


def test_window_layout_advertised_geometry(context: dcg.Context) -> None:
    """Observe window-layout geometry with a visible window child."""
    layout = dcg.WindowLayout(context, width=500, height=400)
    window = dcg.Window(context, parent=layout, width=200, height=150, label="Child")
    _render(context, count=5)
    assert window.state.visible, "the window-layout child must be visible"
    size = layout.state.rect_size
    content = layout.state.content_region_avail
    assert size.x > 0 and size.y > 0, "WindowLayout advertised an empty rectangle"
    assert content.x > 0 and content.y > 0, "WindowLayout advertised an empty content area"
    before = layout.state.pos_to_viewport
    layout.x = 40
    _render(context, count=5)
    assert layout.state.pos_to_viewport.x - before.x == pytest.approx(40, abs=1)


def test_tooltip_advertised_content_geometry(context: dcg.Context) -> None:
    """Verify tooltip content coordinates while its target is hovered."""
    window = dcg.Window(context, width=500, height=400)
    target = dcg.Button(context, parent=window, label="Target", width=120, height=30)
    tooltip = dcg.Tooltip(context, parent=window, target=target)
    child = dcg.Text(context, parent=tooltip, value="Tooltip contents")
    _render(context, count=5)
    x, y = target.state.pos_to_viewport
    width, height = target.state.rect_size
    context.inject_mouse_pos(x + width / 2, y + height / 2)
    _render(context, count=5)
    assert target.state.hovered and child.state.visible, "the tooltip must be shown"
    content = tooltip.state.content_pos
    child_pos = child.state.pos_to_viewport
    area = tooltip.state.content_region_avail
    assert content.x == pytest.approx(child_pos.x, abs=1)
    # Text aligns its glyph rectangle to the frame baseline, below the
    # tooltip's layout cursor.
    assert child_pos.y == pytest.approx(content.y + 3, abs=1)
    assert area.x >= 0 and area.y >= 0


@pytest.mark.parametrize(
    "name",
    (
        name for name in _WIDGETS
        if name not in ("Menu", "MenuBar", "MenuItem", "Subplots", "Tab", "TabBar", "TabButton",
                        "Window")
    ),
)
def test_advertised_geometry_tracks_item_motion(context: dcg.Context, *, name: str) -> None:
    """Verify advertised positions change with the item and its rectangle remains meaningful."""
    subject, _ = _make_widget(context, name=name)
    if not hasattr(subject.state, "pos_to_viewport"):
        pytest.skip(f"{name} does not advertise position")
    subject.x = 0
    _render(context, count=5)
    before = subject.state.pos_to_viewport
    parent_before = subject.state.pos_to_parent
    if hasattr(subject.state, "rect_size"):
        size = subject.state.rect_size
        assert size.x > 0 and size.y > 0, f"{name}: advertised rectangle is empty"
    content_before_x: float | None = None
    if hasattr(subject.state, "content_region_avail"):
        area = subject.state.content_region_avail
        assert area.x > 0 and area.y > 0, f"{name}: advertised content area is empty"
        content_before_x = subject.state.content_pos.x

    subject.x = 40
    _render(context, count=5)
    after = subject.state.pos_to_viewport
    parent_after = subject.state.pos_to_parent
    assert after.x - before.x == pytest.approx(40, abs=1), f"{name}: viewport position did not move"
    assert parent_after.x - parent_before.x == pytest.approx(40, abs=1), (
        f"{name}: parent-relative position did not move"
    )
    if content_before_x is not None:
        assert subject.state.content_pos.x - content_before_x == pytest.approx(40, abs=1), (
            f"{name}: content position did not move"
        )
