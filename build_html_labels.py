#!/usr/bin/env python3
"""
Generate HTML label files for all 11 Food Festival products.

Steps:
  1. Deduplicate extracted xlsx images → icons/ (one canonical file per icon)
  2. Generate icons/logo_white.png from the original logo
  3. Clean up all img_* / extracted_img_* temp files from the project root
  4. Generate output_html/*.html — one label per product
  5. Generate output_html/index.html — navigation page
"""
import os, sys, shutil, hashlib, html as H

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_labels import PRODUCTS, LOGO_PATH, load_logo_white

BASE      = os.path.dirname(os.path.abspath(__file__))
ICONS_DIR = os.path.join(BASE, "icons")
HTML_DIR  = os.path.join(BASE, "output_html")

# ─────────────────────────────────────────────
# 1.  Icon deduplication
# ─────────────────────────────────────────────
# From the xlsx extraction (previous session), each product sheet contained
# the same 4-5 icon images.  We identify the canonical source by file size
# (each unique image has a unique byte-length) and copy it once.
#
# Mapping: dest icon name → one valid source file
ICON_SOURCES = {
    # jpeg 5921 bytes  — "Don't litter" / Тидбайте сміття
    "icon_trash.jpeg":   "img_Кетчуп_Преміум_5000__0.jpeg",
    # png  3921 bytes  — Food safe (glass + fork)
    "icon_foodsafe.png": "img_Кетчуп_Преміум_5000__1.png",
    # png  4627 bytes  — PP 05 recycling (5 kg bucket products)
    "icon_pp05.png":     "img_Кетчуп_Преміум_5000__2.png",
    # png  3412 bytes  — БЕЗ ГМО
    "icon_bez_gmo.png":  "img_Кетчуп_Преміум_5000__3.png",
    # png  2685 bytes  — PET 01 recycling (830 g bottle products)
    "icon_pet01.png":    "img_Кетчуп_Класичний_830_2.png",
    # png 12410 bytes  — HDPE 02 recycling (830 g bottle products)
    "icon_hdpe02.png":   "img_Кетчуп_Класичний_830_3.png",
    # Example label images from the ПРИКЛАД sheet
    "priklad_1.png":     "img_ПРИКЛАД_РОЗМІЩЕННЯ_Д_0.png",
    "priklad_2.png":     "img_ПРИКЛАД_РОЗМІЩЕННЯ_Д_1.png",
}


def setup_icons():
    os.makedirs(ICONS_DIR, exist_ok=True)

    for dest_name, src_name in ICON_SOURCES.items():
        src  = os.path.join(BASE, src_name)
        dest = os.path.join(ICONS_DIR, dest_name)
        if os.path.exists(src):
            shutil.copy2(src, dest)
            print(f"  ✓  icons/{dest_name}")
        else:
            print(f"  ✗  missing source: {src_name}")

    # White logo for dark label backgrounds
    logo_dest = os.path.join(ICONS_DIR, "logo_white.png")
    logo_white = load_logo_white(LOGO_PATH)
    logo_white.save(logo_dest)
    print(f"  ✓  icons/logo_white.png")


def cleanup_temp_files():
    """Remove all img_* and extracted_img_* temp files from project root."""
    removed = 0
    for fname in os.listdir(BASE):
        if fname.startswith("img_") or fname.startswith("extracted_img"):
            os.remove(os.path.join(BASE, fname))
            removed += 1
    if removed:
        print(f"  ✓  removed {removed} temp image files from project root")


# ─────────────────────────────────────────────
# 2.  Per-product icon sets
# ─────────────────────────────────────────────
def get_icons(p):
    """Return [(src_path, alt_text), ...] for the product."""
    if int(p["weight"]) >= 4000:
        # 5 kg bucket — polypropylene (PP 05)
        return [
            ("../icons/icon_trash.jpeg",   "Тидбайте сміття"),
            ("../icons/icon_foodsafe.png", "Придатний для контакту з їжею"),
            ("../icons/icon_pp05.png",     "PP 05 — полі­пропілен"),
            ("../icons/icon_bez_gmo.png",  "БЕЗ ГМО"),
        ]
    else:
        # 830 g bottle — PET + HDPE lid
        return [
            ("../icons/icon_foodsafe.png", "Придатний для контакту з їжею"),
            ("../icons/icon_trash.jpeg",   "Тидбайте сміття"),
            ("../icons/icon_pet01.png",    "PET 01"),
            ("../icons/icon_hdpe02.png",   "HDPE 02"),
            ("../icons/icon_bez_gmo.png",  "БЕЗ ГМО"),
        ]


# ─────────────────────────────────────────────
# 3.  CSS helpers
# ─────────────────────────────────────────────
def rgb(c):      return f"rgb({c[0]},{c[1]},{c[2]})"
def rgba(c, a):  return f"rgba({c[0]},{c[1]},{c[2]},{a})"


