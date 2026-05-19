import pytest
import dearcygui as dcg

def parse_size(expr):
    # Helper function to parse a size expression
    return dcg.parse_size(expr)

@pytest.fixture
def ctx():
    # Create a minimal context for testing
    C = dcg.Context()
    yield C
    C.queue.shutdown(wait=True)
    C.viewport.destroy()

def test_parse_numeric_literals():
    # Test parsing simple numeric literals
    assert float(parse_size("100")) == 100
    assert float(parse_size("123.5")) == 123.5

def test_parse_keywords():
    # Test parsing built-in keywords
    assert str(parse_size("fillx")) == "fillx"
    assert str(parse_size("filly")) == "filly"
    assert str(parse_size("fullx")) == "fullx"
    assert str(parse_size("fully")) == "fully"
    assert str(parse_size("dpi")) == "dpi"

def test_parse_self_references():
    # Test parsing self references
    assert str(parse_size("self.width")) == "self.width"
    assert str(parse_size("self.height")) == "self.height"
    assert str(parse_size("self.x1")) == "self.x1"
    assert str(parse_size("self.x2")) == "self.x2"
    assert str(parse_size("self.y1")) == "self.y1"
    assert str(parse_size("self.y2")) == "self.y2"
    assert str(parse_size("self.xc")) == "self.xc"
    assert str(parse_size("self.yc")) == "self.yc"

def test_parse_basic_expressions():
    # Test parsing basic arithmetic expressions
    assert str(parse_size("100 + 50")) == "(100.0 + 50.0)"
    assert str(parse_size("100 - 50")) == "(100.0 - 50.0)"
    assert str(parse_size("100 * 0.5")) == "(100.0 * 0.5)"
    assert str(parse_size("100 / 2")) == "(100.0 / 2.0)"
    assert str(parse_size("100 // 3")) == "(100.0 // 3.0)"
    assert str(parse_size("100 % 30")) == "(100.0 % 30.0)"
    assert str(parse_size("10 ** 2")) == "(10.0 ** 2.0)"
    assert str(parse_size("-(100+1)")) == "(-(100.0 + 1.0))"

def test_parse_function_calls():
    # Test parsing function calls
    assert str(parse_size("min(100, 50)")) == "Min(100.0, 50.0)"
    assert str(parse_size("max(100, 50)")) == "Max(100.0, 50.0)"
    assert str(parse_size("abs(-100)")) == "abs((-100.0))"

def test_parse_operator_precedence():
    # Test operator precedence is respected
    # This should be parsed as 1 + (2 * 3) = 7, not (1 + 2) * 3 = 9
    expr = parse_size("1 + 2 * 3")
    assert str(expr) == "(1.0 + (2.0 * 3.0))"
    
    # Test that parentheses override default precedence
    expr = parse_size("(1 + 2) * 3")
    assert str(expr) == "((1.0 + 2.0) * 3.0)"

def test_parse_whitespace_handling():
    # Test that whitespace is handled correctly
    assert str(parse_size("100+50")) == str(parse_size("100 + 50"))
    assert float(parse_size(" 100 ")) == 100
    assert "Min" in str(parse_size("min( 100, 50 )"))

def test_parse_complex_expressions():
    # Test parsing more complex expressions
    expr = parse_size("(100 + 50) * 0.5")
    assert "+" in str(expr)
    assert "*" in str(expr)
    
    # Test a complex expression with functions and keywords
    complex_expr = parse_size("min(100 * dpi, fillx - 20)")
    assert "Min" in str(complex_expr)
    assert "dpi" in str(complex_expr)
    assert "fillx" in str(complex_expr)

def test_size_factory_methods():
    # Test Size factory methods
    assert float(dcg.Size.FIXED(100)) == 100
    assert str(dcg.Size.FILLX()) == "fillx"
    assert str(dcg.Size.FILLY()) == "filly"
    assert str(dcg.Size.FULLX()) == "fullx"
    assert str(dcg.Size.FULLY()) == "fully"
    assert str(dcg.Size.DPI()) == "dpi"
    
    # Test function factories
    assert "Min" in str(dcg.Size.MIN(100, 50))
    assert "Max" in str(dcg.Size.MAX(100, 50))
    assert "abs" in str(dcg.Size.ABS(-100))
    
    # Test with more arguments
    assert "Min" in str(dcg.Size.MIN(100, 50, 25))
    
    # Test from_expression (alias for parse_size)
    assert str(dcg.Size.from_expression("100 + 50")) == "(100.0 + 50.0)"

def test_size_self_reference_factory_methods():
    # Test Size factory methods for self references
    assert str(dcg.Size.SELF_WIDTH()) == "self.width"
    assert str(dcg.Size.SELF_HEIGHT()) == "self.height"
    assert str(dcg.Size.SELF_X1()) == "self.x1"
    assert str(dcg.Size.SELF_X2()) == "self.x2"
    assert str(dcg.Size.SELF_Y1()) == "self.y1"
    assert str(dcg.Size.SELF_Y2()) == "self.y2"
    assert str(dcg.Size.SELF_XC()) == "self.xc"
    assert str(dcg.Size.SELF_YC()) == "self.yc"

def test_size_operation_factory_methods():
    # Test Size factory methods for operations
    assert "+" in str(dcg.Size.ADD(100, 50))
    assert "-" in str(dcg.Size.SUBTRACT(100, 50))
    assert "*" in str(dcg.Size.MULTIPLY(100, 0.5))
    assert "/" in str(dcg.Size.DIVIDE(100, 2))
    assert "//" in str(dcg.Size.FLOOR_DIVIDE(100, 3))
    assert "%" in str(dcg.Size.MODULO(100, 30))
    assert "**" in str(dcg.Size.POWER(10, 2))
    assert "-" in str(dcg.Size.NEGATE(100))
    assert "abs" in str(dcg.Size.ABS(-100))

def test_item_references(ctx):
    # Create UI items to reference
    button = dcg.Button(ctx, label="Test Button")
    
    # Test Size factory methods for item references
    width_ref = dcg.Size.RELATIVEX(button)
    assert "other.width" in str(width_ref)
    
    height_ref = dcg.Size.RELATIVEY(button)
    assert "other.height" in str(height_ref)
    
    # Test coordinate references
    x1_ref = dcg.Size.RELATIVE_X1(button)
    assert "other.x1" in str(x1_ref)
    
    y2_ref = dcg.Size.RELATIVE_Y2(button)
    assert "other.y2" in str(y2_ref)
    
    xc_ref = dcg.Size.RELATIVE_XC(button)
    assert "other.xc" in str(xc_ref)

