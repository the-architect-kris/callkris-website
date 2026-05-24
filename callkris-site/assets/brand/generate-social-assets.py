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
HERO_PHOTO = os.path.join(UPLOADS, "Kris-and-Marco-Real-Estate-Houses-36-1024x683.jpg")

INK = (9, 35, 82)
ACCENT = (227, 123, 72)
WHITE = (255, 255, 255)

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


def draw_gradient_overlay(canvas: Image.Image) -> None:
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    width, height = canvas.size

    for x in range(width):
        ratio = x / max(width - 1, 1)
        alpha = int(215 - ratio * 95)
        draw.line([(x, 0), (x, height)], fill=(*INK, alpha))

    for y in range(height):
        ratio = y / max(height - 1, 1)
        if ratio < 0.18:
            continue
        fade = int((ratio - 0.18) / 0.82 * 120)
        draw.line([(0, y), (width, y)], fill=(0, 0, 0, fade))

    canvas.alpha_composite(overlay)


def circular_avatar(source: Image.Image, size: int, border: int = 8) -> Image.Image:
    inner = ImageOps.fit(source, (size, size), method=Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    inner.putalpha(mask)

    total = size + border * 2
    framed = Image.new("RGBA", (total, total), (0, 0, 0, 0))
    ring = Image.new("RGBA", (total, total), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse((0, 0, total - 1, total - 1), fill=(*WHITE, 255))
    framed.alpha_composite(ring)
    framed.alpha_composite(inner, (border, border))
    return framed


def write_og_preview(avatar_source: Image.Image) -> None:
    width, height = 1200, 630
    photo = Image.open(HERO_PHOTO).convert("RGBA")
    canvas = cover_crop(photo, width, height)
    draw_gradient_overlay(canvas)
    draw = ImageDraw.Draw(canvas)

    eyebrow_font = load_font("inter-semibold", 18)
    name_font = load_font("playfair", 78)
    desc_font = load_font("inter-medium", 24)
    body_font = load_font("inter-medium", 22)
    url_font = load_font("inter-semibold", 20)

    draw.text((72, 86), "METRO VANCOUVER REAL ESTATE", font=eyebrow_font, fill=(*ACCENT, 255))
    draw.text((72, 126), "Kris Kereluk", font=name_font, fill=(*WHITE, 255))
    draw.text((72, 226), "Personal Real Estate Corp", font=desc_font, fill=(*ACCENT, 255))
    draw.text(
        (72, 286),
        "Buying · Selling · Featured Listings",
        font=body_font,
        fill=(255, 255, 255, 220),
    )
    draw.text(
        (72, 332),
        "Vancouver · Burnaby · New Westminster · Coquitlam · Port Moody",
        font=body_font,
        fill=(255, 255, 255, 185),
    )

    draw.rectangle((72, 548, 240, 552), fill=(*ACCENT, 255))
    draw.text((72, 566), "callkris.ca", font=url_font, fill=(*WHITE, 235))

    avatar = circular_avatar(avatar_source, 250, border=10)
    canvas.alpha_composite(avatar, (860, 170))

    canvas.convert("RGB").save(
        os.path.join(BASE, "og-preview.jpg"),
        format="JPEG",
        quality=88,
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