def name_font_size(name: str) -> int:
    lens = [(4, 90), (6, 78), (8, 66), (10, 54), (12, 48), (14, 42)]
    n = len(name)
    for threshold, size in lens:
        if n <= threshold:
            return size
    return 36


def mark_italic(storage: str) -> str:
    """Wrap temperature t and d(діб) in <em> tags."""
    t = H.escape(storage)
    t = t.replace(" t ВІД",  " <em>t</em> ВІД")
    t = t.replace(" 14 d(",  " 14 <em>d</em>(")
    return t


# ─────────────────────────────────────────────
# 4.  HTML generator
# ─────────────────────────────────────────────
def generate_html(p: dict) -> str:
    a   = p["accent"]
    a2  = p["accent2"]
    bd  = p.get("bg_dark")
    br  = p.get("border")
    nc  = p.get("name_color", (255, 255, 255))
    bar = br if br else a

    if bd:
        bg_css = (f"background:"
                  f"linear-gradient(90deg,{rgba(a,0.78)} 0%,{rgba(a,0)} 100%),"
                  f"{rgb(bd)};")
    else:
        dark = tuple(int(c * 0.25) for c in a)
        bg_css = (f"background:"
                  f"linear-gradient(90deg,{rgba(a,0.59)} 0%,{rgba(a,0.08)} 100%),"
                  f"{rgb(dark)};")

    # Nutrition rows
    n = p["nutrition"]
    nutri_data = [
        ("Енергетична цінність (калорійність)",
         f"{n['energy_kj']} kJ(кДж)/{n['energy_kcal']} kcal(ккал)", False),
        ("Жири",           f"{n['fat']} g(г)",      False),
        ("з них насичені", f"{n['sat_fat']} g(г)",  True),
        ("Вуглеводи",      f"{n['carbs']} g(г)",    False),
        ("з них цукри",    f"{n['sugars']} g(г)",   True),
        ("Білки",          f"{n['protein']} g(г)",  False),
        ("Сіль",           f"{n['salt']} g(г)",     False),
    ]

    rows_html = ""
    for i, (label, value, indent) in enumerate(nutri_data):
        shade = "background:rgba(255,255,255,.1);" if i % 2 == 0 else ""
        ind   = "padding-left:10px;"              if indent         else ""
        rows_html += (
            f'<div style="padding:2px 3px 3px;{shade}{ind}">'
            f'<div style="font-size:9.5px;color:#fff;line-height:1.25;">{H.escape(label)}</div>'
            f'<div style="font-size:9.5px;font-weight:700;color:#fff;text-align:right;">{H.escape(value)}</div>'
            f'</div>\n'
        )

    # Icon boxes — black icons on small white rounded containers
    icons_html = ""
    for src, alt in get_icons(p):
        icons_html += (
            f'<div title="{H.escape(alt)}" style="background:#fff;border-radius:4px;'
            f'padding:2px 3px;display:inline-flex;align-items:center;justify-content:center;">'
            f'<img src="{src}" alt="{H.escape(alt)}" style="height:28px;width:auto;display:block;">'
            f'</div>\n'
        )

    ns = name_font_size(p["name"])

    return f"""<!DOCTYPE html>
<html lang="uk">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=1220">
  <title>{H.escape(p['name'])} — Food Festival</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,400;0,500;0,700;1,400&display=swap" rel="stylesheet">
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:#111;display:flex;flex-direction:column;align-items:center;min-height:100vh;
          padding:20px 10px;font-family:'Ubuntu',Arial,sans-serif}}
    p.meta{{color:#777;font-size:12px;margin-bottom:12px;letter-spacing:.4px}}
    a.back{{color:#888;font-size:12px;text-decoration:none;margin-bottom:14px;display:block}}
    a.back:hover{{color:#bbb}}

    /* ── Label canvas ── */
    .label{{
      position:relative;width:1178px;height:594px;overflow:hidden;
      {bg_css}
    }}

    /* decorative chrome */
    .bar-l{{position:absolute;left:0;top:0;width:6px;height:100%;background:{rgb(bar)}}}
    .bar-t{{position:absolute;left:0;top:0;width:100%;height:8px;background:{rgb(bar)}}}
    .bar-b{{position:absolute;left:0;bottom:0;width:100%;height:8px;background:{rgb(bar)}}}
    .bar-i{{position:absolute;left:5px;top:15px;right:0;height:2px;background:{rgba(a2,.59)}}}
    .sep  {{position:absolute;left:722px;top:12px;bottom:12px;width:1px;background:{rgba(a2,.4)}}}

    /* Left panel — centred text, x:14–502 */
    .pl{{position:absolute;left:14px;top:18px;width:488px;bottom:14px;
         text-align:center;color:#fff;overflow:hidden}}
    .hdr {{font-size:13.5px;font-weight:700;color:{rgb(a2)};margin-top:7px;line-height:1.2}}
    .hdr2{{font-size:11.5px;font-weight:700;color:{rgb(a2)};margin-top:5px;line-height:1.2}}
    .btxt{{font-size:13px;line-height:1.35}}
    .stxt{{font-size:11px;line-height:1.28}}
    .dtxt{{font-size:11px;line-height:1.28;color:rgba(255,255,255,.82)}}

    /* Nutrition panel — x:514–712 */
    .pn{{position:absolute;left:514px;top:16px;width:198px;bottom:10px}}
    .nhdr{{font-size:9.5px;color:{rgb(a2)};text-align:center;line-height:1.3;margin-bottom:3px}}
    .nhr {{border:none;border-top:1px solid {rgba(a2,.8)};margin:2px 0 4px}}
    .irow{{display:flex;gap:4px;justify-content:center;flex-wrap:wrap;margin-top:9px}}

    /* Right panel — x:730–1140 */
    .pr{{position:absolute;left:730px;top:0;width:410px;height:100%;
         display:flex;flex-direction:column;align-items:center}}
    .rcat {{font-size:20px;color:#fff;font-weight:500;margin-top:6px}}
    .rline{{width:110px;height:2px;background:{rgb(a2)};margin:8px 0}}
    .rname{{font-size:{ns}px;font-weight:700;color:{rgb(nc)};
            text-shadow:2px 2px 4px rgba(0,0,0,.6);line-height:1.05;
            text-align:center;padding:0 8px;flex:1;
            display:flex;align-items:center;justify-content:center}}
    .rmass{{font-size:13px;color:#fff;font-weight:500;margin-bottom:46px}}

    /* Date strip — right edge */
    .ds{{position:absolute;right:0;top:9px;bottom:9px;width:38px;
         background:rgba(255,255,255,.9);
         display:flex;align-items:center;justify-content:center}}
    .dst{{writing-mode:vertical-lr;transform:rotate(180deg);
          font-size:9px;color:#1a1a1a;white-space:nowrap}}

    /* Barcode box — bottom-left */
    .bc{{position:absolute;left:14px;top:494px;width:161px;height:86px;
         background:rgba(255,255,255,0.92);border-radius:4px;
         display:flex;align-items:center;justify-content:center;
         color:rgba(0,0,0,0.35);font-size:10px;letter-spacing:1.5px}}
  </style>
</head>
<body>
<a class="back" href="index.html">← Всі етикетки</a>
<p class="meta">{H.escape(p['key'].replace('_',' '))} · Харчовий ярлик</p>

<div class="label">
  <div class="bar-l"></div>
  <div class="bar-t"></div>
  <div class="bar-b"></div>
  <div class="bar-i"></div>
  <div class="sep"></div>

  <!-- ── LEFT PANEL ── -->
  <div class="pl">
    <div class="hdr">СКЛАД:</div>
    <div class="btxt">{H.escape(p['ingredients'])}</div>

    <div class="hdr">УМОВИ ЗБЕРІГАННЯ:</div>
    <div class="stxt">{mark_italic(p['storage'])}</div>

    <div class="hdr2">АДРЕСА ВИРОБНИЧИХ ПОТУЖНОСТЕЙ:</div>
    <div class="stxt">{H.escape(p['address'])}</div>

    <div class="hdr2">ВИРОБНИК:</div>
    <div class="stxt">{H.escape(p['manufacturer'])}</div>

    <div class="hdr2">ВИГОТОВЛЕНО НА ЗАМОВЛЕННЯ:</div>
    <div class="stxt">{H.escape(p['commission'])}</div>
    <div class="dtxt">Дата «Краще спожити до» та номер партії (L) вказані на етикетці.</div>
  </div>

  <!-- ── NUTRITION PANEL ── -->
  <div class="pn">
    <div class="nhdr">Поживна цінність на 100&nbsp;g(г) продукту</div>
    <hr class="nhr">
    {rows_html}
    <div class="irow">{icons_html}</div>
  </div>

  <!-- ── RIGHT PANEL ── -->
  <div class="pr">
    <div style="height:72px"></div>
    <img src="../icons/logo_white.png" alt="Food Festival"
         style="max-height:255px;max-width:310px;object-fit:contain;">
    <div class="rcat">{H.escape(p['category'])}</div>
    <div class="rline"></div>
    <div class="rname">{H.escape(p['name'])}</div>
    <div class="rmass">МАСА НЕТТО&nbsp;{H.escape(p['weight'])}&nbsp;г&nbsp;<span style="font-size:22px;vertical-align:middle;line-height:0.9;font-weight:400">е</span></div>
  </div>

  <!-- ── DATE STRIP ── -->
  <div class="ds">
    <span class="dst">Дата «Краще спожити до» та номер партії (L)</span>
  </div>

  <!-- ── BARCODE ── -->
  <div class="bc">ШТРИХКОД</div>
</div>
</body>
</html>"""


