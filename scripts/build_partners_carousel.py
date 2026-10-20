"""Build profile/partners.svg: a scrolling carousel of partner logos on a white band.

Usage: python scripts/build_partners_carousel.py   (needs Pillow)

The logos are embedded in the SVG as base64: GitHub shows README images in a
sandbox that does not load files linked from inside an SVG.
"""
import base64
import io
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
LOGOS = ROOT / "assets" / "partners"
OUT = ROOT / "profile" / "partners.svg"

# Same order as the "Trusted by leading organizations" section of flai-analytics.com.
PARTNERS = [
    ("toscana-aeroporti.png", "Toscana Aeroporti"),
    ("unibg.png", "Università degli Studi di Bergamo"),
    ("most.png", "MOST – Centro Nazionale per la Mobilità Sostenibile"),
    ("milan-bergamo-airport.png", "Milan Bergamo Airport"),
    ("terravision.png", "Terravision"),
    ("gesac.png", "GESAC – Napoli Salerno Airports"),
    ("oblyk.png", "OBLYK"),
]

WIDTH, HEIGHT = 840, 120
GAP = 72
# Every logo gets about the same area, so wide wordmarks and square marks look balanced.
LOGO_AREA = 9600
MAX_W, MAX_H = 190, 68
# Embedded PNGs are 3x the display size, so they stay sharp on high-density screens.
RASTER_SCALE = 3
SECONDS_PER_LOOP = 35
FADE = 64


def trim(im):
    """Cut the empty border (transparent or white) around the logo."""
    im = im.convert("RGBA")
    white = Image.new("RGBA", im.size, (255, 255, 255, 255))
    flat = Image.alpha_composite(white, im).convert("RGB")
    diff = ImageChops.difference(flat, white.convert("RGB")).convert("L")
    box = diff.point(lambda v: 255 if v > 12 else 0).getbbox()
    return im.crop(box) if box else im


def display_size(w, h):
    ratio = w / h
    dh = min(MAX_H, (LOGO_AREA / ratio) ** 0.5)
    dw = dh * ratio
    if dw > MAX_W:
        dw, dh = MAX_W, MAX_W / ratio
    return round(dw), round(dh)


def data_uri(im, dw, dh):
    scale = min(RASTER_SCALE, im.width / dw)
    im = im.resize((round(dw * scale), round(dh * scale)), Image.LANCZOS)
    # Logos are flat colours: a 64-colour palette keeps them clean and the SVG small.
    im = im.quantize(64, method=Image.Quantize.FASTOCTREE)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def main():
    images = []
    x = GAP / 2
    for filename, name in PARTNERS:
        im = trim(Image.open(LOGOS / filename))
        dw, dh = display_size(*im.size)
        images.append(
            f'<image x="{x:.0f}" y="{(HEIGHT - dh) / 2:.0f}" width="{dw}" height="{dh}" '
            f'href="{data_uri(im, dw, dh)}"><title>{name}</title></image>'
        )
        x += dw + GAP
    strip = round(x - GAP / 2)
    names = ", ".join(name for _, name in PARTNERS)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Partners: {names}">
<title>Partners: {names}</title>
<style>
.track {{ animation: scroll {SECONDS_PER_LOOP}s linear infinite; }}
@keyframes scroll {{ to {{ transform: translateX(-{strip}px); }} }}
@media (prefers-reduced-motion: reduce) {{ .track {{ animation: none; }} }}
</style>
<defs>
<clipPath id="frame"><rect width="{WIDTH}" height="{HEIGHT}" rx="16"/></clipPath>
<linearGradient id="fade-left"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="fade-right"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/></linearGradient>
<g id="strip">
{chr(10).join(images)}
</g>
</defs>
<rect width="{WIDTH}" height="{HEIGHT}" rx="16" fill="#fff"/>
<g clip-path="url(#frame)">
<g class="track"><use href="#strip"/><use href="#strip" x="{strip}"/></g>
<rect width="{FADE}" height="{HEIGHT}" fill="url(#fade-left)"/>
<rect x="{WIDTH - FADE}" width="{FADE}" height="{HEIGHT}" fill="url(#fade-right)"/>
</g>
<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="15.5" fill="none" stroke="#e5e7eb"/>
</svg>
"""
    OUT.write_text(svg, encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(PARTNERS)} logos, {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
