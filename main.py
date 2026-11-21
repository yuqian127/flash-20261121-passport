#!/usr/bin/env python3
"""Draw an invented passport spread for the Free State of Aerthys.

Writes a 1024x1024 PNG to /output/entry.png. Everything is drawn in code
with Pillow; no external assets, no network, no randomness, so re-running
produces the same bytes.
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont

OUT_PATH = "/output/entry.png"
W = H = 1024

# ---------------------------------------------------------------- palette
TEAL_DEEP = (7, 39, 43)        # outer background
TEAL_PAGE = (14, 68, 73)       # page face
TEAL_PANEL = (11, 55, 60)      # inner panel
GOLD = (201, 162, 39)
GOLD_LIGHT = (227, 199, 102)
GOLD_DIM = (138, 115, 32)
CREAM = (242, 234, 216)
WHITE = (255, 255, 255)
INK_NAVY = (18, 38, 46)
MRZ_BG = (248, 246, 239)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load_font(name, size):
    for path in (
        os.path.join(FONT_DIR, name),
        os.path.join("/usr/share/fonts/truetype/liberation", name),
    ):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def serif(size, bold=False):
    return load_font("DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf", size)


def serif_italic(size):
    return load_font("DejaVuSerif-Italic.ttf", size)


def sans(size, bold=False):
    return load_font("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)


def mono(size):
    return load_font("DejaVuSansMono.ttf", size)


def text_w(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def draw_spaced(draw, cx, y, text, font, fill, spacing=2):
    """Draw text centred on cx with extra tracking between letters."""
    widths = [text_w(draw, ch, font) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total // 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + spacing


def draw_centered(draw, cx, y, text, font, fill):
    draw.text((cx - text_w(draw, text, font) // 2, y), text, font=font, fill=fill)


# ---------------------------------------------------------------- helpers
def lighthouse(draw, cx, base_y, s, color, beam=True):
    """A small lighthouse emblem: tower, gallery, lamp room, beams."""
    tw = s * 0.42          # tower half width at base
    th = s * 1.55          # tower height
    top_y = base_y - th
    # beams
    if beam:
        beam_len = s * 1.15
        for sign in (-1, 1):
            x2 = cx + sign * beam_len
            draw.polygon(
                [(cx, top_y + s * 0.10), (x2, top_y - s * 0.28),
                 (x2, top_y + s * 0.48)],
                fill=color + (70,) if len(color) == 3 else color,
            )
    # tower (tapered)
    draw.polygon(
        [(cx - tw, base_y), (cx + tw, base_y),
         (cx - tw * 0.62, top_y), (cx + tw * 0.62, top_y)],
        fill=color,
    )
    # gallery rail
    draw.rectangle([cx - tw * 0.78, top_y - s * 0.10,
                    cx + tw * 0.78, top_y - s * 0.02], fill=color)
    # lamp room
    draw.rectangle([cx - tw * 0.42, top_y - s * 0.42,
                    cx + tw * 0.42, top_y - s * 0.10], fill=color)
    # dome
    draw.pieslice([cx - tw * 0.48, top_y - s * 0.62,
                   cx + tw * 0.48, top_y - s * 0.30],
                  180, 360, fill=color)
    # base rock
    draw.polygon([(cx - tw * 1.15, base_y), (cx + tw * 1.15, base_y),
                  (cx + tw * 0.7, base_y - s * 0.12),
                  (cx - tw * 0.7, base_y - s * 0.12)], fill=color)


def guilloche(draw, box, color, waves=7, amp=5, step=9):
    """Faint wavy security lines across a rectangle."""
    x0, y0, x1, y1 = box
    for k in range(waves):
        yy = y0 + (k + 1) * (y1 - y0) // (waves + 1)
        pts = []
        for x in range(x0, x1 + 1, step):
            pts.append((x, yy + amp * math.sin((x - x0) / 47.0 + k * 1.3)))
        draw.line(pts, fill=color, width=1)


def mrz_check(field):
    """ICAO 7-3-1 check digit."""
    weights = (7, 3, 1)
    total = 0
    for i, ch in enumerate(field):
        if ch == "<":
            v = 0
        elif ch.isdigit():
            v = int(ch)
        else:
            v = ord(ch) - 55  # A=10 .. Z=35
        total += v * weights[i % 3]
    return str(total % 10)


def mrz_lines():
    line1 = "P<AERVOSS<<MARA<SELIN" + "<" * 23
    doc = "AE2026011"
    cd1 = mrz_check(doc)
    dob = "980314"
    cd2 = mrz_check(dob)
    exp = "340212"
    cd3 = mrz_check(exp)
    pers = "<" * 14
    cd4 = mrz_check(pers)
    composite = mrz_check(doc + cd1 + dob + cd2 + exp + cd3 + pers + cd4)
    line2 = doc + cd1 + "AER" + dob + cd2 + "F" + exp + cd3 + pers + cd4 + composite
    assert len(line1) == 44 and len(line2) == 44, (len(line1), len(line2))
    return line1, line2


def make_stamp(lines, ink, w, h, rotate_deg):
    """A rubber stamp on its own layer, slightly rotated."""
    layer = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pad = 30
    d.rectangle([pad, pad, pad + w, pad + h], outline=ink, width=3)
    d.rectangle([pad + 6, pad + 6, pad + w - 6, pad + h - 6],
                outline=ink, width=1)
    f_big = sans(21, bold=True)
    f_small = sans(15, bold=True)
    y = pad + 12
    for i, (txt, big) in enumerate(lines):
        f = f_big if big else f_small
        draw_centered(d, pad + w // 2, y, txt, f, ink)
        y += 30 if big else 24
    return layer.rotate(rotate_deg, resample=Image.BICUBIC, expand=True)


def make_portrait(w, h):
    """Holder portrait: warm sky, lighthouse behind, head-and-shoulders
    silhouette. No real person, no photo."""
    img = Image.new("RGB", (w, h), (232, 200, 106))
    d = ImageDraw.Draw(img)
    # sky gradient: warm gold down to pale sea teal
    for y in range(h):
        t = y / h
        r = int(232 + (127 - 232) * t)
        g = int(200 + (179 - 200) * t)
        b = int(106 + (168 - 106) * t)
        d.line([(0, y), (w, y)], fill=(r, g, b))
    # sea
    d.rectangle([0, int(h * 0.72), w, h], fill=(46, 110, 110))
    d.line([(0, int(h * 0.72)), (w, int(h * 0.72))], fill=(230, 220, 180), width=2)
    # lighthouse at the right, dark silhouette
    lx = int(w * 0.78)
    base = int(h * 0.72)
    s = h * 0.30
    tw = s * 0.16
    d.polygon([(lx - tw, base), (lx + tw, base),
               (lx - tw * 0.6, base - s), (lx + tw * 0.6, base - s)],
              fill=INK_NAVY)
    d.rectangle([lx - tw * 0.7, base - s - 6, lx + tw * 0.7, base - s],
                fill=INK_NAVY)
    d.rectangle([lx - tw * 0.45, base - s - 20, lx + tw * 0.45, base - s - 6],
                fill=INK_NAVY)
    # head-and-shoulders silhouette, facing left
    cx = int(w * 0.42)
    hy = int(h * 0.46)
    d.ellipse([cx - 34, hy - 40, cx + 34, hy + 38], fill=INK_NAVY)
    d.polygon([(cx - 62, h), (cx + 62, h), (cx + 44, hy + 30),
               (cx + 18, hy + 52), (cx - 18, hy + 52), (cx - 44, hy + 30)],
              fill=INK_NAVY)
    # hair bun
    d.ellipse([cx + 8, hy - 52, cx + 40, hy - 22], fill=INK_NAVY)
    return img


# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), TEAL_DEEP)
    draw = ImageDraw.Draw(img, "RGBA")

    # page frames: left data page, right visa page
    pages = [(28, 40, 500, 984), (524, 40, 996, 984)]
    for (x0, y0, x1, y1) in pages:
        draw.rectangle([x0, y0, x1, y1], fill=TEAL_PAGE)
        draw.rectangle([x0 + 8, y0 + 8, x1 - 8, y1 - 8],
                       outline=GOLD, width=2)
        guilloche(draw, (x0 + 14, y0 + 14, x1 - 14, y1 - 14),
                  (227, 199, 102, 16))

    # centre gutter shadow
    for i in range(12):
        a = 26 - i * 2
        draw.line([(512 - i, 40), (512 - i, 984)], fill=(0, 0, 0, a))
        draw.line([(512 + i, 40), (512 + i, 984)], fill=(0, 0, 0, a))

    # ============================================================ LEFT PAGE
    lx0, lx1 = 28, 500
    cx = (lx0 + lx1) // 2

    # header emblem + titles
    lighthouse(draw, cx, 108, 34, GOLD, beam=True)
    draw_spaced(draw, cx, 122, "FREE STATE OF AERTHYS", serif(24, bold=True),
                GOLD_LIGHT, spacing=2)
    draw_spaced(draw, cx, 152, "PASSPORT", serif(16, bold=True), CREAM,
                spacing=6)
    draw.line([(lx0 + 40, 180), (lx1 - 40, 180)], fill=GOLD, width=2)
    draw_centered(draw, lx0 + 56, 192, "DATA PAGE", sans(11, bold=True),
                  GOLD_LIGHT)

    # portrait
    px0, py0, px1, py1 = 56, 216, 206, 406
    portrait = make_portrait(px1 - px0, py1 - py0)
    img.paste(portrait, (px0, py0))
    draw.rectangle([px0, py0, px1, py1], outline=GOLD, width=2)
    draw_centered(draw, (px0 + px1) // 2, py1 + 8, "HOLDER",
                  sans(10, bold=True), GOLD_LIGHT)

    # data fields, right of the portrait
    fields = [
        ("TYPE", "P"),
        ("CODE", "AER"),
        ("PASSPORT No.", "AE-2026-0117"),
        ("SURNAME", "VOSS"),
        ("GIVEN NAMES", "MARA SELIN"),
        ("NATIONALITY", "AERTHYSIAN"),
        ("DATE OF BIRTH", "14 MAR 1998"),
        ("PLACE OF BIRTH", "PORT LUMEN, AERTHYS"),
    ]
    fx, fy = 226, 216
    row_h = 37
    for i, (label, value) in enumerate(fields):
        y = fy + i * row_h
        draw.text((fx, y), label, font=sans(10, bold=True), fill=GOLD_LIGHT)
        draw.text((fx, y + 13), value, font=sans(15, bold=True), fill=WHITE)

    # second row of fields, full width under the portrait
    fy2 = 520
    col2 = [
        ("SEX", "F", 56),
        ("DATE OF ISSUE", "12 FEB 2024", 150),
        ("DATE OF EXPIRY", "12 FEB 2034", 330),
    ]
    for label, value, x in col2:
        draw.text((x, fy2), label, font=sans(10, bold=True), fill=GOLD_LIGHT)
        draw.text((x, fy2 + 13), value, font=sans(15, bold=True), fill=WHITE)
    draw.text((56, fy2 + 52), "AUTHORITY", font=sans(10, bold=True),
              fill=GOLD_LIGHT)
    draw.text((56, fy2 + 65), "MINISTRY OF PASSAGES",
              font=sans(15, bold=True), fill=WHITE)

    # observation: the telling detail of the place
    draw.text((56, fy2 + 108), "OBSERVATIONS", font=sans(10, bold=True),
              fill=GOLD_LIGHT)
    draw.text((56, fy2 + 121),
              "HOLDER IS A CERTIFIED LAMP-KEEPER, GRADE II.",
              font=sans(13, bold=True), fill=CREAM)

    # signature
    draw.text((56, fy2 + 158), "HOLDER'S SIGNATURE", font=sans(10, bold=True),
              fill=GOLD_LIGHT)
    draw.line([(56, fy2 + 196), (300, fy2 + 196)], fill=GOLD, width=1)
    draw.text((58, fy2 + 168), "Mara Selin Voss", font=serif_italic(20),
              fill=CREAM)

    # machine-readable zone
    mz0, my0, mz1, my1 = 40, 796, 492, 936
    draw.rectangle([mz0, my0, mz1, my1], fill=MRZ_BG)
    draw.rectangle([mz0, my0, mz1, my1], outline=GOLD, width=2)
    line1, line2 = mrz_lines()
    f_mrz = mono(15)
    draw.text((mz0 + 12, 814), line1, font=f_mrz, fill=(0, 0, 0))
    draw.text((mz0 + 12, 868), line2, font=f_mrz, fill=(0, 0, 0))
    draw_centered(draw, (mz0 + 484) // 2, 946,
                  "MACHINE-READABLE ZONE", sans(9, bold=True), GOLD_LIGHT)

    # =========================================================== RIGHT PAGE
    rx0, rx1 = 524, 996
    rcx = (rx0 + rx1) // 2

    # faint watermark lighthouse behind the stamps
    wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wm)
    lighthouse(wd, rcx, 580, 150, (227, 199, 102, 22), beam=False)
    img.paste(Image.alpha_composite(img.convert("RGBA"), wm).convert("RGB"),
              (0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    draw_spaced(draw, rcx, 62, "VISAS", serif(22, bold=True), GOLD_LIGHT,
                spacing=4)
    draw_spaced(draw, rcx, 92, "AND ENDORSEMENTS", serif(13, bold=True),
                CREAM, spacing=3)
    draw.line([(rx0 + 40, 122), (rx1 - 40, 122)], fill=GOLD, width=2)

    # visa sticker: the levy that reveals the country
    vx0, vy0, vx1, vy1 = 552, 140, 968, 268
    draw.rectangle([vx0, vy0, vx1, vy1], fill=(245, 238, 214))
    draw.rectangle([vx0, vy0, vx1, vy1], outline=GOLD, width=3)
    draw.rectangle([vx0 + 7, vy0 + 7, vx1 - 7, vy1 - 7], outline=GOLD, width=1)
    lighthouse(draw, vx0 + 62, vy0 + 96, 30, GOLD, beam=False)
    draw.text((vx0 + 108, vy0 + 16), "VISITOR VISA", font=sans(17, bold=True),
              fill=INK_NAVY)
    draw.text((vx0 + 108, vy0 + 40),
              "LIGHTHOUSE LEVY — PAID 40 AUR",
              font=sans(13, bold=True), fill=INK_NAVY)
    draw.text((vx0 + 108, vy0 + 64),
              "CONDITION: BEARER SHALL TEND ONE LAMP.",
              font=sans(12), fill=INK_NAVY)
    draw.text((vx0 + 108, vy0 + 86),
              "VALID FOR ONE LANTERN SEASON.",
              font=sans(12), fill=INK_NAVY)

    # stamps from neighbouring countries, all after the 2024 issue date
    stamps = [
        ([("KESTREL REPUBLIC", True), ("ARRIVAL", False),
          ("03 MAY 2025", False), ("PORT OF TARN", False)],
         (74, 92, 168, 190), 300, 108, -8, 566, 300),
        ([("VOSTRA", True), ("DEPARTURE", False),
          ("18 MAY 2025", False), ("HARBOUR GATE", False)],
         (168, 60, 50, 190), 280, 108, 6, 660, 452),
        ([("ISLE OF ECHOES", True), ("ARRIVAL", False),
          ("09 AUG 2026", False), ("ECHO QUAY", False)],
         (62, 125, 91, 190), 300, 108, -4, 566, 606),
    ]
    for lines, ink, w, h, angle, x, y in stamps:
        stamp = make_stamp(lines, ink, w, h, angle)
        img.paste(stamp, (x, y), stamp)

    # footer note on the right page
    draw_centered(draw, rcx, 760,
                  "THIS SPREAD IS THE PROPERTY OF THE FREE STATE",
                  sans(11, bold=True), GOLD_LIGHT)
    draw_centered(draw, rcx, 782,
                  "OF AERTHYS. IF FOUND, RETURN TO ANY LIGHTHOUSE.",
                  sans(11, bold=True), GOLD_LIGHT)
    draw.line([(rx0 + 40, 812), (rx1 - 40, 812)], fill=GOLD, width=1)
    draw_centered(draw, rcx, 828, "No. AE-2026-0117  •  48 PAGES",
                  sans(12), CREAM)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    img.save(OUT_PATH, format="PNG")
    print("wrote", OUT_PATH, os.path.getsize(OUT_PATH), "bytes")


if __name__ == "__main__":
    build()