def test_size_arithmetic_operations():
    # Test arithmetic operations between sizing objects
    size1 = dcg.Size.FIXED(100)
    size2 = dcg.Size.FIXED(50)
    
    assert "+" in str(size1 + size2)
    assert "-" in str(size1 - size2)
    assert "*" in str(size1 * size2)
    assert "/" in str(size1 / size2)
    assert "//" in str(size1 // size2)
    assert "%" in str(size1 % size2)
    assert "**" in str(size1 ** size2)
    assert "-" in str(-size1)
    assert "abs" in str(abs(size1))
    
    # Test with mixed types (sizing object and number)
    assert "+" in str(size1 + 50)
    assert "+" in str(50 + size1)
    assert "*" in str(size1 * 0.5)
    assert "*" in str(2 * size1)

def test_parse_error_handling():
    # Test error handling
    with pytest.raises(ValueError):
        parse_size("")
    
    with pytest.raises(ValueError):
        parse_size("invalid_keyword")
    
    with pytest.raises(ValueError):
        parse_size("100 +")  # Incomplete expression
    
    with pytest.raises(ValueError):
        parse_size("(100 + 50")  # Unclosed parenthesis

def test_size_aliases():
    # Test that Sz is an alias for Size
    assert dcg.Sz is dcg.Size
    assert float(dcg.Sz.FIXED(100)) == 100


# ---------------------------------------------------------------------------
# Shared helpers for rendering tests
# ---------------------------------------------------------------------------

@pytest.fixture
def vp_ctx():
    """Context with initialized, hidden viewport for rendering-based tests."""
    C = dcg.Context()
    C.viewport.initialize(visible=False, width=800, height=600)
    yield C
    C.queue.shutdown(wait=True)
    C.viewport.destroy()


def _render(vp, n=15):
    """Render n frames so that layout sizes stabilize."""
    for _ in range(n):
        vp.render_frame()


def _stable_window(ctx, w=700, h=500):
    """A fixed-size, non-resizable, non-scrolling window for sizing tests."""
    return dcg.Window(
        ctx, label="T",
        width=w, height=h,
        no_resize=True, no_move=True,
        no_scrollbar=True,
    )


def _sizes_converged(sizes, last_n=5):
    """Return True if the last `last_n` entries of `sizes` are all equal."""
    tail = sizes[-last_n:]
    return all(s == tail[0] for s in tail)


def test_widget_sizing_comprehensive(ctx):
    """Comprehensive test of widget sizing with string specifications."""
    viewport = ctx.viewport
    viewport.initialize(visible=False, width=800, height=600)
    window = dcg.Window(ctx, label="Size Test", width="600", height="400")
    
    def get_size(widget, frames=10):
        for _ in range(frames):
            viewport.render_frame()
        return widget.state.rect_size
    
    # Test exact fixed sizes - should be precise for string specifications
    fixed_tests = [
        ("200", 200), ("100", 100), ("50.7", 51),
        ("200 + 50", 250), ("100 * 2", 200), ("min(300, 150)", 150)
    ]
    
    for spec, expected in fixed_tests:
        btn = dcg.Button(ctx, label="Test", width=spec, parent=window)
        w, _ = get_size(btn)
        assert w == expected, f"Size '{spec}': expected {expected}, got {w}"
    
    # Get exact content width for fillx tests
    get_size(dcg.Button(ctx, label="Ref", width="100", parent=window))
    content_w = window.state.content_region_avail[0]
    
    # Test exact fillx behavior
    btn = dcg.Button(ctx, label="Button", width="fillx", parent=window)
    w, _ = get_size(btn)
    assert w == content_w, f"Button fillx should be exact: {w} vs {content_w}"

@pytest.mark.xfail(reason="Text widgets don't support setting their size")
def test_text_fillx_fails(ctx):
    """Text widgets are known to not support fillx correctly."""
    viewport = ctx.viewport
    viewport.initialize(visible=False, width=800, height=600)
    window = dcg.Window(ctx, label="Test", width="600", height="400")
    
    def get_size(widget, frames=10):
        for _ in range(frames):
            viewport.render_frame()
        return widget.state.rect_size[0]
    
    content_w = window.state.content_region_avail[0]
    text = dcg.Text(ctx, value="Text", width="fillx", parent=window)
    w = get_size(text)
    assert w == content_w, f"Text fillx should match content width: {w} vs {content_w}"

# Note: these fails are due to the label and pass if we set an empty one
@pytest.mark.xfail(reason="Slider widgets overshoot with fillx")
def test_slider_fillx_overshoots(ctx):
    """Slider widgets are known to overshoot with fillx."""
    viewport = ctx.viewport
    viewport.initialize(visible=False, width=800, height=600)
    window = dcg.Window(ctx, label="Test", width="600", height="400")
    
    def get_size(widget, frames=10):
        for _ in range(frames):
            viewport.render_frame()
        return widget.state.rect_size[0]
    
    size = dcg.Size.FILLX()
    slider = dcg.Slider(ctx, label="Slider", width=size, parent=window)
    w = get_size(slider)
    content_w = window.state.content_region_avail[0]
    assert content_w == size.value
    assert w == content_w, f"Slider fillx should match content width: {w} vs {content_w}"


@pytest.mark.xfail(reason="InputText widgets overshoot with fillx")
def test_inputtext_fillx_overshoots(ctx):
    """InputText widgets are known to overshoot with fillx."""
    viewport = ctx.viewport
    viewport.initialize(visible=False, width=800, height=600)
    window = dcg.Window(ctx, label="Test", width="600", height="400")
    
    def get_size(widget, frames=10):
        for _ in range(frames):
            viewport.render_frame()
        return widget.state.rect_size[0]
    
    input_text = dcg.InputText(ctx, label="Input", width="fillx", parent=window)
    w = get_size(input_text)
    content_w = window.state.content_region_avail[0]
    assert w == content_w, f"InputText fillx should match content width: {w} vs {content_w}"


@pytest.mark.xfail(reason="ColorEdit widgets overshoot with fillx")
def test_coloredit_fillx_overshoots(ctx):
    """ColorEdit widgets are known to overshoot with fillx."""
    viewport = ctx.viewport
    viewport.initialize(visible=False, width=800, height=600)
    window = dcg.Window(ctx, label="Test", width="600", height="400")
    
    def get_size(widget, frames=10):
        for _ in range(frames):
            viewport.render_frame()
        return widget.state.rect_size[0]

    color_edit = dcg.ColorEdit(ctx, label="Color", width="fillx", parent=window)
    w = get_size(color_edit)
    content_w = window.state.content_region_avail[0]
    assert w == content_w, f"ColorEdit fillx should match content width: {w} vs {content_w}"


@pytest.mark.xfail(reason="Combo widgets overshoot with fillx")
def test_combo_fillx_overshoots(ctx):
    """Combo widgets are known to overshoot with fillx."""
    viewport = ctx.viewport
    viewport.initialize(visible=False, width=800, height=600)
    window = dcg.Window(ctx, label="Test", width="600", height="400")
    
    def get_size(widget, frames=10):
        for _ in range(frames):
            viewport.render_frame()
        return widget.state.rect_size[0]

    combo = dcg.Combo(ctx, items=["A", "B"], label="Combo", width="fillx", parent=window)
    w = get_size(combo)
    content_w = window.state.content_region_avail[0]
    assert w == content_w, f"Combo fillx should match content width: {w} vs {content_w}"


def test_layout_sizing_patterns(ctx):
    """Test exact sizing in different layout contexts."""
    viewport = ctx.viewport
    viewport.initialize(visible=False, width=800, height=600)
    window = dcg.Window(ctx, label="Layout", width="600", height="400")
    
    def get_size(widget, frames=10):
        for _ in range(frames):
            viewport.render_frame()
        return widget.state.rect_size[0]
    
    # Test exact relative sizing
    ref = dcg.Button(ctx, label="Ref", width="200", parent=window)
    rel = dcg.Button(ctx, label="Half", width=dcg.Size.RELATIVEX(ref) * 0.5, parent=window)
    assert get_size(rel) == get_size(ref) / 2, "Relative sizing should be exact"
    
    # Test exact layout container sizing
    with dcg.VerticalLayout(ctx, parent=window):
        v1 = dcg.Button(ctx, label="V1", width="fillx")
        v2 = dcg.Button(ctx, label="V2", width="fillx - 50")
    
    assert get_size(v1) - get_size(v2) == 50, "VBox size difference should be exactly 50"
    
    # Test horizontal layout equal sizing
    with dcg.HorizontalLayout(ctx, parent=window):
        h1 = dcg.Button(ctx, label="H1", width="100")
        h2 = dcg.Button(ctx, label="H2", width="100")
    
    assert get_size(h1) == get_size(h2), "HBox equal sizes should be exact"


def test_sizing_edge_cases(ctx):
    """Test edge cases and exact convergence."""
    viewport = ctx.viewport
    viewport.initialize(visible=False, width=800, height=600)
    window = dcg.Window(ctx, label="Edge", width="600", height="400")
    
    # Test convergence timing - should stabilize quickly
    btn = dcg.Button(ctx, label="Conv", width="fillx - 100", parent=window)
    sizes = [btn.state.rect_size[0] for _ in range(10) if viewport.render_frame() or True]
    
    # Should converge to exact value quickly
    final = sizes[-1]
    converged = next((i for i, s in enumerate(sizes) if s == final), None)
    assert converged is not None and converged <= 3, f"Should converge by frame 3, got frame {converged}"

    # Test exact complex expressions
    content_w = window.state.content_region_avail[0]
    
    # max(100, fillx/4) - should be exactly the larger value
    btn_max = dcg.Button(ctx, label="Max", width="max(100, fillx/4)", parent=window)
    viewport.render_frame()
    expected_max = max(100, content_w / 4)
    assert btn_max.state.rect_size[0] == expected_max, f"max() should be exact: expected {expected_max}"
    
    # min(fillx, 300) - should be exactly the smaller value  
    btn_min = dcg.Button(ctx, label="Min", width="min(fillx, 300)", parent=window)
    viewport.render_frame()
    expected_min = min(content_w, 300)
    assert btn_min.state.rect_size[0] == expected_min, f"min() should be exact: expected {expected_min}"


# ===========================================================================
# HorizontalLayout alignment mode tests
# ===========================================================================

def test_hlayout_left_alignment(vp_ctx):
    """HorizontalLayout LEFT: first item at x=0, items left-to-right."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    with dcg.HorizontalLayout(ctx, parent=window):
        b1 = dcg.Button(ctx, label="", width=80, height=30)
        b2 = dcg.Button(ctx, label="", width=80, height=30)
        b3 = dcg.Button(ctx, label="", width=80, height=30)
    _render(ctx.viewport)

    p1, p2, p3 = [b.state.pos_to_parent[0] for b in (b1, b2, b3)]
    # First item at left edge of layout
    assert p1 == 0, f"LEFT: first item x should be 0, got {p1}"
    # Items ordered left-to-right with no overlap
    assert p1 < p2 < p3
    assert p2 >= p1 + b1.state.rect_size[0]
    assert p3 >= p2 + b2.state.rect_size[0]


def test_hlayout_right_alignment(vp_ctx):
    """HorizontalLayout RIGHT: last item's right edge aligns with content width."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    _render(ctx.viewport)  # stable content width
    content_w = window.state.content_region_avail[0]
    with dcg.HorizontalLayout(ctx, alignment_mode=dcg.Alignment.RIGHT, parent=window):
        b1 = dcg.Button(ctx, label="", width=80, height=30)
        b2 = dcg.Button(ctx, label="", width=80, height=30)
        b3 = dcg.Button(ctx, label="", width=80, height=30)
    _render(ctx.viewport)

    p1, p2, p3 = [b.state.pos_to_parent[0] for b in (b1, b2, b3)]
    # Items ordered left-to-right
    assert p1 < p2 < p3
    # Last item's right edge at the layout content width
    last_right = p3 + b3.state.rect_size[0]
    assert abs(last_right - content_w) <= 1, (
        f"RIGHT: last right {last_right} should be at content_w {content_w}"
    )


def test_hlayout_center_alignment(vp_ctx):
    """HorizontalLayout CENTER: items are centered in the content area."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    _render(ctx.viewport)
    content_w = window.state.content_region_avail[0]
    with dcg.HorizontalLayout(ctx, alignment_mode=dcg.Alignment.CENTER, parent=window):
        b1 = dcg.Button(ctx, label="", width=80, height=30)
        b2 = dcg.Button(ctx, label="", width=80, height=30)
        b3 = dcg.Button(ctx, label="", width=80, height=30)
    _render(ctx.viewport)

    p1 = b1.state.pos_to_parent[0]
    p3 = b3.state.pos_to_parent[0]
    w3 = b3.state.rect_size[0]
    # Center of the items group ≈ center of content area
    group_center = (p1 + p3 + w3) / 2
    assert abs(group_center - content_w / 2) <= 1, (
        f"CENTER: group center {group_center} should ≈ content center {content_w / 2}"
    )
    # Symmetric gaps on both sides
    gap_left = p1
    gap_right = content_w - (p3 + w3)
    assert abs(gap_left - gap_right) <= 1, (
        f"CENTER: gaps should be symmetric, left={gap_left} right={gap_right}"
    )


def test_hlayout_justified_alignment(vp_ctx):
    """HorizontalLayout JUSTIFIED: first at left, last right edge at content width."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    _render(ctx.viewport)
    content_w = window.state.content_region_avail[0]
    with dcg.HorizontalLayout(ctx, alignment_mode=dcg.Alignment.JUSTIFIED, parent=window):
        b1 = dcg.Button(ctx, label="", width=80, height=30)
        b2 = dcg.Button(ctx, label="", width=80, height=30)
        b3 = dcg.Button(ctx, label="", width=80, height=30)
    _render(ctx.viewport)

    p1 = b1.state.pos_to_parent[0]
    p3 = b3.state.pos_to_parent[0]
    w3 = b3.state.rect_size[0]
    # First item at left edge
    assert abs(p1) <= 1, f"JUSTIFIED: first item x should be ≈0, got {p1}"
    # Last item's right edge at content width
    last_right = p3 + w3
    assert abs(last_right - content_w) <= 1, (
        f"JUSTIFIED: last right {last_right} should be at content_w {content_w}"
    )
    # Middle item between first and last
    p2 = b2.state.pos_to_parent[0]
    assert p1 < p2 < p3


def test_hlayout_manual_pixel_positions(vp_ctx):
    """HorizontalLayout MANUAL: items placed at specified pixel positions."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    # Pixel positions are used as-is (no DPI scaling applied to positions list values)
    pos_a, pos_b = 20.0, 200.0
    with dcg.HorizontalLayout(ctx, positions=[pos_a, pos_b], parent=window):
        b1 = dcg.Button(ctx, label="", width=60, height=30)
        b2 = dcg.Button(ctx, label="", width=60, height=30)
    _render(ctx.viewport)

    p1 = b1.state.pos_to_parent[0]
    p2 = b2.state.pos_to_parent[0]
    assert abs(p1 - pos_a) <= 1, f"MANUAL pixel: b1 x={p1} should be ≈{pos_a}"
    assert abs(p2 - pos_b) <= 1, f"MANUAL pixel: b2 x={p2} should be ≈{pos_b}"


def test_hlayout_manual_fractional_positions(vp_ctx):
    """HorizontalLayout MANUAL: fractional positions are relative to layout content width."""
    import math
    ctx = vp_ctx
    window = _stable_window(ctx)
    _render(ctx.viewport)
    content_w = window.state.content_region_avail[0]
    # Fractions 0 < f < 1 are multiplied by content_width and floored
    frac_a, frac_b = 0.1, 0.6
    with dcg.HorizontalLayout(ctx, positions=[frac_a, frac_b], parent=window):
        b1 = dcg.Button(ctx, label="", width=60, height=30)
        b2 = dcg.Button(ctx, label="", width=60, height=30)
    _render(ctx.viewport)

    p1 = b1.state.pos_to_parent[0]
    p2 = b2.state.pos_to_parent[0]
    expected_a = math.floor(frac_a * content_w)
    expected_b = math.floor(frac_b * content_w)
    assert abs(p1 - expected_a) <= 1, f"MANUAL frac: b1 x={p1} should be ≈{expected_a}"
    assert abs(p2 - expected_b) <= 1, f"MANUAL frac: b2 x={p2} should be ≈{expected_b}"


# ===========================================================================
# HorizontalLayout wrapping tests
# ===========================================================================

def test_hlayout_wrapping_enabled(vp_ctx):
    """HorizontalLayout no_wrap=False (default): items wrap to the next row."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    _render(ctx.viewport)
    content_w = window.state.content_region_avail[0]
    # Items wider than half content so 3 can't fit in one row
    item_w = int(content_w * 0.4)
    with dcg.HorizontalLayout(ctx, no_wrap=False, parent=window) as layout:
        b1 = dcg.Button(ctx, label="", width=item_w, height=30)
        b2 = dcg.Button(ctx, label="", width=item_w, height=30)
        b3 = dcg.Button(ctx, label="", width=item_w, height=30)
    _render(ctx.viewport)

    p1_y = b1.state.pos_to_parent[1]
    p3_y = b3.state.pos_to_parent[1]
    # b3 must be on a lower row than b1
    assert p3_y > p1_y, (
        f"Wrap enabled: b3 y={p3_y} should be below b1 y={p1_y}"
    )
    # The layout overall height spans more than one row
    assert layout.state.rect_size[1] > b1.state.rect_size[1], (
        "Layout height should span more than one row"
    )


def test_hlayout_wrapping_disabled(vp_ctx):
    """HorizontalLayout no_wrap=True: all items remain on the same row."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    _render(ctx.viewport)
    content_w = window.state.content_region_avail[0]
    item_w = int(content_w * 0.4)
    with dcg.HorizontalLayout(ctx, no_wrap=True, parent=window):
        b1 = dcg.Button(ctx, label="", width=item_w, height=30)
        b2 = dcg.Button(ctx, label="", width=item_w, height=30)
        b3 = dcg.Button(ctx, label="", width=item_w, height=30)
    _render(ctx.viewport)

    # All items on the same row (y coordinate equal)
    p1_y = b1.state.pos_to_parent[1]
    p2_y = b2.state.pos_to_parent[1]
    p3_y = b3.state.pos_to_parent[1]
    assert p1_y == p2_y == p3_y, (
        f"no_wrap=True: all items on same row, got y={p1_y},{p2_y},{p3_y}"
    )
    # Items still ordered left-to-right even beyond content width
    p1_x, p2_x, p3_x = [b.state.pos_to_parent[0] for b in (b1, b2, b3)]
    assert p1_x < p2_x < p3_x


# ===========================================================================
# VerticalLayout alignment mode tests
# ===========================================================================

def test_vlayout_top_alignment(vp_ctx):
    """VerticalLayout TOP: first item at y=0, items stacked top-to-bottom."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    with dcg.VerticalLayout(ctx, parent=window):
        b1 = dcg.Button(ctx, label="", width=100, height=30)
        b2 = dcg.Button(ctx, label="", width=100, height=30)
        b3 = dcg.Button(ctx, label="", width=100, height=30)
    _render(ctx.viewport)

    p1, p2, p3 = [b.state.pos_to_parent[1] for b in (b1, b2, b3)]
    assert p1 == 0, f"TOP: first item y should be 0, got {p1}"
    assert p1 < p2 < p3
    assert p2 >= p1 + b1.state.rect_size[1]
    assert p3 >= p2 + b2.state.rect_size[1]


def test_vlayout_bottom_alignment(vp_ctx):
    """VerticalLayout BOTTOM: last item's bottom edge aligns with layout content height."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    _render(ctx.viewport)
    with dcg.VerticalLayout(ctx, alignment_mode=dcg.Alignment.BOTTOM, parent=window) as layout:
        b1 = dcg.Button(ctx, label="", width=100, height=30)
        b2 = dcg.Button(ctx, label="", width=100, height=30)
        b3 = dcg.Button(ctx, label="", width=100, height=30)
    _render(ctx.viewport)

    p3 = b3.state.pos_to_parent[1]
    h3 = b3.state.rect_size[1]
    layout_h = layout.state.content_region_avail[1]
    last_bottom = p3 + h3
    assert abs(last_bottom - layout_h) <= 1, (
        f"BOTTOM: last bottom {last_bottom} should ≈ layout height {layout_h}"
    )
    p1, p2 = b1.state.pos_to_parent[1], b2.state.pos_to_parent[1]
    assert p1 < p2 < p3


def test_vlayout_center_alignment(vp_ctx):
    """VerticalLayout CENTER: items are centered vertically."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    _render(ctx.viewport)
    with dcg.VerticalLayout(ctx, alignment_mode=dcg.Alignment.CENTER, parent=window) as layout:
        b1 = dcg.Button(ctx, label="", width=100, height=30)
        b2 = dcg.Button(ctx, label="", width=100, height=30)
        b3 = dcg.Button(ctx, label="", width=100, height=30)
    _render(ctx.viewport)

    p1 = b1.state.pos_to_parent[1]
    p3 = b3.state.pos_to_parent[1]
    h3 = b3.state.rect_size[1]
    layout_h = layout.state.content_region_avail[1]
    group_center = (p1 + p3 + h3) / 2
    assert abs(group_center - layout_h / 2) <= 1, (
        f"CENTER: group center {group_center} should ≈ {layout_h / 2}"
    )
    gap_top = p1
    gap_bottom = layout_h - (p3 + h3)
    assert abs(gap_top - gap_bottom) <= 1, (
        f"CENTER: gaps should be symmetric, top={gap_top} bottom={gap_bottom}"
    )


def test_vlayout_justified_alignment(vp_ctx):
    """VerticalLayout JUSTIFIED: first at top, last bottom edge at layout height."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    _render(ctx.viewport)
    with dcg.VerticalLayout(ctx, alignment_mode=dcg.Alignment.JUSTIFIED, parent=window) as layout:
        b1 = dcg.Button(ctx, label="", width=100, height=30)
        b2 = dcg.Button(ctx, label="", width=100, height=30)
        b3 = dcg.Button(ctx, label="", width=100, height=30)
    _render(ctx.viewport)

    p1 = b1.state.pos_to_parent[1]
    p3 = b3.state.pos_to_parent[1]
    h3 = b3.state.rect_size[1]
    layout_h = layout.state.content_region_avail[1]
    assert abs(p1) <= 1, f"JUSTIFIED: first item y should be ≈0, got {p1}"
    last_bottom = p3 + h3
    assert abs(last_bottom - layout_h) <= 1, (
        f"JUSTIFIED: last bottom {last_bottom} should ≈ layout_h {layout_h}"
    )
    p2 = b2.state.pos_to_parent[1]
    assert p1 < p2 < p3


def test_vlayout_manual_alignment(vp_ctx):
    """VerticalLayout MANUAL: items placed at specified pixel y positions."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    # Pixel positions are used as-is (not DPI-scaled)
    pos_a, pos_b = 10.0, 120.0
    with dcg.VerticalLayout(ctx, positions=[pos_a, pos_b], parent=window):
        b1 = dcg.Button(ctx, label="", width=100, height=30)
        b2 = dcg.Button(ctx, label="", width=100, height=30)
    _render(ctx.viewport)

    p1 = b1.state.pos_to_parent[1]
    p2 = b2.state.pos_to_parent[1]
    assert abs(p1 - pos_a) <= 1, f"MANUAL: b1 y={p1} should be ≈{pos_a}"
    assert abs(p2 - pos_b) <= 1, f"MANUAL: b2 y={p2} should be ≈{pos_b}"


def test_vlayout_wrapping_into_columns(vp_ctx):
    """VerticalLayout wrap=True: items overflow into the next column."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    _render(ctx.viewport)
    content_h = window.state.content_region_avail[1]
    # Items taller than half the content so 3 can't fit in one column
    item_h = int(content_h * 0.4)
    with dcg.VerticalLayout(ctx, wrap=True, parent=window):
        b1 = dcg.Button(ctx, label="", width=80, height=item_h)
        b2 = dcg.Button(ctx, label="", width=80, height=item_h)
        b3 = dcg.Button(ctx, label="", width=80, height=item_h)
    _render(ctx.viewport)

    p1_x = b1.state.pos_to_parent[0]
    p3_x = b3.state.pos_to_parent[0]
    # b3 must be in a new column to the right of b1
    assert p3_x > p1_x, (
        f"wrap=True: b3 x={p3_x} should be in a new column (> b1 x={p1_x})"
    )


# ===========================================================================
# Nested layout stability tests
# ===========================================================================

def test_nested_hlayout_left_in_hlayout_left_stable(vp_ctx):
    """HorizontalLayout(LEFT) inside HorizontalLayout(LEFT): converges quickly."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    with dcg.HorizontalLayout(ctx, parent=window):
        with dcg.HorizontalLayout(ctx) as inner:
            dcg.Button(ctx, label="", width=60, height=30)
            dcg.Button(ctx, label="", width=60, height=30)
        dcg.Button(ctx, label="", width=60, height=30)

    sizes = []
    for _ in range(20):
        ctx.viewport.render_frame()
        sizes.append(inner.state.rect_size)
    assert _sizes_converged(sizes, last_n=5), (
        f"Nested LEFT/LEFT hlayout should stabilize; last: {sizes[-6:]}"
    )


def test_nested_hlayout_left_in_hlayout_center_stable(vp_ctx):
    """HorizontalLayout(LEFT) with fixed children inside HorizontalLayout(CENTER): stable."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    with dcg.HorizontalLayout(ctx, alignment_mode=dcg.Alignment.CENTER, parent=window):
        with dcg.HorizontalLayout(ctx) as inner:
            dcg.Button(ctx, label="", width=60, height=30)
            dcg.Button(ctx, label="", width=60, height=30)

    sizes = []
    for _ in range(20):
        ctx.viewport.render_frame()
        sizes.append(inner.state.rect_size)
    assert _sizes_converged(sizes, last_n=5), (
        f"Nested LEFT inside CENTER should stabilize; last: {sizes[-6:]}"
    )


def test_nested_vlayout_in_hlayout_stable(vp_ctx):
    """VerticalLayout inside HorizontalLayout: stable with fixed-size children."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    with dcg.HorizontalLayout(ctx, parent=window):
        with dcg.VerticalLayout(ctx) as vlay:
            dcg.Button(ctx, label="", width=80, height=25)
            dcg.Button(ctx, label="", width=80, height=25)
        dcg.Button(ctx, label="", width=80, height=30)

    sizes = []
    for _ in range(20):
        ctx.viewport.render_frame()
        sizes.append(vlay.state.rect_size)
    assert _sizes_converged(sizes, last_n=5), (
        f"VerticalLayout inside HorizontalLayout should stabilize; last: {sizes[-6:]}"
    )


def test_nested_hlayout_in_vlayout_stable(vp_ctx):
    """HorizontalLayout inside VerticalLayout: stable with fixed-size children."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    with dcg.VerticalLayout(ctx, parent=window):
        with dcg.HorizontalLayout(ctx) as hlay:
            dcg.Button(ctx, label="", width=80, height=25)
            dcg.Button(ctx, label="", width=80, height=25)
        dcg.Button(ctx, label="", width=80, height=30)

    sizes = []
    for _ in range(20):
        ctx.viewport.render_frame()
        sizes.append(hlay.state.rect_size)
    assert _sizes_converged(sizes, last_n=5), (
        f"HorizontalLayout inside VerticalLayout should stabilize; last: {sizes[-6:]}"
    )


def test_nested_3level_layout_stable(vp_ctx):
    """Three levels of nested layouts stabilize."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    with dcg.HorizontalLayout(ctx, parent=window):
        with dcg.VerticalLayout(ctx):
            with dcg.HorizontalLayout(ctx) as inner_h:
                dcg.Button(ctx, label="", width=60, height=25)
                dcg.Button(ctx, label="", width=60, height=25)
            dcg.Button(ctx, label="", width=60, height=25)
        dcg.Button(ctx, label="", width=60, height=30)

    sizes = []
    for _ in range(25):
        ctx.viewport.render_frame()
        sizes.append(inner_h.state.rect_size)
    assert _sizes_converged(sizes, last_n=5), (
        f"3-level nested layout should stabilize; last: {sizes[-6:]}"
    )


# ===========================================================================
# ChildWindow basic sizing tests
# ===========================================================================

def test_childwindow_fixed_size_with_border(vp_ctx):
    """ChildWindow with explicit size and border=True: rect_size matches request."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    # Use string sizes so they are not DPI-scaled (integer sizes are scaled by dpi)
    cw = dcg.ChildWindow(ctx, width='200', height='150', border=True, parent=window)
    _render(ctx.viewport)

    assert cw.state.rect_size[0] == 200, (
        f"ChildWindow width: expected 200, got {cw.state.rect_size[0]}"
    )
    assert cw.state.rect_size[1] == 150, (
        f"ChildWindow height: expected 150, got {cw.state.rect_size[1]}"
    )


def test_childwindow_fixed_size_without_border(vp_ctx):
    """ChildWindow with explicit size and border=False: rect_size matches request."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    cw = dcg.ChildWindow(ctx, width='200', height='150', border=False, parent=window)
    _render(ctx.viewport)

    assert cw.state.rect_size[0] == 200, (
        f"ChildWindow width: expected 200, got {cw.state.rect_size[0]}"
    )
    assert cw.state.rect_size[1] == 150, (
        f"ChildWindow height: expected 150, got {cw.state.rect_size[1]}"
    )


def test_childwindow_fillx(vp_ctx):
    """ChildWindow with fillx fills the parent's content width."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    _render(ctx.viewport)
    content_w = window.state.content_region_avail[0]

    cw = dcg.ChildWindow(ctx, width="fillx", height=100, parent=window)
    _render(ctx.viewport)
    assert cw.state.rect_size[0] == content_w, (
        f"fillx ChildWindow: expected width {content_w}, got {cw.state.rect_size[0]}"
    )


def test_childwindow_filly(vp_ctx):
    """ChildWindow with filly fills the parent's remaining content height."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    _render(ctx.viewport)
    content_h = window.state.content_region_avail[1]

    cw = dcg.ChildWindow(ctx, width=100, height="filly", parent=window)
    _render(ctx.viewport)
    assert cw.state.rect_size[1] == content_h, (
        f"filly ChildWindow: expected height {content_h}, got {cw.state.rect_size[1]}"
    )


# ===========================================================================
# ChildWindow border vs. no-border content area tests
# ===========================================================================

def test_childwindow_border_shrinks_content(vp_ctx):
    """ChildWindow with border: content_region_avail < rect_size."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    cw = dcg.ChildWindow(ctx, width='200', height='150', border=True, parent=window)
    _render(ctx.viewport)

    w, h = cw.state.rect_size
    cw_x, cw_y = cw.state.content_region_avail
    assert cw_x < w, f"Border: content_w {cw_x} should be < rect_w {w}"
    assert cw_y < h, f"Border: content_h {cw_y} should be < rect_h {h}"


def test_childwindow_no_border_full_content(vp_ctx):
    """ChildWindow without border: content_region_avail equals rect_size."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    cw = dcg.ChildWindow(ctx, width='200', height='150', border=False, parent=window)
    _render(ctx.viewport)

    w, h = cw.state.rect_size
    cw_x, cw_y = cw.state.content_region_avail
    assert cw_x == w, f"No-border: content_w {cw_x} should == rect_w {w}"
    assert cw_y == h, f"No-border: content_h {cw_y} should == rect_h {h}"


def test_childwindow_border_vs_no_border_same_outer_size(vp_ctx):
    """Same outer size: bordered ChildWindow has smaller content area."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    cw_border    = dcg.ChildWindow(ctx, width='200', height='100', border=True,  parent=window)
    cw_no_border = dcg.ChildWindow(ctx, width='200', height='100', border=False, parent=window)
    _render(ctx.viewport)

    # Same outer sizes
    assert cw_border.state.rect_size[0]    == cw_no_border.state.rect_size[0] == 200
    assert cw_border.state.rect_size[1]    == cw_no_border.state.rect_size[1] == 100
    # Bordered → smaller content area
    assert cw_border.state.content_region_avail[0] < cw_no_border.state.content_region_avail[0]
    assert cw_border.state.content_region_avail[1] < cw_no_border.state.content_region_avail[1]


def test_childwindow_always_use_window_padding(vp_ctx):
    """always_use_window_padding adds padding to a borderless ChildWindow."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    cw_padded = dcg.ChildWindow(
        ctx, width='200', height='100',
        border=False, always_use_window_padding=True,
        parent=window,
    )
    cw_plain = dcg.ChildWindow(
        ctx, width='200', height='100',
        border=False, always_use_window_padding=False,
        parent=window,
    )
    _render(ctx.viewport)

    # Same outer size
    assert cw_padded.state.rect_size[0] == cw_plain.state.rect_size[0] == 200
    # Padded one has smaller content area
    assert cw_padded.state.content_region_avail[0] < cw_plain.state.content_region_avail[0]
    assert cw_padded.state.content_region_avail[1] < cw_plain.state.content_region_avail[1]


