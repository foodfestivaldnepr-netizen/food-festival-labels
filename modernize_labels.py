"""
Modernize Food Festival labels:
- Detect solid background color
- Replace it with a food photo + gradient
- Add modern accent elements
- Preserve ALL original text, logo, and content
"""

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np
import os

BASE    = os.path.dirname(__file__)
PHOTOS  = os.path.join(BASE, "assets", "food_photos")
SRC     = os.path.join(BASE, "received_photos")
OUT     = os.path.join(BASE, "output_labels")
os.makedirs(OUT, exist_ok=True)

# Map each source file → food photo + accent colors
LABEL_CONFIG = {
    "20260601_123511_8586.jpg": {  # Соус Барбекю — BBQ grilled meat
        "photo": "bbq_sauce.jpg",
        "accent": (200, 60, 10),
        "accent2": (255, 140, 30),
        "out": "01_sauce_bbq.jpg",
    },
    "20260601_123512_3068.jpg": {  # Кетчуп Класичний 5кг — fresh tomatoes
        "photo": "tomatoes.jpg",
        "accent": (185, 15, 15),
        "accent2": (235, 65, 25),
        "out": "02_ketchup_classic_5kg.jpg",
    },
    "20260601_123512_6203.jpg": {  # Майонез 67% — eggs (mayo is egg-based)
        "photo": "eggs.jpg",
        "accent": (10, 75, 165),
        "accent2": (25, 150, 220),
        "out": "03_mayo_67.jpg",
    },
    "20260601_123512_8908.jpg": {  # Майонезний соус Реал — pink sauce / salad
        "photo": "pink_sauce.jpg",
        "accent": (185, 35, 95),
        "accent2": (240, 95, 145),
        "out": "04_mayo_real.jpg",
    },
    "20260601_123513_1656.jpg": {  # Паста томатна 25% — ripe tomatoes
        "photo": "tomatoes.jpg",
        "accent": (190, 22, 8),
        "accent2": (238, 95, 28),
        "out": "05_tomato_pasta.jpg",
    },
    "20260601_123513_4266.jpg": {  # Кетчуп Преміум (green) — fresh herbs/greens
        "photo": "herbs_green.jpg",
        "accent": (18, 125, 28),
        "accent2": (85, 195, 45),
        "out": "06_ketchup_premium.jpg",
    },
    "20260601_123513_6773.jpg": {  # Кетчуп Шашличний 830г — shashlik/grilled meat
        "photo": "shashlik.jpg",
        "accent": (145, 18, 75),
        "accent2": (215, 55, 125),
        "out": "07_ketchup_shashlik_830.jpg",
    },
    "20260601_123513_9326.jpg": {  # Кетчуп Шашличний 5кг — shashlik/grilled meat
        "photo": "shashlik.jpg",
        "accent": (145, 18, 75),
        "accent2": (215, 55, 125),
        "out": "08_ketchup_shashlik_5kg.jpg",
    },
    "20260601_123514_1570.jpg": {  # Соус Сирний — melted cheese
        "photo": "cheese_melt.jpg",
        "accent": (172, 115, 0),
        "accent2": (238, 190, 28),
        "out": "09_sauce_cheese.jpg",
    },
    "20260601_123514_4495.jpg": {  # Гірчиця Американська — hot dog / american food
        "photo": "hotdog.jpg",
        "accent": (162, 102, 0),
        "accent2": (228, 182, 28),
        "out": "10_mustard_american.jpg",
    },
    "20260601_123514_9240.jpg": {  # Кетчуп Класичний 830г — fresh tomatoes
        "photo": "tomatoes.jpg",
        "accent": (185, 15, 15),
        "accent2": (235, 65, 25),
        "out": "11_ketchup_classic_830.jpg",
    },
}


def smart_crop_resize(img, target_w, target_h):
    """Center-crop to target aspect ratio, then resize."""
    iw, ih = img.size
    target_ratio = target_w / target_h
    if iw / ih > target_ratio:
        new_w = int(ih * target_ratio)
        x0 = (iw - new_w) // 2
        img = img.crop((x0, 0, x0 + new_w, ih))
    else:
        new_h = int(iw / target_ratio)
        y0 = (ih - new_h) // 2
        img = img.crop((0, y0, iw, y0 + new_h))
    return img.resize((target_w, target_h), Image.LANCZOS)


def sample_bg_color(img_arr, margin=15):
    """
    Sample background color from the four corner regions.
    Returns the median color to avoid noise.
    """
    h, w = img_arr.shape[:2]
    m = margin
    samples = np.concatenate([
        img_arr[:m, :m].reshape(-1, 3),
        img_arr[:m, w-m:].reshape(-1, 3),
        img_arr[h-m:, :m].reshape(-1, 3),
        img_arr[h-m:, w-m:].reshape(-1, 3),
    ])
    return np.median(samples, axis=0).astype(np.float32)


