#!/usr/bin/env python3
"""
Print-production label generator for Food Festival products.

Generates CMYK-correct print-ready files with:
  - Correct physical dimensions: 200×100mm (4900-5000g) and 120×70mm (830g)
  - 3mm bleeds on every side with crop marks
  - Solid-color backgrounds (no transparency/masks)
  - Two variants per label:
      .ai  — CMYK PDF 1.4, fonts embedded (for Illustrator/prepress)
      .pdf — CMYK PDF 1.4, text as outlines (for RIP/print)

Requirements: pip install pillow numpy  (or use: .venv/bin/python3 build_print_labels.py)
"""

import os, sys, base64, html as H, io, random as _random, shutil, subprocess, tempfile
from dataclasses import dataclass, field, replace
from typing import Optional

try:
    from PIL import Image, ImageFont
    import numpy as np
except ImportError:
    sys.exit("ERROR: missing dependencies. Run: .venv/bin/pip install pillow numpy")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_labels import PRODUCTS, load_logo_white
from add_barcodes_and_export import BARCODES, ean13_svg

BASE      = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE, "food festival logo.png")
ICONS_DIR = os.path.join(BASE, "icons")
FONTS_DIR = os.path.join(BASE, "output_svg", "fonts")
FONT_R    = os.path.join(FONTS_DIR, "Ubuntu-R.ttf")
FONT_B    = os.path.join(FONTS_DIR, "Ubuntu-B.ttf")
OUT_DIR   = os.path.join(BASE, "output_print_v2")
BLEED     = 3.0   # mm

BG_ICON = {
    "01_sauce_bbq":            "icon-flame",
    "02_ketchup_classic_5kg":  "icon-tomato",
    "03_mayo_67":              "icon-egg",
    "04_mayo_real":            "icon-egg",
    "05_tomato_pasta":         "icon-tomato",
    "06_ketchup_premium":      "icon-tomato",
    "07_ketchup_shashlik_830": "icon-drumstick",
    "08_ketchup_shashlik_5kg": "icon-drumstick",
    "09_sauce_cheese":         "icon-cheese",
    "10_mustard_american":     "icon-leaf",
    "11_ketchup_classic_830":  "icon-tomato",
}

SVG_ICON_DEFS = """
  <symbol id="icon-flame" viewBox="0 0 100 100" overflow="visible">
    <path d="M50,88 C22,68 14,44 32,28 C30,42 40,48 44,38 C40,22 52,5 50,3
             C64,18 80,40 68,55 C74,44 77,32 72,25 C87,44 85,68 50,88Z"/>
  </symbol>
  <symbol id="icon-tomato" viewBox="0 0 100 100" overflow="visible">
    <circle cx="50" cy="58" r="36"/>
    <ellipse cx="50" cy="22" rx="5" ry="10"/>
    <ellipse cx="40" cy="26" rx="9" ry="5" transform="rotate(-30,40,26)"/>
    <ellipse cx="60" cy="26" rx="9" ry="5" transform="rotate(30,60,26)"/>
  </symbol>
  <symbol id="icon-egg" viewBox="0 0 100 100" overflow="visible">
    <ellipse cx="50" cy="54" rx="30" ry="42"/>
  </symbol>
  <symbol id="icon-drumstick" viewBox="0 0 100 100" overflow="visible">
    <ellipse cx="66" cy="30" rx="28" ry="26"/>
    <path d="M54,52 L36,78 C28,82 22,90 26,96 C30,102 40,100 44,93
             C48,86 44,80 52,74 L70,48Z"/>
    <circle cx="31" cy="86" r="13"/>
  </symbol>
  <symbol id="icon-cheese" viewBox="0 0 100 100" overflow="visible">
    <path d="M8,84 L92,84 L50,16Z"/>
    <circle cx="40" cy="68" r="7"/>
    <circle cx="62" cy="57" r="5"/>
  </symbol>
  <symbol id="icon-leaf" viewBox="0 0 100 100" overflow="visible">
    <path d="M50,90 C16,72 12,32 50,8 C88,32 84,72 50,90Z M53,8 L53,90 L47,90 L47,8Z"
          fill-rule="evenodd"/>
  </symbol>
"""

# ── Format specifications ─────────────────────────────────────────────────────

@dataclass
class FormatSpec:
    name: str
    trim_w: float          # mm trim width
    trim_h: float          # mm trim height
    # Canvas = trim + 2*BLEED
    # All layout coords below are canvas-relative (mm)
    lp_x1: float; lp_x2: float   # left panel x bounds
    np_x1: float; np_x2: float   # nutrition panel x bounds
    rp_x1: float; rp_x2: float   # right panel x bounds
    ds_x1: float; ds_x2: float   # date strip x bounds
    # Typography (mm)
    fs_body: float    # body text (ingredients, storage…)
    fs_hdr: float     # section headers
    fs_note: float    # small notes
    fs_nutr: float    # nutrition table
    lh_body: float    # body line height
    lh_hdr: float     # header + gap below
    # Right panel
    fs_cat: float     # category font
    fs_mass: float    # mass netto font
    # Logo max height (mm) for right panel
    logo_h: float

    def scaled_typo(self, scale: float) -> "FormatSpec":
        """Return a copy with all typography values multiplied by scale."""
        return replace(self,
            fs_body=self.fs_body * scale,
            fs_hdr=self.fs_hdr * scale,
            fs_note=self.fs_note * scale,
            lh_body=self.lh_body * scale,
            lh_hdr=self.lh_hdr * scale,
        )

    @property
    def canvas_w(self): return self.trim_w + 2 * BLEED
    @property
    def canvas_h(self): return self.trim_h + 2 * BLEED
    @property
    def lp_cx(self): return (self.lp_x1 + self.lp_x2) / 2
    @property
    def np_cx(self): return (self.np_x1 + self.np_x2) / 2
    @property
    def rp_cx(self): return (self.rp_x1 + self.rp_x2) / 2
    @property
    def ds_cx(self): return (self.ds_x1 + self.ds_x2) / 2