# ===========================================================================
# Nested ChildWindow tests (with and without borders)
# ===========================================================================

def test_nested_childwindow_both_bordered(vp_ctx):
    """Two bordered ChildWindows nested: each has its own requested rect_size."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    outer = dcg.ChildWindow(ctx, width='300', height='200', border=True,  parent=window)
    inner = dcg.ChildWindow(ctx, width='100', height='80',  border=True,  parent=outer)
    _render(ctx.viewport)

    assert outer.state.rect_size == (300, 200)
    assert inner.state.rect_size == (100, 80)
    # Inner has a border: its content area is smaller
    assert inner.state.content_region_avail[0] < 100
    assert inner.state.content_region_avail[1] < 80
    # Inner fits within outer's content area
    outer_cw, outer_ch = outer.state.content_region_avail
    assert inner.state.rect_size[0] <= outer_cw
    assert inner.state.rect_size[1] <= outer_ch


def test_nested_childwindow_both_no_border(vp_ctx):
    """Two borderless ChildWindows nested: both have full content regions."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    outer = dcg.ChildWindow(ctx, width='300', height='200', border=False, parent=window)
    inner = dcg.ChildWindow(ctx, width='120', height='90',  border=False, parent=outer)
    _render(ctx.viewport)

    assert outer.state.rect_size == (300, 200)
    assert inner.state.rect_size == (120, 90)
    # No-border: content == outer size
    assert inner.state.content_region_avail[0] == 120
    assert inner.state.content_region_avail[1] == 90


