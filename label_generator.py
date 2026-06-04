"""
Food Festival label generator — new style with food photo backgrounds.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os

ASSETS = os.path.join(os.path.dirname(__file__), "assets")
PHOTOS = os.path.join(ASSETS, "food_photos")
OUTPUT = os.path.join(os.path.dirname(__file__), "output_labels")
os.makedirs(OUTPUT, exist_ok=True)

FONT_BOLD   = "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"
FONT_MEDIUM = "/usr/share/fonts/truetype/ubuntu/Ubuntu-M.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf"

W, H = 1178, 594

# Per-product configuration
PRODUCTS = {
    "bbq": {
        "photo": "bbq.jpg",
        "accent": (200, 60, 20),        # deep orange-red
        "accent2": (255, 140, 0),       # amber
        "category": "СОУС",
        "name": "БАРБЕКЮ",
        "weight": "4900 г",
        "output": "bbq_new.jpg",
    },
    "ketchup_classic_5kg": {
        "photo": "ketchup.jpg",
        "accent": (190, 20, 20),
        "accent2": (230, 80, 40),
        "category": "КЕТЧУП",
        "name": "КЛАСИЧНИЙ",
        "weight": "5000 г",
        "output": "ketchup_classic_5kg_new.jpg",
    },
    "ketchup_classic_830": {
        "photo": "ketchup.jpg",
        "accent": (190, 20, 20),
        "accent2": (230, 80, 40),
        "category": "КЕТЧУП",
        "name": "КЛАСИЧНИЙ",
        "weight": "830 г",
        "output": "ketchup_classic_830_new.jpg",
    },
    "ketchup_premium": {
        "photo": "tomato.jpg",
        "accent": (30, 130, 30),
        "accent2": (100, 200, 50),
        "category": "КЕТЧУП",
        "name": "ПРЕМІУМ",
        "weight": "5000 г",
        "output": "ketchup_premium_new.jpg",
    },
    "ketchup_shashlik_5kg": {
        "photo": "grilled.jpg",
        "accent": (140, 20, 80),
        "accent2": (210, 60, 120),
        "category": "КЕТЧУП",
        "name": "ШАШЛИЧНИЙ",
        "weight": "5000 г",
        "output": "ketchup_shashlik_5kg_new.jpg",
    },
    "ketchup_shashlik_830": {
        "photo": "grilled.jpg",
        "accent": (140, 20, 80),
        "accent2": (210, 60, 120),
        "category": "КЕТЧУП",
        "name": "ШАШЛИЧНИЙ",
        "weight": "830 г",
        "output": "ketchup_shashlik_830_new.jpg",
    },
    "mayo_premium": {
        "photo": "mayo.jpg",
        "accent": (0, 90, 160),
        "accent2": (0, 160, 220),
        "category": "МАЙОНЕЗ",
        "name": "67% ПРЕМІУМ",
        "weight": "4900 г",
        "output": "mayo_premium_new.jpg",
    },
    "mayo_real": {
        "photo": "salad.jpg",
        "accent": (180, 40, 90),
        "accent2": (240, 100, 140),
        "category": "МАЙОНЕЗНИЙ СОУС",
        "name": "РЕАЛ",
        "weight": "4900 г",
        "output": "mayo_real_new.jpg",
    },
    "tomato_pasta": {
        "photo": "tomato.jpg",
        "accent": (200, 30, 10),
        "accent2": (240, 100, 30),
        "category": "ПАСТА",
        "name": "ТОМАТНА 25%",
        "weight": "4900 г",
        "output": "tomato_pasta_new.jpg",
    },
    "cheese_sauce": {
        "photo": "cheese.jpg",
        "accent": (180, 120, 0),
        "accent2": (240, 190, 30),
        "category": "СОУС",
        "name": "СИРНИЙ",
        "weight": "830 г",
        "output": "cheese_sauce_new.jpg",
    },
    "mustard_american": {
        "photo": "mustard.jpg",
        "accent": (170, 110, 0),
        "accent2": (230, 185, 30),
        "category": "ГІРЧИЦЯ",
        "name": "АМЕРИКАНСЬКА",
        "weight": "830 г",
        "output": "mustard_american_new.jpg",
    },
}


def make_gradient_overlay(size, color_left, color_right, alpha_left=200, alpha_right=30):
    w, h = size
    overlay = Image.new("RGBA", size)
    px = overlay.load()
    for x in range(w):
        t = x / w
        a = int(alpha_left + (alpha_right - alpha_left) * t)
        r = int(color_left[0] + (color_right[0] - color_left[0]) * t)
        g = int(color_left[1] + (color_right[1] - color_left[1]) * t)
        b = int(color_left[2] + (color_right[2] - color_left[2]) * t)
        for y in range(h):
            px[x, y] = (r, g, b, a)
    return overlay


def make_dark_overlay(size, alpha=120):
    overlay = Image.new("RGBA", size, (0, 0, 0, alpha))
    return overlay


def draw_logo_text(draw, cx, y, font_m, font_r):
    """Draw text-based Food Festival logo centered at cx, top at y."""
    # Chef hat — simple geometric shape drawn with PIL
    draw.ellipse([cx-22, y+4, cx+22, y+30], fill=(255, 255, 255))
    draw.ellipse([cx-14, y, cx+14, y+20], fill=(255, 255, 255))
    draw.rectangle([cx-22, y+24, cx+22, y+36], fill=(255, 255, 255))

    # "Food Festival" text
    bbox_food = draw.textbbox((0, 0), "Food", font=font_r)
    fw = bbox_food[2] - bbox_food[0]
    draw.text((cx - fw // 2, y + 38), "Food", font=font_r, fill=(255, 255, 255))

    bbox_fest = draw.textbbox((0, 0), "Festival", font=font_r)
    fw2 = bbox_fest[2] - bbox_fest[0]
    draw.text((cx - fw2 // 2, y + 58), "Festival", font=font_r, fill=(255, 255, 255))

    # Divider line
    draw.line([cx - 40, y + 82, cx + 40, y + 82], fill=(255, 255, 255), width=1)


def draw_accent_bar(img_rgba, accent, accent2):
    """Draw a diagonal accent stripe across the image."""
    overlay = Image.new("RGBA", img_rgba.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    # diagonal band from top-left area cutting across
    pts = [(W // 2 - 60, 0), (W // 2 + 80, 0), (W // 2 - 80, H), (W // 2 - 220, H)]
    draw.polygon(pts, fill=accent + (60,))
    return Image.alpha_composite(img_rgba, overlay)


def generate_label(product_key):
    cfg = PRODUCTS[product_key]
    accent = cfg["accent"]
    accent2 = cfg["accent2"]

    # --- Background ---
    photo_path = os.path.join(PHOTOS, cfg["photo"])
    bg = Image.open(photo_path).convert("RGB")
    # crop to label aspect ratio from center
    bw, bh = bg.size
    target_ratio = W / H
    if bw / bh > target_ratio:
        new_w = int(bh * target_ratio)
        x0 = (bw - new_w) // 2
        bg = bg.crop((x0, 0, x0 + new_w, bh))
    else:
        new_h = int(bw / target_ratio)
        y0 = (bh - new_h) // 2
        bg = bg.crop((0, y0, bw, y0 + new_h))
    bg = bg.resize((W, H), Image.LANCZOS)

    # Slight desaturate then enhance colors
    enhancer = ImageEnhance.Color(bg)
    bg = enhancer.enhance(1.3)
    enhancer = ImageEnhance.Contrast(bg)
    bg = enhancer.enhance(1.1)

    # Gentle blur on far right only (so product name area stays sharp)
    bg_blurred = bg.filter(ImageFilter.GaussianBlur(radius=3))
    # blend: left = blurred (text area), right = sharp (photo area)
    mask = Image.new("L", (W, H))
    for x in range(W):
        v = int(255 * min(1.0, x / (W * 0.55)))
        for y in range(H):
            mask.putpixel((x, y), v)
    bg = Image.composite(bg, bg_blurred, mask)

    base = bg.convert("RGBA")

    # Dark overlay (heavier on left for text legibility)
    dark = make_gradient_overlay((W, H), (0, 0, 0), (0, 0, 0), alpha_left=185, alpha_right=55)
    base = Image.alpha_composite(base, dark)

    # Brand color gradient overlay
    color_ov = make_gradient_overlay((W, H), accent, accent2, alpha_left=110, alpha_right=30)
    base = Image.alpha_composite(base, color_ov)

    # Diagonal accent stripe
    base = draw_accent_bar(base, accent, accent2)

    # --- Right panel highlight (where logo+name lives) ---
    right_panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rp_draw = ImageDraw.Draw(right_panel)
    # Soft vignette on right side
    rp_draw.rectangle([W * 2 // 3, 0, W, H], fill=(0, 0, 0, 40))
    base = Image.alpha_composite(base, right_panel)

    # --- Accent top bar ---
    top_bar = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tb_draw = ImageDraw.Draw(top_bar)
    tb_draw.rectangle([0, 0, W, 6], fill=accent + (255,))
    tb_draw.rectangle([0, H - 6, W, H], fill=accent2 + (255,))
    base = Image.alpha_composite(base, top_bar)

    # --- Left accent border ---
    left_bar = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lb_draw = ImageDraw.Draw(left_bar)
    lb_draw.rectangle([0, 0, 5, H], fill=accent + (255,))
    base = Image.alpha_composite(base, left_bar)

    # --- Typography ---
    draw = ImageDraw.Draw(base)

    font_name_large  = ImageFont.truetype(FONT_BOLD, 90)
    font_name_medium = ImageFont.truetype(FONT_BOLD, 72)
    font_category    = ImageFont.truetype(FONT_MEDIUM, 22)
    font_logo        = ImageFont.truetype(FONT_MEDIUM, 18)
    font_logo_r      = ImageFont.truetype(FONT_REGULAR, 16)
    font_small       = ImageFont.truetype(FONT_REGULAR, 11)
    font_tiny        = ImageFont.truetype(FONT_REGULAR, 10)

    # Logo area (right side, centered in right 1/3)
    logo_cx = W * 5 // 6
    draw_logo_text(draw, logo_cx, 30, font_logo, font_logo_r)

    # Category label
    cat_text = cfg["category"]
    bbox = draw.textbbox((0, 0), cat_text, font=font_category)
    cw = bbox[2] - bbox[0]
    draw.text((logo_cx - cw // 2, 122), cat_text, font=font_category, fill=(255, 255, 255))

    # Accent line under category
    draw.line([logo_cx - 50, 148, logo_cx + 50, 148], fill=accent2, width=2)

    # Product name (large, right-center, positioned below category)
    name_text = cfg["name"]
    # Try large font, scale down if too wide
    font_name = font_name_large
    bbox = draw.textbbox((0, 0), name_text, font=font_name)
    nw = bbox[2] - bbox[0]
    if nw > W * 0.55:
        font_name = font_name_medium
        bbox = draw.textbbox((0, 0), name_text, font=font_name)
        nw = bbox[2] - bbox[0]

    nh = bbox[3] - bbox[1]
    nx = logo_cx - nw // 2
    ny = H // 2 - nh // 2 + 10

    # Shadow
    draw.text((nx + 3, ny + 3), name_text, font=font_name, fill=(0, 0, 0, 160))
    # Main text
    draw.text((nx, ny), name_text, font=font_name, fill=(255, 255, 255))
    # Accent color highlight stroke
    draw.text((nx - 1, ny - 1), name_text, font=font_name, fill=accent2 + (80,))

    # Weight badge
    weight_text = cfg["weight"]
    bbox_w = draw.textbbox((0, 0), weight_text, font=font_category)
    ww = bbox_w[2] - bbox_w[0]
    wx = logo_cx - ww // 2 - 10
    wy = H - 55
    draw.rounded_rectangle([wx - 8, wy - 4, wx + ww + 8, wy + 22], radius=4,
                            fill=accent + (180,))
    draw.text((wx, wy), weight_text, font=font_category, fill=(255, 255, 255))

    # --- Left side: info panels ---
    left_x = 18
    panel_w = W * 5 // 12

    # Semi-transparent left info panel
    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    p_draw = ImageDraw.Draw(panel)
    p_draw.rounded_rectangle([left_x, 20, left_x + panel_w, H - 20],
                              radius=8, fill=(0, 0, 0, 100))
    base = Image.alpha_composite(base, panel)
    draw = ImageDraw.Draw(base)

    # Placeholder info text (left column)
    info_lines = [
        ("СКЛАД:", True),
        ("Вода питна, томатна паста, цукор,", False),
        ("загущувач, регулятори кислотності,", False),
        ("консервант, ароматизатор, спеції.", False),
        ("", False),
        ("УМОВИ ЗБЕРІГАННЯ:", True),
        ("Від 0°C до ±24°C. Відносна", False),
        ("вологість не більше 75%.", False),
        ("", False),
        ("ВИРОБНИК:", True),
        ("ТОВ «Аккаржа Плюс»", False),
        ("вул. Шевченка, 368, с. Овідіополь,", False),
        ("Одеська обл., 67801, Україна", False),
        ("", False),
        ("Тел.: +38 066-777-99-80", False),
    ]

    text_x = left_x + 12
    text_y = 35
    for line, is_header in info_lines:
        if not line:
            text_y += 5
            continue
        color = accent2 if is_header else (220, 220, 220)
        font = font_small if not is_header else ImageFont.truetype(FONT_MEDIUM, 11)
        draw.text((text_x, text_y), line, font=font, fill=color)
        text_y += 14 if is_header else 13

    # Nutrition table (right of left panel, left of center)
    tbl_x = left_x + panel_w + 14
    tbl_w = W // 6
    tbl_y = 30

    # Table panel
    tbl_panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tp_draw = ImageDraw.Draw(tbl_panel)
    tp_draw.rounded_rectangle([tbl_x - 4, tbl_y - 4, tbl_x + tbl_w + 4, H - 20],
                               radius=6, fill=(0, 0, 0, 100))
    base = Image.alpha_composite(base, tbl_panel)
    draw = ImageDraw.Draw(base)

    draw.text((tbl_x, tbl_y), "Поживна цінність", font=font_tiny, fill=accent2)
    draw.text((tbl_x, tbl_y + 12), "на 100 г продукту", font=font_tiny, fill=(200, 200, 200))
    draw.line([tbl_x, tbl_y + 24, tbl_x + tbl_w, tbl_y + 24], fill=accent2, width=1)

    rows = [
        ("Енергетична цінність", ""),
        ("(ккал)", "182"),
        ("(кДж)", "775"),
        ("Жири", "0,05 г"),
        ("Вуглеводи", "45,0 г"),
        ("- цукри", "40,0 г"),
        ("Білки", "0,4 г"),
        ("Сіль", "2,5 г"),
    ]
    ry = tbl_y + 28
    for label, value in rows:
        draw.text((tbl_x, ry), label, font=font_tiny, fill=(210, 210, 210))
        if value:
            vbbox = draw.textbbox((0, 0), value, font=font_tiny)
            vw = vbbox[2] - vbbox[0]
            draw.text((tbl_x + tbl_w - vw, ry), value, font=font_tiny, fill=(255, 255, 255))
        ry += 13

    # Icons row (БЕЗ ГМО etc.)
    icon_y = H - 48
    icon_font = ImageFont.truetype(FONT_MEDIUM, 9)
    for i, label in enumerate(["БЕЗ ГМО", "PP 05"]):
        ix = tbl_x + i * 52
        draw.rounded_rectangle([ix, icon_y, ix + 44, icon_y + 22], radius=3,
                                fill=(255, 255, 255, 30), outline=(255, 255, 255, 120))
        b = draw.textbbox((0, 0), label, font=icon_font)
        lw = b[2] - b[0]
        draw.text((ix + (44 - lw) // 2, icon_y + 6), label, font=icon_font, fill=(255, 255, 255))

    # Barcode placeholder
    bc_x = tbl_x + tbl_w + 18
    bc_y = H - 65
    draw.rectangle([bc_x, bc_y, bc_x + 110, H - 20], outline=(255, 255, 255, 150), width=1)
    bc_font = ImageFont.truetype(FONT_REGULAR, 9)
    draw.text((bc_x + 10, bc_y + 10), "ШТРИХКОД", font=bc_font, fill=(200, 200, 200))

    # Date field
    date_x = bc_x + 118
    draw.rectangle([date_x, bc_y, date_x + 80, H - 20], outline=(255, 255, 255, 150), width=1)

    # Mass netto bottom right
    mn_font = ImageFont.truetype(FONT_MEDIUM, 12)
    mn_text = f"МАСА НЕТТО {cfg['weight']} Е"
    draw.text((bc_x, bc_y - 18), mn_text, font=mn_font, fill=(255, 255, 255))

    # --- Final output ---
    result = base.convert("RGB")
    out_path = os.path.join(OUTPUT, cfg["output"])
    result.save(out_path, quality=95)
    print(f"Saved: {out_path}")
    return out_path


if __name__ == "__main__":
    import sys
    keys = sys.argv[1:] if len(sys.argv) > 1 else list(PRODUCTS.keys())
    for key in keys:
        if key in PRODUCTS:
            generate_label(key)
        else:
            print(f"Unknown product: {key}. Available: {list(PRODUCTS.keys())}")
