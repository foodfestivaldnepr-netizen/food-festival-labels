#!/usr/bin/env python3
"""
Embed EAN-13 barcodes into SVG labels and export to PDF.
Barcodes are mapped from barcode.xlsx data.
"""
import os, re, subprocess

BASE    = os.path.dirname(os.path.abspath(__file__))
SVG_DIR = os.path.join(BASE, "output_svg")
OUT_DIR = os.path.join(BASE, "output_print")
PDF_DIR = os.path.join(OUT_DIR, "pdf")
AI_DIR  = os.path.join(OUT_DIR, "ai")

os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(AI_DIR,  exist_ok=True)

# ── Barcode data from barcode.xlsx ──────────────────────────────────────────
BARCODES = {
    "01_sauce_bbq":          "4820219417569",
    "02_ketchup_classic_5kg":"4820219417460",
    "03_mayo_67":            "4820219417507",
    "04_mayo_real":          "4820219417514",
    "05_tomato_pasta":       "4820219417521",
    "06_ketchup_premium":    "4820219417491",
    "07_ketchup_shashlik_830":"4820219417446",
    "08_ketchup_shashlik_5kg":"4820219417453",
    "09_sauce_cheese":       "4820219417552",
    "10_mustard_american":   "4820219417538",
    "11_ketchup_classic_830":"4820219417477",
}

# ── EAN-13 encoder ───────────────────────────────────────────────────────────
# Each digit encoded as 7 binary modules (1=bar, 0=space)
_L = ["0001101","0011001","0010011","0111101","0100011",
      "0110001","0101111","0111011","0110111","0001011"]
_G = ["0100111","0110011","0011011","0100001","0011101",
      "0111001","0000101","0010001","0001001","0010111"]
_R = ["1110010","1100110","1101100","1000010","1011100",
      "1001110","1010000","1000100","1001000","1110100"]
_PARITY = ["LLLLLL","LLGLGG","LLGGLG","LLGGGL","LGLLGG",
           "LGGLLG","LGGGLL","LGLGLG","LGLGGL","LGGLGL"]

def ean13_check(digits12):
    """Compute EAN-13 check digit."""
    s = sum(d * (3 if i % 2 else 1) for i, d in enumerate(digits12))
    return (10 - s % 10) % 10

def ean13_modules(code):
    """Return list of (width, is_bar) tuples for the full EAN-13 barcode.
    Does NOT include quiet zones."""
    assert len(code) == 13
    digits = [int(c) for c in code]
    # Verify check digit
    assert digits[12] == ean13_check(digits[:12]), f"Bad check digit in {code}"

    first   = digits[0]
    parity  = _PARITY[first]
    left6   = digits[1:7]
    right6  = digits[7:13]

    bits = ""
    bits += "101"                           # left guard
    for i, d in enumerate(left6):
        bits += _G[d] if parity[i]=='G' else _L[d]
    bits += "01010"                         # centre guard
    for d in right6:
        bits += _R[d]
    bits += "101"                           # right guard

    # Compress consecutive same bits into runs
    runs = []
    cur = bits[0]; cnt = 1
    for b in bits[1:]:
        if b == cur:
            cnt += 1
        else:
            runs.append((cnt, cur == '1'))
            cur = b; cnt = 1
    runs.append((cnt, cur == '1'))
    return runs  # total = 95 modules

def ean13_svg(code, x, y, w, h, bar_color="black", text_color="black"):
    """
    Generate SVG elements for an EAN-13 barcode fitting in a w×h rectangle
    starting at (x, y). Returns a string of SVG elements.
    """
    runs   = ean13_modules(code)
    total  = sum(r[0] for r in runs)   # should be 95
    quiet  = 7                          # quiet zone modules on each side

    total_w_modules = total + 2 * quiet
    module_w = w / total_w_modules
    bar_h    = h * 0.80
    text_h   = h - bar_h
    font_sz  = text_h * 0.85

    elems = []
    cx = x + quiet * module_w          # start x after quiet zone

    for (width_m, is_bar) in runs:
        bar_w = width_m * module_w
        if is_bar:
            elems.append(
                f'<rect x="{cx:.3f}" y="{y:.3f}" '
                f'width="{bar_w:.3f}" height="{bar_h:.3f}" '
                f'fill="{bar_color}"/>'
            )
        cx += bar_w

    # Human-readable digits below bars — split as EAN-13 standard:
    # first digit | 6 digits | 6 digits
    text_y  = y + bar_h + font_sz * 0.9
    total_bar_w = total * module_w
    cx0 = x + quiet * module_w            # left guard start

    # First digit (left of barcode)
    elems.append(
        f'<text x="{x + quiet * module_w * 0.4:.3f}" y="{text_y:.3f}" '
        f'font-family="Ubuntu,sans-serif" font-size="{font_sz:.1f}" '
        f'fill="{text_color}" text-anchor="middle">{code[0]}</text>'
    )

    # Left 6 digits — centred over modules 4..45 (after left guard 3 + each digit 7 = 3+42)
    left_center_x = cx0 + (3 + 21) * module_w
    elems.append(
        f'<text x="{left_center_x:.3f}" y="{text_y:.3f}" '
        f'font-family="Ubuntu,sans-serif" font-size="{font_sz:.1f}" '
        f'fill="{text_color}" text-anchor="middle" letter-spacing="{module_w*1.3:.2f}">'
        f'{code[1:7]}</text>'
    )

    # Right 6 digits — centred over modules 51..92
    right_center_x = cx0 + (3 + 42 + 5 + 21) * module_w
    elems.append(
        f'<text x="{right_center_x:.3f}" y="{text_y:.3f}" '
        f'font-family="Ubuntu,sans-serif" font-size="{font_sz:.1f}" '
        f'fill="{text_color}" text-anchor="middle" letter-spacing="{module_w*1.3:.2f}">'
        f'{code[7:13]}</text>'
    )

    return "\n".join(elems)