def test_nested_childwindow_outer_bordered_inner_not(vp_ctx):
    """Outer bordered, inner not: inner fills its content fully."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    outer = dcg.ChildWindow(ctx, width='300', height='200', border=True,  parent=window)
    inner = dcg.ChildWindow(ctx, width='100', height='60',  border=False, parent=outer)
    _render(ctx.viewport)

    # Outer's content area is reduced by border/padding
    assert outer.state.content_region_avail[0] < 300
    # Inner fits within outer
    assert inner.state.rect_size[0] <= outer.state.content_region_avail[0]
    # Inner (no border): content == rect_size
    assert inner.state.content_region_avail[0] == inner.state.rect_size[0]
    assert inner.state.content_region_avail[1] == inner.state.rect_size[1]


def test_nested_childwindow_outer_not_inner_bordered(vp_ctx):
    """Outer not bordered, inner bordered: inner's content is reduced."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    outer = dcg.ChildWindow(ctx, width='300', height='200', border=False, parent=window)
    inner = dcg.ChildWindow(ctx, width='100', height='60',  border=True,  parent=outer)
    _render(ctx.viewport)

    # Outer has no border: its content fills its rect
    assert outer.state.content_region_avail == (300, 200)
    # Inner rect_size matches request
    assert inner.state.rect_size == (100, 60)
    # Inner content is reduced by its border
    assert inner.state.content_region_avail[0] < 100
    assert inner.state.content_region_avail[1] < 60


