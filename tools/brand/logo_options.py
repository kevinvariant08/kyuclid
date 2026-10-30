"""Draw the three logo options for Kevin to choose between, as SVGs and PNG sheets in docs/logo-options/.

All three come from Euclid's Elements, Book I, Proposition 1: on a segment AB draw the circle centred A through B and
the circle centred B through A. They cross at C, and ABC is equilateral. Every number below follows from one radius.

Usage:
    python tools/brand/logo_options.py

Needs Chrome or Edge, Pillow, and a network connection for the wordmark's web font. Delete this file and the
docs/logo-options folder once a logo is picked; the winner then moves into tools/brand/build_logos.py.
"""
import math
from pathlib import Path

from render_png import screenshot

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "logo-options"
S3 = math.sqrt(3) / 2

DARK = {"bg": "#0D1322", "ink": "#F1EFE9", "red": "#F2583F", "soft": "#B6BDD0", "tile": "#0A0F1C"}
LIGHT = {"bg": "#F4F3EF", "ink": "#141B33", "red": "#C4301B", "soft": "#424A63", "tile": "#FFFFFF"}


def points(*pts):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)


def construction(r, y):
    """A, B and C for circles of radius r whose centres sit on the line y, centred on x = 50."""
    return (50 - r / 2, y), (50 + r / 2, y), (50, y - r * S3)


def strip(x0, y0, deg, length, width, fill, tip_fill=None, tip=8):
    """A straight band from (x0, y0), deg degrees off straight down, optionally ending in a rank bar."""
    s, c = math.sin(math.radians(deg)), math.cos(math.radians(deg))
    nx, ny = c * width / 2, -s * width / 2
    def quad(a, b):
        return f'<polygon points="{points((a[0] - nx, a[1] - ny), (a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny))}" fill="{{}}"/>'
    end = (x0 + s * length, y0 + c * length)
    out = quad((x0, y0), end).format(fill)
    if tip_fill:
        out += quad((x0 + s * (length - tip), y0 + c * (length - tip)), end).format(tip_fill)
    return out


def proposition(ink, red):
    """The figure as Euclid draws it: two rings and the solid triangle."""
    r, y, w = 27, 50, 7.5
    a, b, c = construction(r, y)
    rings = "".join(f'<circle cx="{p[0]:.2f}" cy="{y}" r="{r}" fill="none" stroke="{ink}" stroke-width="{w}"/>' for p in (a, b))
    return rings + f'<polygon points="{points(a, b, c)}" fill="{red}" stroke="{red}" stroke-width="3" stroke-linejoin="round"/>'


def knot(ink, red):
    """The rings are a belt's two loops. Each tail leaves its loop along the tangent at the crossing, and ends in a rank bar."""
    r, y, w = 24, 40, 7.5
    a, b, c = construction(r, y)
    bottom = y + r * S3
    tails = strip(50, bottom, -60, 36, w, ink, red) + strip(50, bottom, 60, 36, w, ink, red)
    rings = "".join(f'<circle cx="{p[0]:.2f}" cy="{y}" r="{r}" fill="none" stroke="{ink}" stroke-width="{w}"/>' for p in (a, b))
    return tails + rings + f'<polygon points="{points(a, b, c)}" fill="{red}" stroke="{red}" stroke-width="2.5" stroke-linejoin="round"/>'


def vesica(ink, red):
    """Two solid discs with their overlap cut out, and the triangle exactly inscribed in the opening."""
    r, y = 30, 50
    a, b, c = construction(r, y)
    disc = lambda p: f"M{p[0] - r:g} {y}a{r} {r} 0 1 0 {2 * r} 0a{r} {r} 0 1 0 {-2 * r} 0Z"
    return (f'<path fill="{ink}" fill-rule="evenodd" d="{disc(a)}{disc(b)}"/>'
            f'<polygon points="{points(a, b, c)}" fill="{red}"/>')


