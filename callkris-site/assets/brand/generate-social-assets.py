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
HERO_PHOTO = os.path.join(UPLOADS, "Kris-and-Marco-Real-Estate-Houses-12-1024x683.jpg")
PANEL_WIDTH = 700

INK = (9, 35, 82)
INK_DEEP = (6, 26, 58)
ACCENT = (227, 123, 72)
WHITE = (255, 255, 255)
MUTED = (196, 206, 222)

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
    pos: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    tracking: float = 0.22,
) -> None:
    x, y = pos
    spacing = font.size * tracking
    for index, char in enumerate(text):
        draw.text((x, y), char, font=font, fill=fill)
        x += draw.textlength(char, font=font) + spacing


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: float,
) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = current + " " + word
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def write_og_preview(avatar_source: Image.Image) -> None:
    width, height = 1200, 630
    canvas = Image.new("RGBA", (width, height), (*INK, 255))
    draw = ImageDraw.Draw(canvas)

    photo = cover_crop(Image.open(HERO_PHOTO).convert("RGBA"), width - PANEL_WIDTH, height)
    photo_panel = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    photo_panel.paste(photo, (PANEL_WIDTH, 0))

    seam = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    seam_draw = ImageDraw.Draw(seam)
    for x in range(48):
        alpha = int(150 * (1 - x / 47))
        seam_draw.line(
            [(PANEL_WIDTH + x, 0), (PANEL_WIDTH + x, height)],
            fill=(*INK_DEEP, alpha),
        )
    photo_panel.alpha_composite(seam)
    canvas.alpha_composite(photo_panel)

    panel = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    panel_draw = ImageDraw.Draw(panel)
    panel_draw.rectangle((0, 0, PANEL_WIDTH, height), fill=(*INK, 255))
    panel_draw.rectangle((0, 0, 8, height), fill=(*ACCENT, 255))
    panel_draw.rectangle((64, 88, 120, 92), fill=(*ACCENT, 255))
    canvas.alpha_composite(panel)

    draw = ImageDraw.Draw(canvas)

    eyebrow_font = load_font("inter-semibold", 17)
    name_font = load_font("playfair", 86)
    desc_font = load_font("inter-semibold", 24)
    lead_font = load_font("inter-medium", 28)
    body_font = load_font("inter-medium", 21)
    url_font = load_font("inter-semibold", 22)

    text_x = 64
    draw_tracked_caps(
        draw,
        (text_x, 72),
        "METRO VANCOUVER REAL ESTATE",
        eyebrow_font,
        ACCENT,
    )
    draw.text((text_x, 118), "Kris Kereluk", font=name_font, fill=WHITE)
    draw.text((text_x, 236), "Personal Real Estate Corp", font=desc_font, fill=ACCENT)
    draw.text(
        (text_x, 292),
        "Buying & selling across\nMetro Vancouver",
        font=lead_font,
        fill=WHITE,
        spacing=8,
    )

    for index, line in enumerate(
        wrap_text(
            draw,
            "Vancouver · Burnaby · New Westminster · Coquitlam · Port Moody",
            body_font,
            PANEL_WIDTH - text_x - 48,
        )
    ):
        draw.text((text_x, 392 + index * 30), line, font=body_font, fill=MUTED)

    avatar = ImageOps.fit(avatar_source, (118, 118), method=Image.Resampling.LANCZOS)
    avatar_mask = Image.new("L", avatar.size, 0)
    ImageDraw.Draw(avatar_mask).ellipse((0, 0, 117, 117), fill=255)
    avatar.putalpha(avatar_mask)
    framed = Image.new("RGBA", (134, 134), (0, 0, 0, 0))
    ImageDraw.Draw(framed).ellipse((0, 0, 133, 133), fill=(*ACCENT, 255))
    framed.alpha_composite(avatar, (8, 8))
    canvas.alpha_composite(framed, (text_x, 500))

    draw.text((text_x + 154, 528), "callkris.ca", font=url_font, fill=WHITE)
    draw.text((text_x + 154, 558), "778-288-4481", font=body_font, fill=MUTED)

    canvas.convert("RGB").save(
        os.path.join(BASE, "og-preview.jpg"),
        format="JPEG",
        quality=90,
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