# Canvas coords: 0 = left/top bleed edge; 3 = trim start; canvas_w-3 = trim end
LARGE = FormatSpec(
    name="large", trim_w=200, trim_h=100,
    # Panels proportional to old 1178×594 px layout
    lp_x1=3,   lp_x2=88,    # 85mm wide
    np_x1=90,  np_x2=124,   # 34mm wide
    rp_x1=127, rp_x2=198,   # 71mm wide (right of divider to date strip)
    ds_x1=198, ds_x2=203,   # 5mm date strip
    fs_body=1.95, fs_hdr=2.05, fs_note=1.7, fs_nutr=1.55,
    lh_body=2.45, lh_hdr=4.5,
    fs_cat=3.4, fs_mass=2.2,
    logo_h=34,
)

SMALL = FormatSpec(
    name="small", trim_w=120, trim_h=70,
    # Proportionally scaled (×0.60 in X, ×0.70 in Y), keeping same visual ratios
    lp_x1=3,  lp_x2=54,     # 51mm wide
    np_x1=55, np_x2=74,     # 19mm wide
    rp_x1=75, rp_x2=117,   # 42mm wide
    ds_x1=117, ds_x2=123,  # 6mm date strip
    fs_body=1.6, fs_hdr=1.7, fs_note=1.4, fs_nutr=1.35,
    lh_body=1.95, lh_hdr=3.5,
    fs_cat=2.8, fs_mass=1.9,
    logo_h=22,
)

# ── Color utilities ───────────────────────────────────────────────────────────

def composite(fg, alpha, bg):
    """Pre-composite fg (RGB tuple) at alpha over bg, returning solid RGB tuple."""
    return tuple(round(f * alpha + b * (1 - alpha)) for f, b in zip(fg, bg))

def css(c):
    """RGB tuple → CSS rgb() string."""
    return f"rgb({c[0]},{c[1]},{c[2]})"

def hexc(c):
    """RGB tuple → hex color string."""
    return f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}"

def bg_color(p):
    """Compute solid background base color for product p."""
    if p.get("bg_dark"):
        return p["bg_dark"]
    return tuple(int(c * 0.25) for c in p["accent"])

# ── Font / text helpers ───────────────────────────────────────────────────────

_font_cache = {}

MM_PER_PT = 25.4 / 72.0    # 1pt = 0.353mm → 1mm = 2.835pt
PT_PER_MM = 72.0 / 25.4    # for converting mm → Pillow px

def _pf(path, size_mm):
    """Load Pillow font at given physical size (mm)."""
    size_px = max(1, round(size_mm * PT_PER_MM))
    k = (path, size_px)
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(path, size_px)
    return _font_cache[k]

def text_width_mm(text, path, size_mm):
    """Measure text width in mm using Pillow."""
    px = _pf(path, size_mm).getlength(text)
    return px / PT_PER_MM

def wrap_mm(text, path, size_mm, max_w_mm):
    """Word-wrap text to fit within max_w_mm, returns list of line strings."""
    font   = _pf(path, size_mm)
    max_px = max_w_mm * PT_PER_MM
    words  = text.split()
    lines, line = [], ""
    for word in words:
        candidate = f"{line} {word}".strip() if line else word
        if font.getlength(candidate) <= max_px:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def svgt(x, y_top, text, fs_mm, fill_color, bold=False, anchor="start",
         letter_spacing=None, transform=None, italic=False):
    """Single SVG <text> element. y_top = visual top of text (mm).
    Returns SVG element string."""
    baseline_y = y_top + fs_mm * 0.78
    fw = "bold" if bold else "normal"
    fs_ = "italic" if italic else "normal"
    ls  = f' letter-spacing="{letter_spacing}"' if letter_spacing else ""
    tr  = f' transform="{transform}"' if transform else ""
    return (f'<text x="{x:.3f}" y="{baseline_y:.3f}" '
            f'font-family="Ubuntu,sans-serif" font-size="{fs_mm}" '
            f'font-weight="{fw}" font-style="{fs_}" '
            f'fill="{fill_color}" text-anchor="{anchor}"{ls}{tr}>'
            f'{H.escape(text)}</text>')