def test_nested_childwindow_three_levels(vp_ctx):
    """Three-level nesting: each ChildWindow keeps its requested rect_size."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    outer  = dcg.ChildWindow(ctx, width='400', height='300', border=True,  parent=window)
    middle = dcg.ChildWindow(ctx, width='200', height='150', border=False, parent=outer)
    inner  = dcg.ChildWindow(ctx, width='80',  height='60',  border=True,  parent=middle)
    _render(ctx.viewport)

    assert outer.state.rect_size  == (400, 300)
    assert middle.state.rect_size == (200, 150)
    assert inner.state.rect_size  == (80, 60)
    # middle (no border): content == rect_size
    assert middle.state.content_region_avail[0] == 200
    assert middle.state.content_region_avail[1] == 150
    # inner (border): content < rect_size
    assert inner.state.content_region_avail[0] < 80
    assert inner.state.content_region_avail[1] < 60


def test_nested_childwindow_fillx_in_bordered(vp_ctx):
    """fillx inner ChildWindow fills the bordered outer's content area."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    outer = dcg.ChildWindow(ctx, width='300', height='200', border=True, parent=window)
    _render(ctx.viewport)
    outer_content_w = outer.state.content_region_avail[0]

    inner = dcg.ChildWindow(ctx, width="fillx", height='50', border=False, parent=outer)
    _render(ctx.viewport)
    assert inner.state.rect_size[0] == outer_content_w, (
        f"fillx inner: expected {outer_content_w}, got {inner.state.rect_size[0]}"
    )


