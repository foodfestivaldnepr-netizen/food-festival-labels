#!/usr/bin/env python3
"""
Generate print-ready SVG label files for all 11 Food Festival products.

Output folder: output_svg/
  - fonts/Ubuntu-B.ttf, Ubuntu-R.ttf  (referenced by all SVGs)
  - 01_sauce_bbq.svg … 11_ketchup_classic_830.svg

Open any SVG in a browser → File → Print for a clean vector print.
"""
import os, sys, base64, html as H, random, io, shutil
from PIL import Image, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_labels import PRODUCTS, LOGO_PATH, load_logo_white
from build_html_labels import BG_EMOJI

BASE      = os.path.dirname(os.path.abspath(__file__))
SVG_DIR   = os.path.join(BASE, "output_svg")
ICONS_DIR = os.path.join(BASE, "icons")

FONT_B = "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"
FONT_R = "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf"

LW, LH = 1178, 594  # label pixel dimensions

# ── colour helpers ────────────────────────────────────────────────────────────

def rgb(c):            return f"rgb({c[0]},{c[1]},{c[2]})"
def rgba(c, a):        return f"rgba({c[0]},{c[1]},{c[2]},{a})"

# For fill/stroke attributes, use fill + fill-opacity for max SVG compatibility
def fill_attr(c, a=1): return f'fill="{rgb(c)}" fill-opacity="{a}"'
def stroke_attr(c, a, w=1): return f'stroke="{rgb(c)}" stroke-opacity="{a}" stroke-width="{w}"'

# ── font / text helpers ───────────────────────────────────────────────────────

_font_cache: dict = {}
def _pf(path, size):
    k = (path, size)
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(path, size)
    return _font_cache[k]

def text_width(text, path, size):
    return _pf(path, size).getlength(text)

def wrap(text, path, size, max_w):
    font  = _pf(path, size)
    words = text.split()
    lines, line = [], ""
    for word in words:
        candidate = f"{line} {word}".strip() if line else word
        if font.getlength(candidate) <= max_w:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def svgt(x, y, text, fs, fill_color, fill_a=1.0,
         bold=False, anchor="start", letter_spacing=None,
         transform=None):
    """Single SVG <text> element. y is the visual top of the text."""
    baseline_y = y + fs * 0.78      # convert top → SVG baseline
    fw   = "bold" if bold else "normal"
    fop  = f' fill-opacity="{fill_a}"' if fill_a != 1.0 else ""
    ls   = f' letter-spacing="{letter_spacing}"' if letter_spacing else ""
    tr   = f' transform="{transform}"'            if transform      else ""
    return (f'<text x="{x:.1f}" y="{baseline_y:.1f}" '
            f'font-family="Ubuntu,sans-serif" font-size="{fs}" font-weight="{fw}" '
            f'fill="{fill_color}" text-anchor="{anchor}"{fop}{ls}{tr}>'
            f'{H.escape(text)}</text>')

# ── logo ──────────────────────────────────────────────────────────────────────