def svgt_styled(cx, y_top, words, fs_mm, fill_color, bold_wds=None):
    """SVG <text> with per-word <tspan> bold styling, centered at cx."""
    baseline_y = y_top + fs_mm * 0.78
    parts = []
    for wd in words:
        escaped = H.escape(wd)
        clean   = wd.rstrip('.,;:()')
        if bold_wds and clean in bold_wds:
            parts.append(f'<tspan font-weight="bold">{escaped}</tspan>')
        else:
            parts.append(escaped)
    content = ' '.join(parts)
    return (f'<text x="{cx:.3f}" y="{baseline_y:.3f}" '
            f'font-family="Ubuntu,sans-serif" font-size="{fs_mm}" '
            f'font-weight="normal" fill="{fill_color}" text-anchor="middle">'
            f'{content}</text>')

# ── Logo & icon loading ───────────────────────────────────────────────────────

_logo_cache = {}

def load_logo_b64(max_h_px=600):
    """Load brand logo as base64 PNG (white content on transparent bg)."""
    if max_h_px in _logo_cache:
        return _logo_cache[max_h_px]
    img = load_logo_white(LOGO_PATH)
    new_w = round(img.width / img.height * max_h_px)
    img = img.resize((new_w, max_h_px), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    result = (img.size, f"data:image/png;base64,{b64}")
    _logo_cache[max_h_px] = result
    return result

_icon_cache = {}

def load_icon_b64(filename, target_h_px):
    """Load icon as base64 PNG: strips white background, inverts to white-on-transparent."""
    k = (filename, target_h_px)
    if k in _icon_cache:
        return _icon_cache[k]
    path = os.path.join(ICONS_DIR, filename)
    img  = Image.open(path).convert("RGBA")
    arr  = np.array(img)
    white_mask = (arr[:,:,0] > 215) & (arr[:,:,1] > 215) & (arr[:,:,2] > 215)
    arr[white_mask, 3]  = 0
    arr[~white_mask, :3] = 255
    img  = Image.fromarray(arr, "RGBA")
    nw   = round(img.width / img.height * target_h_px)
    img  = img.resize((nw, target_h_px), Image.LANCZOS)
    buf  = io.BytesIO()
    img.save(buf, "PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    result = (nw, target_h_px, f"data:image/png;base64,{b64}")
    _icon_cache[k] = result
    return result

def default_icons(weight_str):
    if int(weight_str) >= 4000:
        return ["icon_foodsafe.png", "icon_trash.jpeg", "icon_pp05.png", "icon_bez_gmo.png"]
    return ["icon_foodsafe.png", "icon_trash.jpeg", "icon_pet01.png",
            "icon_hdpe02.png", "icon_bez_gmo.png"]

# ── Emoji background texture ──────────────────────────────────────────────────

def emoji_layer_svg(key, fmt):
    """Deterministic decorative vector icon texture, clipped to label canvas."""
    icon_id = BG_ICON.get(key, "")
    if not icon_id:
        return ""
    cw, ch = fmt.canvas_w, fmt.canvas_h
    scale  = 1178 / cw
    sz_lo  = round(250 / scale)
    sz_hi  = round(310 / scale)
    min_d2 = sz_hi ** 2
    rng    = _random.Random(hash(key) & 0xFFFFFFFF)
    placed, uses = [], []
    for _ in range(5):
        candidate = (rng.uniform(0, cw), rng.uniform(0, ch))
        best_score = 0
        for _ in range(400):
            cx2, cy2 = rng.uniform(0, cw), rng.uniform(0, ch)
            score = min((cx2-px)**2+(cy2-py)**2 for px, py in placed) if placed else min_d2
            if score >= min_d2:
                candidate = (cx2, cy2)
                break
            if score > best_score:
                best_score, candidate = score, (cx2, cy2)
        placed.append(candidate)
        rot = rng.uniform(-35, 35)
        sz  = rng.randint(sz_lo, sz_hi)
        cx2, cy2 = candidate
        uses.append(
            f'  <use xlink:href="#{icon_id}" '
            f'x="{cx2 - sz/2:.2f}" y="{cy2 - sz/2:.2f}" '
            f'width="{sz}" height="{sz}" '
            f'transform="rotate({rot:.1f},{cx2:.2f},{cy2:.2f})"/>'
        )
    inner = "\n".join(uses)
    return f'<g fill="white" opacity="0.12" clip-path="url(#label-clip)">\n{inner}\n</g>'

# ── Left panel typography auto-fit ───────────────────────────────────────────

def measure_left_panel_height(p, fmt):
    """Simulate left_panel_svg layout and return total height needed (mm)."""
    wrap_w = (fmt.lp_x2 - fmt.lp_x1) - 5
    total  = 0.0

    sections = [
        p["ingredients"],
        p["storage"],
        p["address"],
        p["manufacturer"],
    ]
    if p.get("commission"):
        sections.append(p["commission"])

    for body_text in sections:
        total += fmt.lh_hdr
        total += len(wrap_mm(body_text, FONT_R, fmt.fs_body, wrap_w)) * fmt.lh_body

    note = "Дата «Краще спожити до» та номер партії (L) вказані на етикетці."
    total += fmt.fs_note * 0.5
    total += len(wrap_mm(note, FONT_R, fmt.fs_note, wrap_w)) * fmt.fs_note * 1.4
    return total

def fit_left_panel_typo(p, fmt, available_h):
    """Return a FormatSpec with typography scaled to fit available_h.
    Uses binary search so scaled font is as large as possible while fitting."""
    if measure_left_panel_height(p, fmt) <= available_h:
        return fmt
    # Binary search: find largest scale factor where content still fits
    lo, hi = 0.3, 1.0
    for _ in range(12):
        mid = (lo + hi) / 2
        if measure_left_panel_height(p, fmt.scaled_typo(mid)) <= available_h:
            lo = mid
        else:
            hi = mid
    fitted = fmt.scaled_typo(lo)
    print(f"    auto-scale left panel: {lo:.2f}x  (fs_body {fmt.fs_body:.2f}→{fitted.fs_body:.2f}mm)")
    return fitted

# ── Left panel ────────────────────────────────────────────────────────────────

def left_panel_svg(p, fmt, a2_solid, white_solid):
    """Generate left panel SVG text content (ingredients, storage, etc.)."""
    cx       = fmt.lp_cx
    wrap_w   = (fmt.lp_x2 - fmt.lp_x1) - 5   # 2.5mm margin each side
    out      = []
    y        = fmt.lp_x1 + 2   # top of content (canvas y)
    y        = BLEED + 3        # safe zone top + small offset

    def header(text):
        nonlocal y
        out.append(svgt(cx, y, text, fmt.fs_hdr, hexc(a2_solid),
                        bold=True, anchor="middle"))
        y += fmt.lh_hdr

    def body(text, bold_wds=None, italic_wds=None, alpha_note=False):
        nonlocal y
        fill = hexc(white_solid)
        for line in wrap_mm(text, FONT_R, fmt.fs_body, wrap_w):
            if bold_wds:
                out.append(svgt_styled(cx, y, line.split(), fmt.fs_body,
                                       fill, bold_wds=bold_wds))
            elif italic_wds:
                # Render full line; mark italic words inline
                words = line.split()
                parts = []
                for wd in words:
                    esc   = H.escape(wd)
                    clean = wd.rstrip('.,;:()')
                    if clean in italic_wds:
                        parts.append(f'<tspan font-style="italic">{esc}</tspan>')
                    else:
                        parts.append(esc)
                baseline_y = y + fmt.fs_body * 0.78
                out.append(
                    f'<text x="{cx:.3f}" y="{baseline_y:.3f}" '
                    f'font-family="Ubuntu,sans-serif" font-size="{fmt.fs_body}" '
                    f'font-weight="normal" fill="{fill}" text-anchor="middle">'
                    + ' '.join(parts) + '</text>'
                )
            else:
                out.append(svgt(cx, y, line, fmt.fs_body, fill, anchor="middle"))
            y += fmt.lh_body

    header("СКЛАД:")
    body(p["ingredients"], bold_wds=p.get("bold_wds"))

    header("УМОВИ ЗБЕРІГАННЯ:")
    body(p["storage"], italic_wds={'t', 'd(діб)'})

    header("АДРЕСА ВИРОБНИЧИХ ПОТУЖНОСТЕЙ:")
    body(p["address"])

    header("ВИРОБНИК:")
    body(p["manufacturer"])

    if p.get("commission"):
        header("ВИГОТОВЛЕНО НА ЗАМОВЛЕННЯ:")
        body(p["commission"])

    # Date note
    y += fmt.fs_note * 0.5
    note = "Дата «Краще спожити до» та номер партії (L) вказані на етикетці."
    for line in wrap_mm(note, FONT_R, fmt.fs_note, wrap_w):
        out.append(svgt(cx, y, line, fmt.fs_note, hexc(white_solid), anchor="middle"))
        y += fmt.fs_note * 1.4

    return "\n".join(out)

# ── Nutrition panel ───────────────────────────────────────────────────────────

def nutrition_panel_svg(p, fmt, a2_solid, white_solid, row_stripe_solid):
    """Generate nutrition table SVG content."""
    nx  = fmt.np_x1
    nw  = fmt.np_x2 - fmt.np_x1
    ncx = fmt.np_cx
    out = []
    y   = BLEED + 3   # canvas y start

    n = p["nutrition"]
    rows = [
        ("Енергетична цінність (калорійність)",
         f"{n['energy_kj']} kJ(кДж)/{n['energy_kcal']} kcal(ккал)", False),
        ("Жири",           f"{n['fat']} g(г)",     False),
        ("з них насичені", f"{n['sat_fat']} g(г)", True),
        ("Вуглеводи",      f"{n['carbs']} g(г)",   False),
        ("з них цукри",    f"{n['sugars']} g(г)",  True),
        ("Білки",          f"{n['protein']} g(г)", False),
        ("Сіль",           f"{n['salt']} g(г)",    False),
    ]

    # Header
    header_text = "Поживна цінність на 100 g(г) продукту"
    for hl in wrap_mm(header_text, FONT_R, fmt.fs_nutr, nw - 1):
        out.append(svgt(ncx, y, hl, fmt.fs_nutr, hexc(a2_solid), anchor="middle"))
        y += fmt.fs_nutr * 1.35
    y += 0.5

    # Divider
    out.append(f'<line x1="{nx:.3f}" y1="{y:.3f}" x2="{nx+nw:.3f}" y2="{y:.3f}" '
               f'stroke="{hexc(a2_solid)}" stroke-width="0.3" fill="none"/>')
    y += 1.2

    # Rows
    row_h = fmt.fs_nutr * 3.5
    for i, (label, value, indent) in enumerate(rows):
        ry = y + i * row_h
        if i % 2 == 0:
            out.append(f'<rect x="{nx:.3f}" y="{ry:.3f}" '
                       f'width="{nw:.3f}" height="{row_h:.3f}" '
                       f'fill="{hexc(row_stripe_solid)}"/>')
        indent_mm = 1.5 if indent else 0
        lx  = nx + 0.5 + indent_mm
        lw2 = nw - 9 - indent_mm
        for j, ll in enumerate(wrap_mm(label, FONT_R, fmt.fs_nutr, lw2)):
            out.append(svgt(lx, ry + 0.3 + j * fmt.fs_nutr * 1.3,
                           ll, fmt.fs_nutr, "#ffffff"))
        out.append(svgt(nx + nw - 0.5, ry + fmt.fs_nutr * 1.5,
                        value, fmt.fs_nutr, "#ffffff",
                        bold=True, anchor="end"))

    return "\n".join(out)

# ── Right panel ───────────────────────────────────────────────────────────────

def right_panel_svg(p, fmt, a2_solid, nc_solid, white_solid,
                    logo_size, logo_b64):
    """Generate right panel SVG content (logo, category, name, mass, icons)."""
    rx  = fmt.rp_x1
    rw  = fmt.rp_x2 - fmt.rp_x1
    rcx = fmt.rp_cx
    lw_px, lh_px = logo_size
    out = []

    # ── Logo (high-res PNG) ──
    # Scale to target height in mm, preserving aspect ratio
    target_lh_mm = fmt.logo_h
    target_lw_mm = target_lh_mm * lw_px / lh_px
    if target_lw_mm > rw - 4:
        target_lw_mm = rw - 4
        target_lh_mm = target_lw_mm * lh_px / lw_px
    lx = rcx - target_lw_mm / 2
    ly = BLEED + 3 + 2
    out.append(f'<image x="{lx:.3f}" y="{ly:.3f}" '
               f'width="{target_lw_mm:.3f}" height="{target_lh_mm:.3f}" '
               f'href="{logo_b64}"/>')

    # ── Category ──
    cat_y  = ly + target_lh_mm + 2
    cat_fs = fmt.fs_cat
    while text_width_mm(p["category"], FONT_R, cat_fs) > rw - 2 and cat_fs > 1.8:
        cat_fs -= 0.1
    out.append(svgt(rcx, cat_y, p["category"], cat_fs,
                    "#ffffff", anchor="middle"))

    # ── Accent line ──
    line_y = cat_y + cat_fs + 1.5
    line_w = min(18, rw * 0.4)
    out.append(f'<rect x="{rcx-line_w/2:.3f}" y="{line_y:.3f}" '
               f'width="{line_w:.3f}" height="0.5" '
               f'fill="{hexc(a2_solid)}"/>')

    # ── Product name (auto-size) ──
    name      = p["name"]
    name_len  = len(name)
    name_max_w = rw - 3

    # For large format, name can be large (up to ~15mm); for small, more constrained
    max_fs = fmt.rp_x2 - fmt.rp_x1  # never bigger than panel width in mm (rough ceiling)
    max_fs = min(max_fs, 15.0 if fmt.name == "large" else 9.0)
    ns = max_fs
    while text_width_mm(name, FONT_B, ns) > name_max_w and ns > 3.5:
        ns -= 0.2

    # Vertical centre of name area = between accent line and mass row
    bottom_reserve = fmt.fs_mass + 3 + BLEED   # mass netto + gap + bleed margin
    mass_y    = fmt.canvas_h - bottom_reserve
    name_area_h = mass_y - (line_y + 2)
    name_top  = line_y + 2 + (name_area_h - ns) / 2

    out.append(svgt(rcx, name_top, name, ns,
                    hexc(nc_solid), bold=True, anchor="middle"))

    extra_y = name_top + ns + 2
    if p.get("subtitle"):
        sub_fs = min(fmt.fs_cat * 0.85, ns * 0.5)
        out.append(svgt(rcx, extra_y, p["subtitle"], sub_fs,
                        hexc(a2_solid), anchor="middle"))
        extra_y += sub_fs + 1.5
    if p.get("sweetener_note"):
        sw_fs = min(fmt.fs_cat * 0.7, 3.0)
        out.append(svgt(rcx, extra_y, p["sweetener_note"], sw_fs,
                        hexc(a2_solid), anchor="middle"))

    # ── Mass netto + е ──
    mass_text = f"МАСА НЕТТО {p['weight']} g(г)"
    out.append(svgt(rcx, mass_y, mass_text, fmt.fs_mass,
                    "#ffffff", anchor="middle"))
    mw_mm = text_width_mm(mass_text, FONT_R, fmt.fs_mass)
    e_x   = rcx + mw_mm / 2 + 0.5
    e_fs  = fmt.fs_mass * 1.6
    out.append(svgt(e_x, mass_y - e_fs * 0.3, "е", e_fs,
                    "#ffffff", anchor="start"))

    # ── Icons row (placed in left panel bottom area by main assembler) ──
    # (handled separately in main SVG assembler)

    return "\n".join(out)

# ── Icons row ─────────────────────────────────────────────────────────────────

def icons_svg(p, fmt, x_start, y_start, width_mm, height_mm):
    """Generate icons row SVG, centred in given bounding box."""
    icon_files = p.get("icons", default_icons(p["weight"]))
    n          = len(icon_files)
    if not n:
        return ""
    spacing_mm = 1.5
    target_h_px = max(20, round(height_mm * 11.8))   # ~300dpi scale
    loaded     = [load_icon_b64(f, target_h_px) for f in icon_files]
    # Convert pixel widths back to mm
    total_w_mm = sum(iw / target_h_px * height_mm for iw, _, _ in loaded) + spacing_mm * (n - 1)
    if total_w_mm > width_mm:
        # Reduce height to fit
        scale = width_mm / total_w_mm
        height_mm  = height_mm  * scale
        total_w_mm = total_w_mm * scale
        target_h_px = max(10, round(height_mm * 11.8))
        loaded = [load_icon_b64(f, target_h_px) for f in icon_files]
        total_w_mm = sum(iw / target_h_px * height_mm for iw, _, _ in loaded) + spacing_mm * (n - 1)

    x = x_start + (width_mm - total_w_mm) / 2
    y = y_start + (height_mm * 0) / 2   # top-aligned
    parts = []
    for iw_px, ih_px, b64 in loaded:
        iw_mm = iw_px / ih_px * height_mm
        parts.append(f'<image x="{x:.3f}" y="{y:.3f}" '
                     f'width="{iw_mm:.3f}" height="{height_mm:.3f}" '
                     f'href="{b64}"/>')
        x += iw_mm + spacing_mm
    return "\n".join(parts)

# ── Barcode ───────────────────────────────────────────────────────────────────

def barcode_block_svg(barcode_code, x, y, w, h, bg_color_hex="#ffffff"):
    """White background rect + EAN-13 barcode, all in mm coordinates."""
    pad = 0.8
    bars = ean13_svg(
        barcode_code,
        x=x + pad, y=y + pad, w=w - 2*pad, h=h - 2*pad,
        bar_color="#000000", text_color="#000000",
    )
    return (f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" '
            f'rx="0.7" fill="{bg_color_hex}"/>\n{bars}')

# ── Crop marks ────────────────────────────────────────────────────────────────

def crop_marks_svg(canvas_w, canvas_h, bleed, gap=0.4, lw=0.15):
    """8 crop mark lines at the 4 trim corners, running through bleed zone."""
    tx1, ty1 = bleed, bleed                          # trim top-left
    tx2, ty2 = canvas_w - bleed, canvas_h - bleed   # trim bottom-right
    attr = f'stroke="#000000" stroke-width="{lw}" fill="none"'
    marks = [
        # Top-left
        f'<line x1="{0}" y1="{ty1}" x2="{tx1-gap:.3f}" y2="{ty1}" {attr}/>',
        f'<line x1="{tx1}" y1="{0}" x2="{tx1}" y2="{ty1-gap:.3f}" {attr}/>',
        # Top-right
        f'<line x1="{tx2+gap:.3f}" y1="{ty1}" x2="{canvas_w}" y2="{ty1}" {attr}/>',
        f'<line x1="{tx2}" y1="{0}" x2="{tx2}" y2="{ty1-gap:.3f}" {attr}/>',
        # Bottom-left
        f'<line x1="{0}" y1="{ty2}" x2="{tx1-gap:.3f}" y2="{ty2}" {attr}/>',
        f'<line x1="{tx1}" y1="{ty2+gap:.3f}" x2="{tx1}" y2="{canvas_h}" {attr}/>',
        # Bottom-right
        f'<line x1="{tx2+gap:.3f}" y1="{ty2}" x2="{canvas_w}" y2="{ty2}" {attr}/>',
        f'<line x1="{tx2}" y1="{ty2+gap:.3f}" x2="{tx2}" y2="{canvas_h}" {attr}/>',
    ]
    return "\n".join(marks)

# ── SVG assembler ─────────────────────────────────────────────────────────────

def generate_print_svg(p, fmt, logo_size, logo_b64, barcode_code):
    """Assemble full print-ready SVG with mm coordinates, no transparency."""
    a1  = p["accent"]
    a2  = p["accent2"]
    bg  = bg_color(p)
    nc  = p.get("name_color", (255, 255, 255))
    bar = p.get("border", a1)
    cw  = fmt.canvas_w
    ch  = fmt.canvas_h

    # ── Pre-composite all colors (no transparency in output) ──
    # Background gradient: semi-transparent accent over dark bg → solid colors
    if p.get("bg_dark"):
        grad_start = composite(a1, 0.78, bg)
        grad_end   = bg
    else:
        grad_start = composite(a1, 0.59, bg)
        grad_end   = composite(a1, 0.08, bg)

    divider_col = composite(a2, 0.40, bg)
    stripe_col  = composite((255, 255, 255), 0.10, bg)    # nutrition row stripe
    white_solid = (255, 255, 255)                          # text color
    a2_solid    = a2
    nc_solid    = nc

    # ── Layout: barcode + icons at bottom of left panel area ──
    # (computed first so we know available text height for auto-fitting)
    if fmt.name == "large":
        bc_x, bc_y, bc_w, bc_h = 5.0, ch - BLEED - 17.0, 28.0, 15.0
        ic_x = bc_x + bc_w + 2
        ic_w = fmt.lp_x2 - ic_x - 2
        ic_y = bc_y
        ic_h = bc_h
    else:
        # Small: icons row above barcode, both spanning left panel width
        lp_w = fmt.lp_x2 - fmt.lp_x1 - 2
        bc_h = 12.0
        ic_h = 9.0
        bc_y = ch - BLEED - bc_h - 0.5
        ic_y = bc_y - ic_h - 0.5
        bc_x = fmt.lp_x1 + 1
        bc_w = lp_w
        ic_x = bc_x
        ic_w = lp_w

    barcode_svg = barcode_block_svg(barcode_code, bc_x, bc_y, bc_w, bc_h) if barcode_code else ""
    ic_svg      = icons_svg(p, fmt, ic_x, ic_y, ic_w, ic_h)

    # ── Auto-fit left panel typography ──
    lc_clip_bottom = ic_y if fmt.name == "small" else bc_y
    lp_available_h = (lc_clip_bottom - 0.5) - (BLEED + 3)   # clip end y minus content start y
    fmt_lp = fit_left_panel_typo(p, fmt, lp_available_h)

    # ── Panel SVG content ──
    lp  = left_panel_svg(p, fmt_lp, a2_solid, white_solid)
    np_ = nutrition_panel_svg(p, fmt, a2_solid, white_solid, stripe_col)
    rp  = right_panel_svg(p, fmt, a2_solid, nc_solid, white_solid,
                          logo_size, logo_b64)

    # ── Date strip ──
    ds_cx = fmt.ds_cx
    ds_cy = ch / 2
    ds_text_col = composite((0, 0, 0), 1.0, (255, 255, 255))   # pure black

    # ── Clip paths (using canvas-relative coords) ──
    # Keep clip-paths for panel containment — they become PDF clipping paths (OK for print)
    pl_clip  = (f'<clipPath id="pl-clip"><rect x="{fmt.lp_x1}" y="{BLEED}" '
                f'width="{fmt.lp_x2-fmt.lp_x1}" height="{fmt.trim_h}"/></clipPath>')
    pn_clip  = (f'<clipPath id="pn-clip"><rect x="{fmt.np_x1}" y="{BLEED}" '
                f'width="{fmt.np_x2-fmt.np_x1}" height="{fmt.trim_h}"/></clipPath>')
    rp_clip  = (f'<clipPath id="rp-clip"><rect x="{fmt.rp_x1}" y="{BLEED}" '
                f'width="{fmt.rp_x2-fmt.rp_x1}" height="{fmt.trim_h}"/></clipPath>')
    lc_clip  = (f'<clipPath id="lc-clip"><rect x="{fmt.lp_x1}" y="{BLEED}" '
                f'width="{fmt.lp_x2-fmt.lp_x1}" '
                f'height="{lc_clip_bottom - BLEED - 0.5}"/></clipPath>')

    product_key = p["output"].replace(".jpg", "")
    em_layer = emoji_layer_svg(product_key, fmt)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{cw}mm" height="{ch}mm" viewBox="0 0 {cw} {ch}">
<defs>
  <style>
    @font-face {{ font-family: 'Ubuntu'; font-weight: 400;
                  src: url('fonts/Ubuntu-R.ttf') format('truetype'); }}
    @font-face {{ font-family: 'Ubuntu'; font-weight: 700;
                  src: url('fonts/Ubuntu-B.ttf') format('truetype'); }}
  </style>
  {SVG_ICON_DEFS}
  <linearGradient id="bg_grad" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%"   stop-color="{css(grad_start)}"/>
    <stop offset="100%" stop-color="{css(grad_end)}"/>
  </linearGradient>
  <clipPath id="label-clip"><rect width="{cw}" height="{ch}"/></clipPath>
  {pl_clip}
  {pn_clip}
  {rp_clip}
  {lc_clip}
</defs>

<!-- ── Background (full canvas including bleeds) ── -->
<rect width="{cw}" height="{ch}" fill="{css(bg)}"/>
<rect width="{cw}" height="{ch}" fill="url(#bg_grad)"/>

<!-- ── Emoji background texture ── -->
{em_layer}

<!-- ── Decorative chrome ── -->
<rect x="{BLEED}" y="{BLEED}" width="1" height="{fmt.trim_h}" fill="{css(bar)}"/>
<rect x="{BLEED}" y="{BLEED}" width="{fmt.trim_w}" height="1.2" fill="{css(bar)}"/>
<rect x="{BLEED}" y="{BLEED+fmt.trim_h-1.2:.3f}" width="{fmt.trim_w}" height="1.2" fill="{css(bar)}"/>
<line x1="{fmt.np_x1}" y1="{BLEED+2}" x2="{fmt.np_x1}" y2="{BLEED+fmt.trim_h-2}"
      stroke="{css(divider_col)}" stroke-width="0.25" fill="none"/>

<!-- ── Left panel (ingredients, storage, address…) ── -->
<g clip-path="url(#lc-clip)">
{lp}
</g>

<!-- ── Nutrition panel ── -->
<g clip-path="url(#pn-clip)">
{np_}
</g>

<!-- ── Right panel (logo, name, mass) ── -->
<g clip-path="url(#rp-clip)">
{rp}
</g>

<!-- ── Icons row ── -->
{ic_svg}

<!-- ── Barcode ── -->
{barcode_svg}

<!-- ── Date strip (right edge) ── -->
<rect x="{fmt.ds_x1:.3f}" y="{BLEED:.3f}" width="{fmt.ds_x2-fmt.ds_x1:.3f}" height="{fmt.trim_h:.3f}"
      fill="#ffffff"/>
<text x="{ds_cx:.3f}" y="{ds_cy:.3f}"
      font-family="Ubuntu,sans-serif" font-size="1.8"
      fill="#000000" text-anchor="middle" dominant-baseline="middle"
      transform="rotate(-90 {ds_cx:.3f} {ds_cy:.3f})">Дата «Краще спожити до» та номер партії (L)</text>

<!-- ── Crop marks ── -->
{crop_marks_svg(cw, ch, BLEED)}

</svg>"""

# ── Export pipeline ───────────────────────────────────────────────────────────

def run_gs(src_pdf, dst, outlines=False):
    """Ghostscript: RGB PDF → CMYK PDF (with or without text-to-outlines)."""
    cmd = [
        "gs", "-sDEVICE=pdfwrite",
        "-sColorConversionStrategy=CMYK",
        "-dProcessColorModel=/DeviceCMYK",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/prepress",
        "-dNOPAUSE", "-dBATCH", "-q",
        f"-sOutputFile={dst}",
    ]
    if outlines:
        cmd.append("-dNoOutputFonts")
    cmd.append(src_pdf)
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        print(f"  GS ERROR: {result.stderr.decode()[:200]}")

def export_product(p, fmt, logo_size, logo_b64, svg_dir, ai_dir, pdf_dir):
    name         = p["output"].replace(".jpg", "")
    barcode_code = BARCODES.get(name, "")
    svg_content  = generate_print_svg(p, fmt, logo_size, logo_b64, barcode_code)

    # Save SVG source
    svg_path = os.path.join(svg_dir, f"{name}.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    with tempfile.TemporaryDirectory() as tmp:
        fonts_tmp = os.path.join(tmp, "fonts")
        os.makedirs(fonts_tmp)
        shutil.copy2(FONT_R, os.path.join(fonts_tmp, "Ubuntu-R.ttf"))
        shutil.copy2(FONT_B, os.path.join(fonts_tmp, "Ubuntu-B.ttf"))

        svg_tmp = os.path.join(tmp, "label.svg")
        with open(svg_tmp, "w", encoding="utf-8") as f:
            f.write(svg_content)

        rgb_pdf = os.path.join(tmp, "label_rgb.pdf")

        # SVG → RGB PDF at 300dpi
        r = subprocess.run(
            ["rsvg-convert", "--format=pdf", "--dpi-x=300", "--dpi-y=300",
             "-o", rgb_pdf, svg_tmp],
            capture_output=True
        )
        if r.returncode != 0:
            print(f"  rsvg ERROR: {r.stderr.decode()[:200]}")
            return

        ai_out  = os.path.join(ai_dir,  f"{name}.ai")
        pdf_out = os.path.join(pdf_dir, f"{name}.pdf")

        # RGB PDF → CMYK, fonts embedded (.ai)
        run_gs(rgb_pdf, ai_out, outlines=False)

        # RGB PDF → CMYK, text as outlines (.pdf)
        run_gs(rgb_pdf, pdf_out, outlines=True)

    print(f"  ✓  {name}  ({fmt.trim_w}×{fmt.trim_h}mm)")

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Food Festival — Print-Ready Labels")
    print("=" * 50)

    # Assign format to each product
    product_formats = []
    for p in PRODUCTS:
        fmt = SMALL if int(p["weight"]) <= 1000 else LARGE
        product_formats.append((p, fmt))

    # Create output directories
    for fmt in (LARGE, SMALL):
        for subdir in ("ai", "pdf"):
            os.makedirs(os.path.join(OUT_DIR, fmt.name, subdir), exist_ok=True)
        os.makedirs(os.path.join(OUT_DIR, fmt.name, "svg_source"), exist_ok=True)

    # Load logo once per format (different resolutions for different print sizes)
    print("\nLoading assets…")
    logo_large = load_logo_b64(max_h_px=600)
    logo_small = load_logo_b64(max_h_px=400)
    print(f"  logo LARGE: {logo_large[0][0]}×{logo_large[0][1]}px")
    print(f"  logo SMALL: {logo_small[0][0]}×{logo_small[0][1]}px")

    print(f"\nGenerating {len(PRODUCTS)} labels…")
    for p, fmt in product_formats:
        logo_data = logo_large if fmt is LARGE else logo_small
        logo_size, logo_b64 = logo_data
        svg_dir  = os.path.join(OUT_DIR, fmt.name, "svg_source")
        ai_dir   = os.path.join(OUT_DIR, fmt.name, "ai")
        pdf_dir  = os.path.join(OUT_DIR, fmt.name, "pdf")
        export_product(p, fmt, logo_size, logo_b64, svg_dir, ai_dir, pdf_dir)

    print(f"\nDone → {OUT_DIR}/")
    print("  Output structure:")
    print("    large/ai/   — 200×100mm + bleeds, CMYK, fonts embedded")
    print("    large/pdf/  — 200×100mm + bleeds, CMYK, text as outlines")
    print("    small/ai/   — 120×70mm  + bleeds, CMYK, fonts embedded")
    print("    small/pdf/  — 120×70mm  + bleeds, CMYK, text as outlines")

if __name__ == "__main__":
    main()