# ===========================================================================
# Layout inside ChildWindow tests
# ===========================================================================

def test_hlayout_content_width_matches_childwindow(vp_ctx):
    """HorizontalLayout inside ChildWindow: layout content width = ChildWindow content width."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    cw = dcg.ChildWindow(ctx, width='300', height='150', border=True, parent=window)
    _render(ctx.viewport)
    cw_content_w = cw.state.content_region_avail[0]

    with dcg.HorizontalLayout(ctx, parent=cw) as hlay:
        dcg.Button(ctx, label="", width=60, height=25)
        dcg.Button(ctx, label="", width=60, height=25)
    _render(ctx.viewport)

    assert abs(hlay.state.content_region_avail[0] - cw_content_w) <= 1, (
        f"HLayout content_w {hlay.state.content_region_avail[0]} should ≈ "
        f"ChildWindow content_w {cw_content_w}"
    )


def test_hlayout_right_in_childwindow(vp_ctx):
    """HorizontalLayout RIGHT inside ChildWindow: items aligned to ChildWindow content edge."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    cw = dcg.ChildWindow(ctx, width='300', height='150', border=True, parent=window)
    _render(ctx.viewport)
    cw_content_w = cw.state.content_region_avail[0]

    with dcg.HorizontalLayout(ctx, alignment_mode=dcg.Alignment.RIGHT, parent=cw):
        b1 = dcg.Button(ctx, label="", width=60, height=25)
        b2 = dcg.Button(ctx, label="", width=60, height=25)
    _render(ctx.viewport)

    last_right = b2.state.pos_to_parent[0] + b2.state.rect_size[0]
    assert abs(last_right - cw_content_w) <= 1, (
        f"RIGHT in ChildWindow: last right {last_right} should ≈ content_w {cw_content_w}"
    )