OPTIONS = [
    ("a", "proposition", "A. Proposition", proposition,
     "Euclid's figure, drawn plainly: two rings and the triangle. The most literal of the three, and the one a mathematician recognises first. The rings get thin at favicon size."),
    ("b", "knot", "B. Knot", knot,
     "The two circles become the loops of a tied belt, and each tail ends in a rank bar. It carries the belt idea on its own. Up close it can also read as glasses and a moustache, and it is the weakest of the three at 16 px."),
    ("c", "vesica", "C. Vesica (recommended)", vesica,
     "Two solid discs with their overlap cut away, and the triangle's corners sitting exactly on the two centres and the crossing point. The strongest silhouette, the clearest at 16 px, and the most unlike anything else on a tab bar."),
]


def mark_svg(fn, theme, size=None):
    dims = f' width="{size}" height="{size}"' if size else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"{dims}>{fn(theme["ink"], theme["red"])}</svg>'


def panel(fn, t):
    return f"""<div class="p" style="background:{t['bg']};color:{t['ink']}">
      <div class="big">{mark_svg(fn, t, 210)}</div>
      <div class="sizes">{mark_svg(fn, t, 64)}{mark_svg(fn, t, 32)}{mark_svg(fn, t, 24)}{mark_svg(fn, t, 16)}</div>
      <div class="lock">{mark_svg(fn, t, 54)}<span>kyuclid</span></div>
    </div>"""


def tile(fn, t):
    return f'<div class="tile" style="background:{t["tile"]}">{mark_svg(fn, t, 104)}</div>'


STYLE = """html,body{margin:0}body{width:1200px;background:#fff;font-family:'IBM Plex Sans',sans-serif;color:#141B33}
.head{padding:26px 36px 18px;display:flex;gap:30px;align-items:baseline;justify-content:space-between}
h1{font:800 34px/1.1 'Bricolage Grotesque',sans-serif;letter-spacing:-.015em;margin:0;white-space:nowrap}
.head p{font-size:16px;line-height:1.45;margin:0;max-width:760px;color:#424A63}
.row{display:grid;grid-template-columns:1fr 1fr 190px}
.p{padding:22px 28px;display:flex;flex-direction:column;align-items:center;gap:16px}
.sizes{display:flex;align-items:center;gap:22px}.lock{display:flex;align-items:center;gap:10px;font:800 42px/1 'Bricolage Grotesque',sans-serif;letter-spacing:-.012em}.lock span{padding-bottom:5px}
.tiles{background:#E7E6DF;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px}
.tile{width:136px;height:136px;border-radius:30px;display:grid;place-items:center}
"""
FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=IBM+Plex+Sans:wght@400&display=block">'


def page(name, fn, note):
    return (f'<!doctype html><meta charset="utf-8">{FONTS}<style>{STYLE}</style>'
            f'<div class="head"><h1>{name}</h1><p>{note}</p></div>'
            f'<div class="row">{panel(fn, DARK)}{panel(fn, LIGHT)}<div class="tiles">{tile(fn, DARK)}{tile(fn, LIGHT)}</div></div>')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sheets = []
    for key, slug, name, fn, note in OPTIONS:
        for theme, suffix in ((LIGHT, ""), (DARK, "-on-dark")):
            (OUT / f"option-{key}-{slug}{suffix}.svg").write_text(mark_svg(fn, theme) + "\n", encoding="utf-8")
        html = OUT / f"_{key}.html"
        html.write_text(page(name, fn, note), encoding="utf-8")
        screenshot(html.as_uri(), OUT / f"option-{key}-{slug}.png", 1200, 560, 5000)
        html.unlink()
        sheets.append(f'<div class="head"><h1>{name}</h1></div><div class="row">{panel(fn, DARK)}{panel(fn, LIGHT)}<div class="tiles">{tile(fn, DARK)}{tile(fn, LIGHT)}</div></div>')
    html = OUT / "_all.html"
    html.write_text(f'<!doctype html><meta charset="utf-8">{FONTS}<style>{STYLE}.head{{padding:14px 36px 10px}}h1{{font-size:24px}}</style>' + "".join(sheets), encoding="utf-8")
    screenshot(html.as_uri(), OUT / "all-three.png", 1200, 1376, 5000)
    html.unlink()


if __name__ == "__main__":
    main()
