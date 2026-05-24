#!/usr/bin/env python3
"""Generate favicon and Open Graph preview assets for callkris.ca."""

from __future__ import annotations

import os
import urllib.request

from PIL import Image, ImageDraw, ImageFont, ImageOps

BASE = os.path.dirname(os.path.abspath(__file__))
SITE_ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
UPLOADS = os.path.join(SITE_ROOT, "wp-content", "uploads")
FONTS = os.path.join(BASE, ".fonts")

FAVICON_SOURCE_URL = (
    "https://cdn.lofty.com/image/fs/517975163338756/website/12194/"
    "cmsbuild/2025107_bb754ba208234180.png"
)
PORTRAIT_SOURCE = os.path.join(UPLOADS, "cropped-Kris-Kereluk-270x270.png")

INK = (9, 35, 82)
INK_DEEP = (5, 22, 50)
INK_HI = (14, 45, 102)
ACCENT = (227, 123, 72)
ACCENT_DK = (200, 101, 50)
WHITE = (255, 255, 255)
MUTED = (178, 192, 215)
CREAM = (244, 238, 226)

FONT_URLS = {
    "playfair": (
        os.path.join(FONTS, "PlayfairDisplay-Bold.ttf"),
        "https://fonts.gstatic.com/s/playfairdisplay/v40/"
        "nuFvD-vYSZviVYUb_rj3ij__anPXJzDwcbmjWBN2PKeiukDQ.ttf",
    ),
    "inter-semibold": (
        os.path.join(FONTS, "Inter-SemiBold.ttf"),
        "https://fonts.gstatic.com/s/inter/v20/"
        "UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuGKYMZg.ttf",
    ),
    "inter-medium": (
        os.path.join(FONTS, "Inter-Medium.ttf"),
        "https://fonts.gstatic.com/s/inter/v20/"
        "UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuI6fMZg.ttf",
    ),
}


def ensure_fonts() -> None:
    os.makedirs(FONTS, exist_ok=True)
    for _, (path, url) in FONT_URLS.items():
        if not os.path.isfile(path):
            urllib.request.urlretrieve(url, path)


def load_font(key: str, size: int) -> ImageFont.FreeTypeFont:
    path, _ = FONT_URLS[key]
    return ImageFont.truetype(path, size)


def fetch_favicon_source() -> Image.Image:
    cache = os.path.join(BASE, "favicon-source.png")
    if not os.path.isfile(cache):
        urllib.request.urlretrieve(FAVICON_SOURCE_URL, cache)
    return Image.open(cache).convert("RGBA")


def write_favicons(source: Image.Image) -> None:
    square = ImageOps.fit(source, (512, 512), method=Image.Resampling.LANCZOS)
    square.save(os.path.join(BASE, "favicon.png"))

    for size, name in (
        (180, "apple-touch-icon.png"),
        (32, "favicon-32x32.png"),
        (16, "favicon-16x16.png"),
    ):
        ImageOps.fit(source, (size, size), method=Image.Resampling.LANCZOS).save(
            os.path.join(BASE, name)
        )

    icon = ImageOps.fit(source, (48, 48), method=Image.Resampling.LANCZOS)
    icon.save(os.path.join(BASE, "favicon.ico"), format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
    icon.save(os.path.join(SITE_ROOT, "favicon.ico"), format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])


def cover_crop(image: Image.Image, width: int, height: int) -> Image.Image:
    scale = max(width / image.width, height / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def draw_tracked_caps(
    draw: ImageDraw.ImageDraw,
    pos: tuple[float, float],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    tracking: float = 0.22,
) -> float:
    x, y = pos
    spacing = font.size * tracking
    for char in text:
        draw.text((x, y), char, font=font, fill=fill)
        x += draw.textlength(char, font=font) + spacing
    return x


def gradient_background(width: int, height: int) -> Image.Image:
    canvas = Image.new("RGBA", (width, height), (*INK_DEEP, 255))
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(height):
        t = y / max(height - 1, 1)
        r = int(INK_DEEP[0] + (INK_HI[0] - INK_DEEP[0]) * t)
        g = int(INK_DEEP[1] + (INK_HI[1] - INK_DEEP[1]) * t)
        b = int(INK_DEEP[2] + (INK_HI[2] - INK_DEEP[2]) * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
    canvas.alpha_composite(overlay)
    return canvas


def add_grain(canvas: Image.Image, strength: int = 6) -> None:
    import random

    random.seed(7)
    width, height = canvas.size
    grain = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    pixels = grain.load()
    for y in range(0, height, 2):
        for x in range(0, width, 2):
            value = random.randint(-strength, strength)
            alpha = 25 if value >= 0 else 18
            color = (255, 255, 255) if value >= 0 else (0, 0, 0)
            pixels[x, y] = (*color, alpha)
    canvas.alpha_composite(grain)


def rounded_card(image: Image.Image, radius: int) -> Image.Image:
    """Return image with rounded-corner mask applied."""
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, image.size[0] - 1, image.size[1] - 1),
        radius=radius,
        fill=255,
    )
    out = image.copy()
    if out.mode != "RGBA":
        out = out.convert("RGBA")
    out.putalpha(mask)
    return out