def embed_barcode(svg_path, barcode_code, out_path):
    """Replace the placeholder barcode box with a real EAN-13 barcode."""
    with open(svg_path, encoding="utf-8") as f:
        content = f.read()

    # The placeholder section looks like:
    # <!-- Barcode box -->
    # <rect x="14" y="494" width="161" height="86" rx="4"
    # fill="white" fill-opacity="0.92"/>
    # <text ...>ШТРИХКОД</text>
    #
    # We replace everything from <!-- Barcode box --> to the closing </text>
    # of the ШТРИХКОД placeholder.

    # Build replacement: white background rect + real barcode
    bx, by, bw, bh = 14, 494, 161, 86
    pad = 4
    svg_barcode = ean13_svg(
        barcode_code,
        x  = bx + pad,
        y  = by + pad,
        w  = bw - 2*pad,
        h  = bh - 2*pad,
        bar_color   = "black",
        text_color  = "black",
    )

    new_block = (
        f'<!-- Barcode -->\n'
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="4" '
        f'fill="white" fill-opacity="0.96"/>\n'
        f'{svg_barcode}'
    )

    # Match the placeholder block (from comment to closing </text> of ШТРИХКОД)
    pattern = re.compile(
        r'<!-- Barcode box -->.*?letter-spacing="1\.5">ШТРИХКОД</text>',
        re.DOTALL
    )
    if pattern.search(content):
        new_content = pattern.sub(new_block, content)
    else:
        # Fallback: insert before </svg>
        new_content = content.replace("</svg>", new_block + "\n</svg>")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"  Barcode embedded: {os.path.basename(out_path)}")


def export_pdf(svg_path, pdf_path):
    """Export SVG to PDF using rsvg-convert."""
    result = subprocess.run(
        ["rsvg-convert", "--format=pdf", "-o", pdf_path, svg_path],
        capture_output=True
    )
    if result.returncode != 0:
        print(f"  ERROR exporting {svg_path}: {result.stderr.decode()}")
    else:
        print(f"  PDF: {os.path.basename(pdf_path)}")


def export_ai_from_svg(svg_path, ai_path):
    """Export to AI-compatible format: PDF exported via rsvg-convert.
    Modern .ai files are PDF-based; this PDF can be opened directly in Illustrator."""
    export_pdf(svg_path, ai_path)


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    tmp_dir = os.path.join(BASE, "output_svg_with_barcodes")
    os.makedirs(tmp_dir, exist_ok=True)

    for name, barcode_code in BARCODES.items():
        print(f"\n[{name}] → {barcode_code}")
        src_svg  = os.path.join(SVG_DIR, f"{name}.svg")
        tmp_svg  = os.path.join(tmp_dir, f"{name}.svg")
        pdf_out  = os.path.join(PDF_DIR, f"{name}.pdf")
        ai_out   = os.path.join(AI_DIR,  f"{name}.ai")

        if not os.path.exists(src_svg):
            print(f"  MISSING: {src_svg}")
            continue

        # 1. Embed barcode into SVG
        embed_barcode(src_svg, barcode_code, tmp_svg)

        # 2. Copy fonts dir into tmp for rsvg-convert
        fonts_src = os.path.join(SVG_DIR, "fonts")
        fonts_dst = os.path.join(tmp_dir, "fonts")
        if not os.path.exists(fonts_dst) and os.path.exists(fonts_src):
            import shutil
            shutil.copytree(fonts_src, fonts_dst)

        # 3. Export to PDF
        export_pdf(tmp_svg, pdf_out)

        # 4. Export to AI (PDF-based, openable in Adobe Illustrator)
        export_ai_from_svg(tmp_svg, ai_out)

    print("\nDone.")
    print(f"  PDFs: {PDF_DIR}")
    print(f"  AI:   {AI_DIR}")
    print(f"  SVGs with barcodes: {tmp_dir}")