def test_justified_hlayout_in_childwindow(vp_ctx):
    """JUSTIFIED HorizontalLayout in ChildWindow: first at left, last at right edge."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    cw = dcg.ChildWindow(ctx, width='300', height='80', border=True, parent=window)
    _render(ctx.viewport)
    cw_content_w = cw.state.content_region_avail[0]

    with dcg.HorizontalLayout(ctx, alignment_mode=dcg.Alignment.JUSTIFIED, parent=cw):
        b1 = dcg.Button(ctx, label="", width=60, height=25)
        b2 = dcg.Button(ctx, label="", width=60, height=25)
    _render(ctx.viewport)

    p1 = b1.state.pos_to_parent[0]
    last_right = b2.state.pos_to_parent[0] + b2.state.rect_size[0]
    assert abs(p1) <= 1, f"JUSTIFIED in CW: first item x should be ≈0, got {p1}"
    assert abs(last_right - cw_content_w) <= 1, (
        f"JUSTIFIED in CW: last right {last_right} should ≈ {cw_content_w}"
    )


def test_vlayout_in_childwindow_stable(vp_ctx):
    """VerticalLayout inside ChildWindow: sizes converge quickly."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    cw = dcg.ChildWindow(ctx, width='200', height='300', border=False, parent=window)
    with dcg.VerticalLayout(ctx, parent=cw) as vlay:
        dcg.Button(ctx, label="", width=100, height=30)
        dcg.Button(ctx, label="", width=100, height=30)

    sizes = []
    for _ in range(20):
        ctx.viewport.render_frame()
        sizes.append(vlay.state.rect_size)
    assert _sizes_converged(sizes, last_n=5), (
        f"VerticalLayout in ChildWindow should stabilize; last: {sizes[-6:]}"
    )