def load_logo_b64(max_w=290, max_h=200):
    img = load_logo_white(LOGO_PATH)
    img.thumbnail((max_w, max_h), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return img.size, f"data:image/png;base64,{b64}"

# ── icon helpers ─────────────────────────────────────────────────────────────

_icon_cache_svg: dict = {}

def _load_icon_b64(filename, target_h=62):
    if filename in _icon_cache_svg:
        return _icon_cache_svg[filename]
    from PIL import Image
    import numpy as np
    path = os.path.join(ICONS_DIR, filename)
    img  = Image.open(path).convert("RGBA")
    arr  = np.array(img)
    white = (arr[:,:,0] > 215) & (arr[:,:,1] > 215) & (arr[:,:,2] > 215)
    arr[white,   3]  = 0
    arr[~white, :3]  = 255
    img  = Image.fromarray(arr, "RGBA")
    ow, oh = img.size
    nw  = round(ow / oh * target_h)
    img = img.resize((nw, target_h), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    result = (nw, target_h, f"data:image/png;base64,{b64}")
    _icon_cache_svg[filename] = result
    return result

def _default_icons_svg(weight_str):
    plastic = "icon_hdpe02.png" if int(weight_str) >= 4000 else "icon_pp05.png"
    return ["icon_bez_gmo.png", plastic, "icon_foodsafe.png", "icon_trash.jpeg"]

def icons_layer(p):
    icon_files = p.get("icons", _default_icons_svg(p["weight"]))
    if not icon_files:
        return ""
    target_h = 62
    loaded   = [_load_icon_b64(f, target_h) for f in icon_files]
    ax1, ax2 = 185, 510
    ay1, ay2 = 492, 582
    spacing  = 10
    total_w  = sum(iw for iw, _, _ in loaded) + spacing * (len(loaded) - 1)
    x = ax1 + (ax2 - ax1 - total_w) // 2
    y = ay1 + (ay2 - ay1 - target_h) // 2
    parts = []
    for iw, ih, b64 in loaded:
        parts.append(f'<image x="{x}" y="{y}" width="{iw}" height="{ih}" href="{b64}"/>')
        x += iw + spacing
    return "\n".join(parts)

# ── emoji background ──────────────────────────────────────────────────────────

def emoji_layer(key):
    emoji = BG_EMOJI.get(key, "")
    if not emoji:
        return ""
    rng    = random.Random(hash(key) & 0xFFFFFFFF)
    min_d2 = 310 ** 2
    placed, spans = [], []
    for _ in range(5):
        candidate  = (rng.uniform(0, LW), rng.uniform(0, LH))
        best_score = 0
        for _ in range(400):
            cx, cy = rng.uniform(0, LW), rng.uniform(0, LH)
            score  = min((cx-px)**2+(cy-py)**2 for px,py in placed) if placed else min_d2
            if score >= min_d2:
                candidate = (cx, cy)
                break
            if score > best_score:
                best_score, candidate = score, (cx, cy)
        placed.append(candidate)
        rot = rng.uniform(-35, 35)
        sz  = rng.randint(250, 310)
        cx, cy = candidate
        spans.append(
            f'  <text x="{cx:.0f}" y="{cy:.0f}" font-size="{sz}" dominant-baseline="middle"'
            f' transform="rotate({rot:.1f} {cx:.0f} {cy:.0f})">{emoji}</text>'
        )
    inner = "\n".join(spans)
    return (f'<g opacity="0.12" clip-path="url(#label-clip)"\n'
            f'   style="filter:brightness(0) invert(1)">\n{inner}\n</g>')

# ── panel builders ────────────────────────────────────────────────────────────

def left_panel(p, a2):
    cx  = 14 + 244      # centre of left panel
    pw  = 476           # usable wrap width
    out = []
    y   = 18            # visual top y (below top bar)

    def header(text, fs=13.5, gap_before=7):
        nonlocal y
        y += gap_before
        out.append(svgt(cx, y, text, fs, rgb(a2), bold=True, anchor="middle"))
        y += fs + 3

    def body(text, fs=11, lh=None, font=FONT_R, alpha=1.0):
        nonlocal y
        if lh is None:
            lh = round(fs * 1.35)
        for line in wrap(text, font, int(fs), pw):
            out.append(svgt(cx, y, line, fs, "#ffffff", fill_a=alpha, anchor="middle"))
            y += lh

    def gap(n=5):
        nonlocal y; y += n

    header("СКЛАД:", 13.5, gap_before=4)
    body(p["ingredients"], 13, lh=18)

    header("УМОВИ ЗБЕРІГАННЯ:", 13.5)
    body(p["storage"], 11, lh=14)

    header("АДРЕСА ВИРОБНИЧИХ ПОТУЖНОСТЕЙ:", 11.5, gap_before=5)
    body(p["address"], 11, lh=14)

    header("ВИРОБНИК:", 11.5, gap_before=4)
    body(p["manufacturer"], 11, lh=14)

    if p.get("commission"):
        header("ВИГОТОВЛЕНО НА ЗАМОВЛЕННЯ:", 11.5, gap_before=4)
        body(p["commission"], 11, lh=14)

    if p.get("phone"):
        gap(3)
        body(p["phone"], 11, lh=14, alpha=0.82)

    body("Дата «Краще спожити до» та номер партії (L) вказані на етикетці.",
         11, lh=14, alpha=0.82)

    return "\n".join(out)


def nutrition_panel(p, a2):
    nx  = 514
    nw  = 198
    ncx = nx + nw // 2
    out = []
    y   = 14

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
    out.append(svgt(ncx, y, "Поживна цінність на 100 g(г) продукту",
                    9.5, rgb(a2), anchor="middle"))
    y += 13

    # Divider
    out.append(f'<line x1="{nx}" y1="{y+6}" x2="{nx+nw}" y2="{y+6}" '
               f'{stroke_attr(a2, 0.8)} fill="none"/>')
    y += 10

    # Nutrition rows
    row_h = 28
    for i, (label, value, indent) in enumerate(rows):
        ry = y + i * row_h
        if i % 2 == 0:
            out.append(f'<rect x="{nx}" y="{ry}" width="{nw}" height="{row_h}" '
                       f'fill="white" fill-opacity="0.1"/>')
        indent_px = 10 if indent else 0
        lx  = nx + 3 + indent_px
        lw2 = nw - 36 - indent_px
        label_lines = wrap(label, FONT_R, 9, lw2)
        for j, ll in enumerate(label_lines):
            out.append(svgt(lx, ry + 2 + j * 11, ll, 9, "#ffffff"))
        # Value right-aligned
        out.append(svgt(nx + nw - 3, ry + 14, value,
                        9.5, "#ffffff", bold=True, anchor="end"))

    return "\n".join(out)


def right_panel(p, a2, nc, logo_size, logo_b64):
    rx  = 730
    rw  = 410
    rcx = rx + rw // 2
    lw_img, lh_img = logo_size
    out = []

    # Logo centred
    lx = rcx - lw_img // 2
    out.append(f'<image x="{lx}" y="22" width="{lw_img}" height="{lh_img}" '
               f'href="{logo_b64}"/>')

    # Category
    cat_y = 22 + lh_img + 16
    out.append(svgt(rcx, cat_y, p["category"], 20, "#ffffff", anchor="middle"))

    # Accent line
    line_y = cat_y + 22
    out.append(f'<rect x="{rcx-55}" y="{line_y}" width="110" height="2" '
               f'{fill_attr(a2)}/>')

    # Product name — vertically centred between accent line and mass row
    name_len = len(p["name"])
    ns = next((s for thr, s in [(4,90),(6,78),(8,66),(10,54),(12,48),(14,42)]
               if name_len <= thr), 36)
    name_area_mid = (line_y + LH - 52) // 2
    name_top_y    = name_area_mid - ns // 2
    out.append(svgt(rcx, name_top_y, p["name"], ns, rgb(nc),
                    bold=True, anchor="middle"))

    # МАСА НЕТТО + е
    mass_y = LH - 50
    out.append(svgt(rcx, mass_y, f"МАСА НЕТТО {p['weight']} г", 13,
                    "#ffffff", anchor="middle"))
    # "е" (estimate symbol) slightly larger, appended to the right
    mw = text_width(f"МАСА НЕТТО {p['weight']} г", FONT_R, 13)
    out.append(svgt(rcx + mw // 2 + 4, mass_y - 6, "е", 22, "#ffffff"))

    return "\n".join(out)

# ── SVG assembler ─────────────────────────────────────────────────────────────

def generate_svg(p: dict, logo_size, logo_b64) -> str:
    a   = p["accent"]
    a2  = p["accent2"]
    bd  = p.get("bg_dark")
    br  = p.get("border")
    nc  = p.get("name_color", (255, 255, 255))
    bar = br if br else a

    if bd:
        g_s, g_e = rgba(a, 0.78), rgba(a, 0)
        bg_base  = rgb(bd)
    else:
        dark    = tuple(int(c * 0.25) for c in a)
        g_s, g_e = rgba(a, 0.59), rgba(a, 0.08)
        bg_base  = rgb(dark)

    lp  = left_panel(p, a2)
    np_ = nutrition_panel(p, a2)
    rp  = right_panel(p, a2, nc, logo_size, logo_b64)
    em  = emoji_layer(p["key"])
    ic  = icons_layer(p)

    # Wrap each panel's elements in a clip group
    def clip(inner, clip_id):
        return f'<g clip-path="url(#{clip_id})">\n{inner}\n</g>'

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{LW}" height="{LH}" viewBox="0 0 {LW} {LH}">
<defs>
  <style>
    @font-face {{
      font-family: 'Ubuntu'; font-weight: 400;
      src: url('fonts/Ubuntu-R.ttf') format('truetype');
    }}
    @font-face {{
      font-family: 'Ubuntu'; font-weight: 700;
      src: url('fonts/Ubuntu-B.ttf') format('truetype');
    }}
  </style>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%"   stop-color="{g_s}"/>
    <stop offset="100%" stop-color="{g_e}"/>
  </linearGradient>
  <clipPath id="label-clip"><rect width="{LW}" height="{LH}"/></clipPath>
  <clipPath id="pl-clip"><rect x="14"  y="8" width="488" height="{LH-16}"/></clipPath>
  <clipPath id="pn-clip"><rect x="514" y="8" width="198" height="{LH-16}"/></clipPath>
  <clipPath id="rp-clip"><rect x="730" y="0" width="448" height="{LH}"/></clipPath>
</defs>

<!-- Background -->
<rect width="{LW}" height="{LH}" fill="{bg_base}"/>
<rect width="{LW}" height="{LH}" fill="url(#bg)"/>

<!-- Emoji texture -->
{em}

<!-- Decorative chrome -->
<rect x="0" y="0" width="6" height="{LH}" {fill_attr(bar)}/>
<rect x="0" y="0" width="{LW}" height="8" {fill_attr(bar)}/>
<rect x="0" y="{LH-8}" width="{LW}" height="8" {fill_attr(bar)}/>
<rect x="5" y="15" width="{LW-5}" height="2" {fill_attr(a2, 0.59)}/>
<polygon points="549,0 629,0 579,{LH} 499,{LH}" {fill_attr(a2, 0.05)}/>
<line x1="722" y1="12" x2="722" y2="{LH-12}"
      stroke="{rgb(a2)}" stroke-opacity="0.4" stroke-width="1" fill="none"/>

<!-- Left panel -->
{clip(lp, "pl-clip")}

<!-- Nutrition panel -->
{clip(np_, "pn-clip")}

<!-- Right panel -->
{clip(rp, "rp-clip")}

<!-- Barcode box -->
<rect x="14" y="494" width="161" height="86" rx="4"
      fill="white" fill-opacity="0.92"/>
<text x="94" y="542" font-family="Ubuntu,sans-serif" font-size="10"
      fill="black" fill-opacity="0.35" text-anchor="middle"
      letter-spacing="1.5">ШТРИХКОД</text>

<!-- Icons -->
{ic}

<!-- Date strip (right edge) -->
<rect x="{LW-48}" y="9" width="48" height="{LH-18}"
      fill="white" fill-opacity="0.9"/>
<text x="{LW-24}" y="{LH//2}" font-family="Ubuntu,sans-serif" font-size="9"
      fill="#1a1a1a" text-anchor="middle" dominant-baseline="middle"
      transform="rotate(-90 {LW-24} {LH//2})">Дата «Краще спожити до» та номер партії (L)</text>

</svg>"""


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(SVG_DIR, exist_ok=True)

    # Copy font files so SVGs are self-contained as a folder
    fonts_dir = os.path.join(SVG_DIR, "fonts")
    os.makedirs(fonts_dir, exist_ok=True)
    for fname, src in [("Ubuntu-R.ttf", FONT_R), ("Ubuntu-B.ttf", FONT_B)]:
        dst = os.path.join(fonts_dir, fname)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
    print("── Fonts ──────────────────────────────────")
    print("  ✓  fonts/Ubuntu-R.ttf")
    print("  ✓  fonts/Ubuntu-B.ttf")

    # Load logo once
    logo_size, logo_b64 = load_logo_b64()
    print(f"  ✓  logo embedded ({logo_size[0]}×{logo_size[1]}px)")

    print(f"\n── SVG labels ({len(PRODUCTS)}) ──────────────────")
    for p in PRODUCTS:
        svg   = generate_svg(p, logo_size, logo_b64)
        fname = p["output"].replace(".jpg", ".svg")
        fpath = os.path.join(SVG_DIR, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(svg)
        size_kb = os.path.getsize(fpath) // 1024
        print(f"  ✓  {fname}  ({size_kb} KB)")

    print(f"\nDone → {SVG_DIR}/")
    print("  (zip output_svg/ folder to share — fonts/ subfolder required)")


if __name__ == "__main__":
    main()
