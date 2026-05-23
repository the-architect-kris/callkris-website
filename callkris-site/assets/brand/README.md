# Kris Kereluk — Text Wordmark Assets

Primary brand mark: **Kris Kereluk** (Playfair Display, navy) + **Personal Real Estate Corp** (Inter, orange caps).

| Color | Hex | Use |
|---|---|---|
| Navy | `#092352` | Name on light backgrounds |
| Orange | `#e37b48` | Descriptor line |
| White | `#ffffff` | Name on dark backgrounds |

Fonts: [Playfair Display](https://fonts.google.com/specimen/Playfair+Display) 700, [Inter](https://fonts.google.com/specimen/Inter) 600.

---

**Regenerating assets**

```bash
python3 assets/brand/generate-wordmarks.py
```

This downloads the brand fonts and rebuilds all PNG exports from the same proportions used on the live site.

---

## Print (`print/`)

| File | Use when |
|---|---|
| `kris-kereluk-wordmark-light.svg` | **Preferred for print on white paper** — convert text to outlines in Illustrator/Inkscape before final production |
| `kris-kereluk-wordmark-dark.svg` | Print on dark or navy backgrounds |
| `kris-kereluk-wordmark-light-3600w.png` | High-res raster for white/light paper (3600 px wide) |
| `kris-kereluk-wordmark-light-2400w.png` | Standard high-res print |
| `kris-kereluk-wordmark-light-1200w.png` | Proofs and small-format print |
| `kris-kereluk-wordmark-dark-*.png` | Same sizes for dark backgrounds |

**Print tips**
- Give your printer the `.svg` and ask them to outline fonts before output.
- Use the `3600w` PNG if the shop cannot work with SVG.
- Leave clear space around the logo equal to the height of the “Kris” letterforms.

---

## Web / search.callkris.ca (`web/`)

### Option A — HTML + CSS (recommended)

Copy the snippet from `web/wordmark-snippet.html`, or use:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://callkris.ca/assets/brand.css">

<a href="https://callkris.ca/" class="wordmark wordmark--light">
  Kris Kereluk<span>Personal Real Estate Corp</span>
</a>
```

- **`wordmark--light`** — white or light gray header (`#F2F2F2`)
- **`wordmark--dark`** — navy header (`#092352`)

Styles live in `/assets/brand.css` at the site root.

### Option B — PNG fallback

If the search platform only accepts an image:

| File | Use when |
|---|---|
| `kris-kereluk-wordmark-light-512w.png` | Header on light background |
| `kris-kereluk-wordmark-light-256w.png` | Mobile / compact header |
| `kris-kereluk-wordmark-dark-512w.png` | Header on dark background |

Link the image to `https://callkris.ca/`.