# ===========================================================================
# ChildWindow inside Layout tests
# ===========================================================================

def test_childwindow_in_hlayout_keeps_size(vp_ctx):
    """ChildWindow inside HorizontalLayout: ChildWindow gets its requested size."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    with dcg.HorizontalLayout(ctx, parent=window):
        cw  = dcg.ChildWindow(ctx, width='150', height='80', border=True)
        dcg.Button(ctx, label="", width=80, height=80)
    _render(ctx.viewport)

    assert cw.state.rect_size[0] == 150, (
        f"ChildWindow in HLayout: width {cw.state.rect_size[0]} should be 150"
    )
    assert cw.state.rect_size[1] == 80, (
        f"ChildWindow in HLayout: height {cw.state.rect_size[1]} should be 80"
    )


def test_childwindow_in_vlayout_keeps_size(vp_ctx):
    """ChildWindow inside VerticalLayout: ChildWindow gets its requested size."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    with dcg.VerticalLayout(ctx, parent=window):
        cw = dcg.ChildWindow(ctx, width='150', height='80', border=False)
        dcg.Button(ctx, label="", width=150, height=30)
    _render(ctx.viewport)

    assert cw.state.rect_size[0] == 150
    assert cw.state.rect_size[1] == 80


def test_nested_childwindow_in_layout_in_childwindow(vp_ctx):
    """Deep nesting: ChildWindow → Layout → ChildWindow keeps inner rect_size."""
    ctx = vp_ctx
    window = _stable_window(ctx)
    outer_cw = dcg.ChildWindow(ctx, width='350', height='250', border=True, parent=window)
    with dcg.HorizontalLayout(ctx, alignment_mode=dcg.Alignment.CENTER, parent=outer_cw):
        inner_cw = dcg.ChildWindow(ctx, width='100', height='80', border=True)
    _render(ctx.viewport)

    assert inner_cw.state.rect_size[0] == 100
    assert inner_cw.state.rect_size[1] == 80