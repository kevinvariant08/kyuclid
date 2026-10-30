"""Build the Kyuclid logo SVGs in assets/ from the brand fonts.

The wordmark is converted to outlines, so the SVGs render the same everywhere
(an <img> or favicon SVG can't load web fonts). The ∴ in the seal is drawn as
three circles for the same reason.

Usage:
    python tools/brand/build_logos.py path/to/BigShouldersDisplay-900.ttf

Get the font from https://fonts.google.com/specimen/Big+Shoulders+Display.
The Google Fonts repo ships it as a variable font; make a static 900 instance
with fontTools:
    from fontTools.varLib import instancer
    instancer.instantiateVariableFont(TTFont("BigShouldersDisplay[wght].ttf"), {"wght": 900}).save("BSD-900.ttf")

Then re-render the PNG icons and OG images with tools/brand/render_png.py.
"""
import math
import sys
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets"

NAME = "KYUCLID"
TRACKING_EM = 0.06  # matches .wordmark { letter-spacing: .06em } in index.html

# Colours: see docs/brand.md. Light theme first, dark theme second.
SEAL, ON_SEAL = "#B42318", "#FFFFFF"
SEAL_DARK, ON_SEAL_DARK = "#E5534B", "#16070A"
INK, INK_DARK = "#1B1E33", "#E7E9F1"
BG, BG_DARK = "#EEF0F4", "#10121B"
TILT = -4  # degrees, as in .seal { transform: rotate(-4deg) }


def wordmark(font_path, cap_height):
    """Return (path_d, width) for NAME with its caps exactly cap_height tall, top at y=0."""
    font = TTFont(font_path)
    upm = font["head"].unitsPerEm
    caps = font["OS/2"].sCapHeight
    cmap = font.getBestCmap()
    glyphs = font.getGlyphSet()
    s = cap_height / caps
    track = TRACKING_EM * upm

    # First pass: find the ink bounds so the mark starts exactly at x=0.
    x = 0
    bounds = BoundsPen(glyphs)
    for ch in NAME:
        g = glyphs[cmap[ord(ch)]]
        g.draw(TransformPen(bounds, (1, 0, 0, 1, x, 0)))
        x += g.width + track
    xmin, _, xmax, _ = bounds.bounds

    pen = SVGPathPen(glyphs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    x = -xmin
    for ch in NAME:
        g = glyphs[cmap[ord(ch)]]
        # flip y and put the cap line at y=0
        g.draw(TransformPen(pen, (s, 0, 0, -s, x * s, caps * s)))
        x += g.width + track
    return pen.getCommands(), (xmax - xmin) * s


def seal(cx, cy, size, fill, dots, bold=False):
    """The rotated square seal with ∴ drawn as three dots. bold=True is the favicon cut."""
    h = size / 2
    rx = size * (6 / 34)
    if bold:   # bigger dots so ∴ survives at 16–32 px
        r, side, top = 0.10, 0.36, 0.335
    else:      # close to IBM Plex Serif's ∴ at the header's size
        r, side, top = 0.072, 0.29, 0.355
    height = side * math.sqrt(3) / 2
    pts = [(0.5, top), (0.5 - side / 2, top + height), (0.5 + side / 2, top + height)]
    circles = "".join(
        f'<circle cx="{cx - h + px * size:.2f}" cy="{cy - h + py * size:.2f}" r="{r * size:.2f}"/>'
        for px, py in pts
    )
    return (
        f'<g transform="rotate({TILT} {cx:.2f} {cy:.2f})">'
        f'<rect x="{cx - h:.2f}" y="{cy - h:.2f}" width="{size:.2f}" height="{size:.2f}" rx="{rx:.2f}" fill="{fill}"/>'
        f'<g fill="{dots}">{circles}</g></g>'
    )


def tilted_extent(size):
    """Width of the square's bounding box once rotated by TILT."""
    a = math.radians(abs(TILT))
    return size * (math.cos(a) + math.sin(a))


def svg(w, h, body, title, bg=None):
    rect = f'<rect width="{w:g}" height="{h:g}" fill="{bg}"/>' if bg else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:g} {h:g}" '
        f'width="{w:g}" height="{h:g}" role="img" aria-label="{title}">'
        f"<title>{title}</title>{rect}{body}</svg>\n"
    )


def write(name, text):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("wrote", path.relative_to(ROOT))


def main(font_path):
    # Horizontal lockup, in the header's proportions: seal 34 px, caps 20.8 px, gap 10 px.
    cap = 100
    d, wm_w = wordmark(font_path, cap)
    size = cap * 34 / 20.8
    ext = tilted_extent(size)
    pad = (ext - size) / 2 + 2
    gap = cap * 10 / 20.8
    w = pad + size + pad + gap + wm_w + 2
    h = ext + 4
    cy = h / 2
    for suffix, fill, dots, ink in (("", SEAL, ON_SEAL, INK), ("-dark", SEAL_DARK, ON_SEAL_DARK, INK_DARK)):
        body = seal(pad + size / 2, cy, size, fill, dots) + (
            f'<path transform="translate({pad * 2 + size + gap:.2f} {cy - cap / 2:.2f})" fill="{ink}" d="{d}"/>'
        )
        write(f"logo/kyuclid-horizontal{suffix}.svg", svg(round(w, 1), round(h, 1), body, "Kyuclid"))

    # Wordmark alone.
    for suffix, ink in (("", INK), ("-dark", INK_DARK)):
        write(f"logo/kyuclid-wordmark{suffix}.svg",
              svg(round(wm_w + 2, 1), cap + 2, f'<path transform="translate(1 1)" fill="{ink}" d="{d}"/>', "Kyuclid"))

    # Square lockup (avatars, link cards): seal over the wordmark on a solid tile.
    S = 512
    seal_size = 200
    cap_sq = 66
    d_sq, wm_sq = wordmark(font_path, cap_sq)
    gap_sq = 46
    block = tilted_extent(seal_size) + gap_sq + cap_sq
    top = (S - block) / 2
    seal_cy = top + tilted_extent(seal_size) / 2
    wm_top = top + tilted_extent(seal_size) + gap_sq
    for suffix, fill, dots, ink, bg in (
        ("", SEAL, ON_SEAL, INK, BG),
        ("-dark", SEAL_DARK, ON_SEAL_DARK, INK_DARK, BG_DARK),
    ):
        body = seal(S / 2, seal_cy, seal_size, fill, dots) + (
            f'<path transform="translate({(S - wm_sq) / 2:.2f} {wm_top:.2f})" fill="{ink}" d="{d_sq}"/>'
        )
        write(f"logo/kyuclid-square{suffix}.svg", svg(S, S, body, "Kyuclid", bg))

    # The seal on its own (transparent), and the favicon cut with bigger dots.
    write("logo/kyuclid-seal.svg", svg(64, 64, seal(32, 32, 58, SEAL, ON_SEAL), "Kyuclid"))
    write("favicon.svg", svg(64, 64, seal(32, 32, 59, SEAL, ON_SEAL, bold=True), "Kyuclid"))
    # App icon artwork: the seal inside the maskable safe zone on the dark theme's navy.
    write("icons/app-icon.svg", svg(512, 512, seal(256, 256, 280, SEAL, ON_SEAL, bold=True), "Kyuclid", BG_DARK))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
