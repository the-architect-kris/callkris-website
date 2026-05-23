#!/usr/bin/env python3
"""Generate Kris Kereluk text wordmark PNG assets."""

from PIL import Image, ImageDraw, ImageFont
import os
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
NAME_FONT = os.path.join(BASE, ".fonts", "PlayfairDisplay-Bold.ttf")
DESC_FONT = os.path.join(BASE, ".fonts", "Inter-SemiBold.ttf")

INK = (9, 35, 82, 255)
ACCENT = (227, 123, 72, 255)
WHITE = (255, 255, 255, 255)

FONT_URLS = {
    NAME_FONT: "https://fonts.gstatic.com/s/playfairdisplay/v40/nuFvD-vYSZviVYUb_rj3ij__anPXJzDwcbmjWBN2PKeiukDQ.ttf",
    DESC_FONT: "https://fonts.gstatic.com/s/inter/v20/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuGKYMZg.ttf",
}


def ensure_fonts():
    os.makedirs(os.path.dirname(NAME_FONT), exist_ok=True)
    for path, url in FONT_URLS.items():
        if not os.path.isfile(path):
            urllib.request.urlretrieve(url, path)


def tracking_width(draw, text, font, ratio=0.16):
    tracking = font.size * ratio
    total = 0.0
    for i, ch in enumerate(text):
        total += draw.textlength(ch, font=font)
        if i < len(text) - 1:
            total += tracking
    return total


def draw_tracking(draw, pos, text, font, fill, ratio=0.16):
    x, y = pos
    tracking = font.size * ratio
    for i, ch in enumerate(text):
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font)
        if i < len(text) - 1:
            x += tracking


def render(scale=1.0, variant="light", pad=None):
    if pad is None:
        pad = round(12 * scale)

    name_px = round(20 * scale)
    desc_px = round(9.28 * scale)
    gap = round(3 * scale)
    bottom_pad = round(6 * scale)

    name_font = ImageFont.truetype(NAME_FONT, name_px)
    desc_font = ImageFont.truetype(DESC_FONT, desc_px)

    name = "Kris Kereluk"
    desc = "PERSONAL REAL ESTATE CORP"

    name_bbox = name_font.getbbox(name)
    desc_bbox = desc_font.getbbox(desc)
    name_w = name_bbox[2] - name_bbox[0]
    name_h = name_bbox[3] - name_bbox[1]
    desc_h = desc_bbox[3] - desc_bbox[1]

    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    desc_w = tracking_width(probe, desc, desc_font)

    w = int(max(name_w, desc_w) + pad * 2)
    h = int(name_h + gap + desc_h + pad + bottom_pad)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    name_color = WHITE if variant == "dark" else INK

    name_y = pad - name_bbox[1]
    draw.text((pad, name_y), name, font=name_font, fill=name_color)
    desc_y = pad + name_h + gap - desc_bbox[1]
    draw_tracking(draw, (pad, desc_y), desc, desc_font, ACCENT)

    return img


def main():
    ensure_fonts()

    ref = render(scale=1.0, variant="light")
    base_w, base_h = ref.size

    print_dir = os.path.join(BASE, "print")
    web_dir = os.path.join(BASE, "web")
    os.makedirs(print_dir, exist_ok=True)
    os.makedirs(web_dir, exist_ok=True)

    for variant in ("light", "dark"):
        for target_w, label in ((512, "512w"), (256, "256w"), (128, "128w")):
            scale = target_w / base_w
            img = render(scale=scale, variant=variant)
            out = os.path.join(web_dir, f"kris-kereluk-wordmark-{variant}-{label}.png")
            img.save(out, optimize=True)
            print("web", variant, label, img.size)

        for target_w, label in ((1200, "1200w"), (2400, "2400w"), (3600, "3600w")):
            scale = target_w / base_w
            img = render(scale=scale, variant=variant, pad=round(24 * scale))
            out = os.path.join(print_dir, f"kris-kereluk-wordmark-{variant}-{label}.png")
            img.save(out, optimize=True)
            print("print", variant, label, img.size)

    # SVG viewBox reference
    print("base", base_w, base_h)


if __name__ == "__main__":
    main()