def build_bg_mask(img_arr, bg_color, tolerance=55, feather=4):
    """
    Returns a float mask [0..1]:
      1.0 = pure background (replace with food photo)
      0.0 = content (keep original)
    """
    diff = np.sqrt(np.sum((img_arr.astype(np.float32) - bg_color) ** 2, axis=2))
    mask = np.clip((tolerance - diff) / tolerance, 0, 1)

    # Feather edges for a smooth blend
    mask_img = Image.fromarray((mask * 255).astype(np.uint8), "L")
    mask_img = mask_img.filter(ImageFilter.GaussianBlur(feather))
    return np.array(mask_img).astype(np.float32) / 255.0


def make_horizontal_gradient(size, color_l, alpha_l, color_r, alpha_r):
    """RGBA gradient left→right."""
    w, h = size
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    for x in range(w):
        t = x / (w - 1)
        r = int(color_l[0] * (1-t) + color_r[0] * t)
        g = int(color_l[1] * (1-t) + color_r[1] * t)
        b = int(color_l[2] * (1-t) + color_r[2] * t)
        a = int(alpha_l   * (1-t) + alpha_r   * t)
        arr[:, x] = [r, g, b, a]
    return Image.fromarray(arr, "RGBA")


def add_modern_accents(img_rgba, accent, accent2, W, H):
    """Overlay modern design elements onto the label."""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Top accent bar (thick)
    draw.rectangle([0, 0, W, 7], fill=accent + (255,))
    # Bottom accent bar
    draw.rectangle([0, H - 7, W, H], fill=accent2 + (255,))
    # Left side accent stripe
    draw.rectangle([0, 0, 6, H], fill=accent + (230,))

    # Thin accent2 line just inside top bar
    draw.rectangle([7, 10, W, 13], fill=accent2 + (180,))

    # Diagonal light stripe (decorative)
    stripe = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stripe)
    cx = W // 2
    pts = [(cx - 40, 0), (cx + 40, 0), (cx - 10, H), (cx - 90, H)]
    sd.polygon(pts, fill=accent2 + (18,))
    overlay = Image.alpha_composite(overlay, stripe)

    return Image.alpha_composite(img_rgba, overlay)


def modernize(src_filename, cfg):
    label_path = os.path.join(SRC, src_filename)
    photo_path = os.path.join(PHOTOS, cfg["photo"])
    out_path   = os.path.join(OUT, cfg["out"])

    accent  = cfg["accent"]
    accent2 = cfg["accent2"]

    # --- Load label ---
    label = Image.open(label_path).convert("RGB")
    W, H = label.size
    label_arr = np.array(label)

    # --- Detect background ---
    bg_color = sample_bg_color(label_arr)
    mask = build_bg_mask(label_arr, bg_color, tolerance=58, feather=3)

    # --- Prepare food photo background ---
    food = Image.open(photo_path).convert("RGB")
    food = smart_crop_resize(food, W, H)

    # Slightly warm up colors in the food photo
    food = ImageEnhance.Color(food).enhance(1.35)
    food = ImageEnhance.Contrast(food).enhance(1.1)
    food = ImageEnhance.Brightness(food).enhance(0.9)

    # Apply accent color tint to food photo (subtle brand coloring)
    tint = Image.new("RGB", (W, H), accent)
    food = Image.blend(food, tint, 0.22)

    # Apply dark-left gradient over food (so left text stays readable)
    grad = make_horizontal_gradient((W, H),
                                    color_l=(0, 0, 0), alpha_l=155,
                                    color_r=(0, 0, 0), alpha_r=25)
    food_rgba = food.convert("RGBA")
    food_rgba = Image.alpha_composite(food_rgba, grad)
    food_final = np.array(food_rgba.convert("RGB"))

    # --- Composite: blend food photo into background areas ---
    mask_3ch = mask[:, :, np.newaxis]  # broadcast over RGB
    composited = (food_final * mask_3ch + label_arr * (1 - mask_3ch)).astype(np.uint8)
    result = Image.fromarray(composited).convert("RGBA")

    # --- Add modern accents on top ---
    result = add_modern_accents(result, accent, accent2, W, H)

    # --- Save ---
    result.convert("RGB").save(out_path, quality=95)
    print(f"  ✓  {cfg['out']}")
    return out_path


def run_all():
    print(f"Processing {len(LABEL_CONFIG)} labels...\n")
    outputs = []
    for src, cfg in LABEL_CONFIG.items():
        try:
            p = modernize(src, cfg)
            outputs.append(p)
        except Exception as e:
            print(f"  ✗  {src}: {e}")
    print(f"\nDone — {len(outputs)} labels saved to output_labels/")
    return outputs


if __name__ == "__main__":
    run_all()