# ─────────────────────────────────────────────
# 5.  Index page
# ─────────────────────────────────────────────
def generate_index() -> str:
    cards = ""
    for p in PRODUCTS:
        fname = p["output"].replace(".jpg", ".html")
        a2    = p["accent2"]
        cards += (
            f'<a href="{fname}" class="card">'
            f'<div class="preview-wrap"><iframe src="{fname}" scrolling="no" tabindex="-1"></iframe></div>'
            f'<div class="card-lbl" style="color:{rgb(a2)}">'
            + H.escape(p["category"]) + ' · ' + H.escape(p["name"])
            + f'</div>'
            f'<div class="card-sub">{p["weight"]}&nbsp;г</div>'
            f'</a>\n'
        )

    return f"""<!DOCTYPE html>
<html lang="uk">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Food Festival — Усі етикетки</title>
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:wght@400;700&display=swap" rel="stylesheet">
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:#111;color:#ddd;font-family:'Ubuntu',Arial,sans-serif;padding:30px 20px}}
    h1{{font-size:22px;font-weight:700;color:#eee;margin-bottom:6px}}
    .sub{{font-size:12px;color:#666;margin-bottom:28px}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:20px}}
    .card{{background:#1e1e1e;border:1px solid #2a2a2a;border-radius:8px;overflow:hidden;
           text-decoration:none;transition:transform .15s,border-color .15s;display:block}}
    .card:hover{{transform:translateY(-3px);border-color:#444}}
    .preview-wrap{{position:relative;overflow:hidden;width:100%;
                   aspect-ratio:1178/594;background:#111}}
    .preview-wrap iframe{{display:block;width:1178px;height:594px;border:none;
                          transform-origin:top left;pointer-events:none;
                          transform:scale(0.289)}}
    .card-lbl{{font-size:13px;font-weight:700;padding:8px 12px 2px}}
    .card-sub{{font-size:11px;color:#666;padding:0 12px 10px}}
    .ref{{margin-top:32px}}
    .ref h2{{font-size:15px;color:#888;margin-bottom:12px}}
    .ref-imgs{{display:flex;gap:16px;flex-wrap:wrap}}
    .ref-imgs img{{border-radius:6px;border:1px solid #2a2a2a;max-height:200px;width:auto}}
    .ref-cap{{font-size:11px;color:#555;margin-top:4px}}
  </style>
</head>
<body>
<h1>Food Festival — Харчові ярлики</h1>
<p class="sub">11 продуктів · Натисніть для перегляду ярлика</p>
<div class="grid">
{cards}
</div>
<div class="ref">
  <h2>Приклади розміщення дати (з Форма коригувань.xlsx)</h2>
  <div class="ref-imgs">
    <div><img src="../icons/priklad_1.png" alt="Приклад 1"><p class="ref-cap">Приклад 1 — розміщення дати</p></div>
    <div><img src="../icons/priklad_2.png" alt="Приклад 2"><p class="ref-cap">Приклад 2 — зразок ярлика</p></div>
  </div>
</div>
<script>
function scaleFrames(){{
  document.querySelectorAll('.preview-wrap').forEach(function(w){{
    w.querySelector('iframe').style.transform='scale('+w.offsetWidth/1178+')';
  }});
}}
window.addEventListener('load',scaleFrames);
window.addEventListener('resize',scaleFrames);
</script>
</body>
</html>"""


# ─────────────────────────────────────────────
# 6.  Main
# ─────────────────────────────────────────────
def main():
    print("── Icons ──────────────────────────────────")
    setup_icons()

    print("\n── Cleanup ────────────────────────────────")
    cleanup_temp_files()

    os.makedirs(HTML_DIR, exist_ok=True)

    print(f"\n── HTML labels ({len(PRODUCTS)}) ──────────────────")
    for p in PRODUCTS:
        html  = generate_html(p)
        fname = p["output"].replace(".jpg", ".html")
        fpath = os.path.join(HTML_DIR, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  ✓  {fname}")

    print("\n── Index ───────────────────────────────────")
    idx_path = os.path.join(HTML_DIR, "index.html")
    with open(idx_path, "w", encoding="utf-8") as f:
        f.write(generate_index())
    print(f"  ✓  index.html")

    print(f"\nDone → {HTML_DIR}/")


if __name__ == "__main__":
    main()