def write_og_preview(avatar_source: Image.Image) -> None:
    width, height = 1200, 630
    canvas = gradient_background(width, height)

    decor = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    decor_draw = ImageDraw.Draw(decor)
    decor_draw.ellipse((-220, -260, 360, 320), fill=(*INK_HI, 180))
    decor_draw.ellipse((780, 420, 1320, 960), fill=(*INK_HI, 150))
    canvas.alpha_composite(decor)

    add_grain(canvas)

    card_w, card_h = 360, 470
    card_x, card_y = 760, 80
    card_bg = Image.new("RGBA", (card_w + 20, card_h + 20), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(card_bg)
    shadow_draw.rounded_rectangle(
        (10, 14, card_w + 10, card_h + 14),
        radius=22,
        fill=(0, 0, 0, 110),
    )
    canvas.alpha_composite(card_bg, (card_x - 10, card_y - 4))

    portrait = Image.open(PORTRAIT_SOURCE).convert("RGBA")
    portrait = ImageOps.fit(portrait, (card_w, card_h), method=Image.Resampling.LANCZOS)
    portrait = rounded_card(portrait, radius=20)
    canvas.alpha_composite(portrait, (card_x, card_y))

    rule = Image.new("RGBA", (card_w + 36, 10), (0, 0, 0, 0))
    ImageDraw.Draw(rule).rectangle((0, 0, 80, 8), fill=(*ACCENT, 255))
    canvas.alpha_composite(rule, (card_x - 18, card_y + card_h + 22))

    draw = ImageDraw.Draw(canvas)

    badge_font = load_font("inter-semibold", 14)
    badge_text = "REALTOR® · SUTTON GROUP"
    badge_w = sum(
        draw.textlength(c, font=badge_font) + badge_font.size * 0.22 for c in badge_text
    )
    badge_x = card_x + (card_w - int(badge_w)) // 2
    draw_tracked_caps(draw, (badge_x, card_y + card_h + 50), badge_text, badge_font, MUTED)

    bar_x = 72
    draw.rectangle((bar_x, 86, bar_x + 48, 90), fill=(*ACCENT, 255))

    eyebrow_font = load_font("inter-semibold", 16)
    name_font = load_font("playfair", 118)
    role_font = load_font("inter-semibold", 20)
    lead_font = load_font("playfair", 28)
    url_font = load_font("inter-semibold", 26)
    phone_font = load_font("inter-medium", 22)

    draw_tracked_caps(
        draw,
        (bar_x, 108),
        "METRO VANCOUVER REAL ESTATE",
        eyebrow_font,
        ACCENT,
    )

    draw.text((bar_x - 6, 154), "Kris", font=name_font, fill=WHITE)
    draw.text((bar_x - 6, 278), "Kereluk.", font=name_font, fill=CREAM)

    draw_tracked_caps(
        draw,
        (bar_x, 418),
        "PERSONAL REAL ESTATE CORP",
        role_font,
        ACCENT,
        tracking=0.18,
    )

    draw.text(
        (bar_x, 458),
        "Trusted guidance for buying",
        font=lead_font,
        fill=WHITE,
    )
    draw.text(
        (bar_x, 496),
        "& selling across Metro Vancouver.",
        font=lead_font,
        fill=WHITE,
    )

    footer_y = height - 64
    rule_w = 620
    draw.line(
        [(bar_x, footer_y - 16), (bar_x + rule_w, footer_y - 16)],
        fill=(*MUTED, 110),
        width=1,
    )
    draw.text((bar_x, footer_y), "callkris.ca", font=url_font, fill=WHITE)
    phone_text = "778 · 288 · 4481"
    phone_w = draw.textlength(phone_text, font=phone_font)
    draw.text(
        (bar_x + rule_w - phone_w, footer_y + 3),
        phone_text,
        font=phone_font,
        fill=ACCENT,
    )

    canvas.convert("RGB").save(
        os.path.join(BASE, "og-preview.jpg"),
        format="JPEG",
        quality=92,
        optimize=True,
    )


def main() -> None:
    ensure_fonts()
    favicon_source = fetch_favicon_source()
    write_favicons(favicon_source)
    write_og_preview(favicon_source)
    print("Generated favicon + og-preview assets in assets/brand/")


if __name__ == "__main__":
    main()
