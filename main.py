#!/usr/bin/env python3
"""THE WORLD IN ONE DAY -- 24 November 2026, as one magazine cover.

A Python 3.13 standard-library-only program. It draws a 1024x1024 PNG
(a dark "night edition" magazine cover) and writes it to
$MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png).

Stories, as reported on the day:
  * Nvidia reinstates Jensen Huang as CEO after Trump pressed the board
    all weekend; Vance led the push. Shares +33%, Nasdaq +6%, S&P +4%.
  * COP31 in Antalya collapses with no deal after two weeks; the final
    text drops every mention of fossil fuels. First failure since 2009.
  * Ukrainian sea drones sink the Russian corvette Merkury off Benghazi,
    Libya, and hit the cargo ship MV Angara; a Ka-27 helicopter destroyed.
  * Also today: a candy-factory fire in Serang, Indonesia (24 dead,
    34 still missing); Iran warns over a US blockade; a 6.5 quake off
    Vanuatu; a deadly storm in Brazil.

No network, no randomness, no clock: two runs write identical bytes.
"""

import math
import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------- palette
INK_NAVY_TOP = (13, 27, 51)
INK_NAVY_BOTTOM = (9, 19, 36)
PANEL = (26, 50, 84)
PANEL_DARK = (19, 38, 66)
PAPER = (238, 243, 250)
MUTED = (168, 186, 210)
GOLD = (246, 178, 7)
GOLD_DARK = (214, 148, 0)
LEAF = (124, 179, 66)
LEAF_DARK = (56, 120, 44)
LEAF_PALE = (176, 214, 132)
RUBY = (198, 47, 47)
STEEL = (44, 82, 143)
STEEL_PALE = (186, 210, 232)
SEA = (18, 92, 122)
TANGERINE = (232, 116, 28)
SAND = (222, 200, 158)
COAL = (12, 14, 18)
EMBER = (246, 122, 26)
FLAME = (250, 196, 48)


# ------------------------------------------------------- tiny 5x7 bitmap font
# Every glyph is 7 rows of 5 cells. "1" is ink, "0" is empty. Only those
# two characters are ever used, so a symbol can never silently vanish.
GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
}


def glyph_lit_count(ch):
    """How many lit cells a glyph has (used by the self-check)."""
    rows = GLYPHS.get(ch)
    if rows is None:
        return 0
    total = 0
    for row in rows:
        total += row.count("1")
    return total


# ------------------------------------------------------------------- canvas
class Canvas:
    """An RGB pixel buffer with small drawing helpers."""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pixels = bytearray(width * height * 3)

    def put(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            base = (y * self.width + x) * 3
            self.pixels[base] = colour[0]
            self.pixels[base + 1] = colour[1]
            self.pixels[base + 2] = colour[2]

    def fill(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        for yy in range(y0, y1):
            base = (yy * self.width + x0) * 3
            for xx in range(x0, x1):
                off = base + (xx - x0) * 3
                self.pixels[off] = colour[0]
                self.pixels[off + 1] = colour[1]
                self.pixels[off + 2] = colour[2]

    def frame(self, x, y, w, h, colour, thick=2):
        self.fill(x, y, w, thick, colour)
        self.fill(x, y + h - thick, w, thick, colour)
        self.fill(x, y, thick, h, colour)
        self.fill(x + w - thick, y, thick, h, colour)

    def hline(self, x, y, length, colour, thick=1):
        self.fill(x, y, length, thick, colour)

    def vline(self, x, y, length, colour, thick=1):
        self.fill(x, y, thick, length, colour)

    def line(self, x0, y0, x1, y1, colour, thick=1):
        """Bresenham line, thickened by a small square brush."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            half = thick // 2
            self.fill(x - half, y - half, thick, thick, colour)
            if x == x1 and y == y1:
                break
            step = 2 * err
            if step >= dy:
                err += dy
                x += sx
            if step <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, radius, colour):
        for yy in range(cy - radius, cy + radius + 1):
            span = radius * radius - (yy - cy) * (yy - cy)
            if span < 0:
                continue
            half = int(span ** 0.5)
            self.fill(cx - half, yy, half * 2 + 1, 1, colour)

    def ring(self, cx, cy, radius, colour, thick=3):
        for yy in range(cy - radius - thick, cy + radius + thick + 1):
            for xx in range(cx - radius - thick, cx + radius + thick + 1):
                dist = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if radius - thick <= dist <= radius:
                    self.put(xx, yy, colour)

    def triangle(self, p0, p1, p2, colour):
        """Fill a triangle by scanning its rows."""
        pts = sorted((p0, p1, p2), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        if ay == cy:
            return
        for yy in range(ay, cy + 1):
            xs = []
            for (x0, y0), (x1, y1) in (((ax, ay), (bx, by)),
                                       ((bx, by), (cx, cy)),
                                       ((ax, ay), (cx, cy))):
                if y0 == y1:
                    continue
                if min(y0, y1) <= yy <= max(y0, y1):
                    t = (yy - y0) / (y1 - y0)
                    xs.append(int(x0 + t * (x1 - x0)))
            if len(xs) >= 2:
                self.fill(min(xs), yy, max(xs) - min(xs) + 1, 1, colour)


# --------------------------------------------------------------------- text
def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(canvas, x, y, text, scale, colour):
    """Draw one line of upper-case bitmap text at (x, y)."""
    cursor = x
    for ch in text:
        rows = GLYPHS.get(ch)
        if rows is None:
            cursor += 6 * scale
            continue
        for row_i, row in enumerate(rows):
            for col_i, cell in enumerate(row):
                if cell == "1":
                    canvas.fill(cursor + col_i * scale,
                                y + row_i * scale,
                                scale, scale, colour)
        cursor += 6 * scale


def draw_centred(canvas, cx, y, text, scale, colour):
    draw_text(canvas, cx - text_width(text, scale) // 2, y, text, scale, colour)


def draw_right(canvas, right, y, text, scale, colour):
    draw_text(canvas, right - text_width(text, scale), y, text, scale, colour)


def wrap_lines(text, max_width, scale):
    """Greedy word wrap into lines no wider than max_width pixels."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_paragraph(canvas, x, y, text, max_width, scale, colour, leading=4):
    lines = wrap_lines(text, max_width, scale)
    for i, line in enumerate(lines):
        draw_text(canvas, x, y + i * (7 * scale + leading), line, scale, colour)
    return y + len(lines) * (7 * scale + leading)


# ------------------------------------------------------------- scene pieces
def draw_chip(canvas, x, y, size):
    """A green processor chip with pins, for the Nvidia story."""
    pin = 8
    for i in range(6):
        off = 12 + i * (size - 24) // 5
        canvas.fill(x + off, y - pin, 6, pin, STEEL_PALE)
        canvas.fill(x + off, y + size, 6, pin, STEEL_PALE)
        canvas.fill(x - pin, y + off, pin, 6, STEEL_PALE)
        canvas.fill(x + size, y + off, pin, 6, STEEL_PALE)
    canvas.fill(x, y, size, size, LEAF)
    canvas.frame(x, y, size, size, LEAF_DARK, 4)
    inner = size // 4
    canvas.fill(x + inner, y + inner, size - 2 * inner,
                size - 2 * inner, LEAF_DARK)
    canvas.fill(x + inner + 8, y + inner + 8,
                size - 2 * inner - 16, size - 2 * inner - 16, LEAF)
    draw_centred(canvas, x + size // 2, y + size // 2 - 10,
                 "NVDA", 3, PAPER)


def draw_cracked_earth(canvas, cx, cy, radius):
    """A tan globe with a black crack down its middle."""
    canvas.disc(cx, cy, radius, SAND)
    canvas.ring(cx, cy, radius, COAL, 2)
    crack = [(cx - 18, cy - radius + 6), (cx - 4, cy - radius // 2),
             (cx - 16, cy - 6), (cx + 2, cy + radius // 3),
             (cx - 10, cy + radius - 8)]
    for (x0, y0), (x1, y1) in zip(crack, crack[1:]):
        canvas.line(x0, y0, x1, y1, COAL, 4)
    crack2 = [(cx + 22, cy - radius // 2), (cx + 12, cy),
              (cx + 24, cy + radius // 2)]
    for (x0, y0), (x1, y1) in zip(crack2, crack2[1:]):
        canvas.line(x0, y0, x1, y1, COAL, 3)


def draw_burst(canvas, cx, cy, radius):
    """A starburst explosion in orange and yellow."""
    for k in range(12):
        ang = k * 30
        long = radius if k % 2 == 0 else radius // 2
        dx = int(long * math.cos(math.radians(ang)))
        dy = int(long * math.sin(math.radians(ang)))
        canvas.line(cx, cy, cx + dx, cy + dy,
                    EMBER if k % 2 == 0 else FLAME, 5)
    canvas.disc(cx, cy, radius // 3, FLAME)
    canvas.disc(cx, cy, radius // 5, PAPER)


def draw_sinking_ship(canvas, x, y, w, h):
    """A warship low in the water, bow down, beside a burst."""
    canvas.fill(x, y, w, h // 2, STEEL_PALE)
    canvas.fill(x, y + h // 2, w, h // 2, SEA)
    # hull: long dark shape, deeper at the left (sinking bow)
    hull_top = y + h // 2 + 6
    canvas.fill(x + 30, hull_top, w - 90, 26, COAL)
    canvas.triangle((x + 30, hull_top), (x + 30, hull_top + 26),
                    (x + 4, hull_top + 26), COAL)
    canvas.triangle((x + w - 60, hull_top), (x + w - 60, hull_top + 26),
                    (x + w - 34, hull_top + 26), COAL)
    # superstructure and funnel
    canvas.fill(x + 90, hull_top - 22, 110, 22, COAL)
    canvas.fill(x + 230, hull_top - 34, 26, 34, COAL)
    # white wake dashes
    for wx in (x + 8, x + 44, x + 78):
        canvas.fill(wx, hull_top + 34, 24, 4, PAPER)
    draw_burst(canvas, x + w - 52, y + 34, 34)
    # two small sea drones on the water
    for dx in (x + 130, x + 300):
        canvas.fill(dx, y + h - 12, 34, 8, PAPER)
        canvas.fill(dx + 14, y + h - 22, 3, 10, PAPER)


def draw_kicker(canvas, x, y, w, text, colour):
    canvas.fill(x, y, w, 30, colour)
    draw_text(canvas, x + 12, y + 8, text, 2, PAPER)


# ------------------------------------------------------------------ picture
def build_picture():
    canvas = Canvas(WIDTH, HEIGHT)
    # night-sky gradient, top to bottom
    for yy in range(HEIGHT):
        t = yy / (HEIGHT - 1)
        r = int(INK_NAVY_TOP[0] + (INK_NAVY_BOTTOM[0] - INK_NAVY_TOP[0]) * t)
        g = int(INK_NAVY_TOP[1] + (INK_NAVY_BOTTOM[1] - INK_NAVY_TOP[1]) * t)
        b = int(INK_NAVY_TOP[2] + (INK_NAVY_BOTTOM[2] - INK_NAVY_TOP[2]) * t)
        canvas.fill(0, yy, WIDTH, 1, (r, g, b))

    # ---- masthead
    draw_centred(canvas, WIDTH // 2, 20, "THE WORLD IN ONE DAY", 5, PAPER)
    canvas.fill(28, 74, WIDTH - 56, 34, GOLD)
    draw_text(canvas, 44, 82, "TUESDAY, 24 NOVEMBER 2026", 2, INK_NAVY_BOTTOM)
    draw_right(canvas, WIDTH - 44, 82, "WORLD NEWS", 2, INK_NAVY_BOTTOM)
    canvas.hline(28, 116, WIDTH - 56, GOLD, 3)

    # ---- hero: Nvidia lead story
    canvas.fill(28, 126, WIDTH - 56, 300, PANEL)
    canvas.frame(28, 126, WIDTH - 56, 300, GOLD_DARK, 2)
    # chip, left
    canvas.line(96, 150, 150, 204, GOLD, 3)
    canvas.line(372, 150, 318, 204, GOLD, 3)
    canvas.line(96, 402, 150, 348, GOLD, 3)
    canvas.line(372, 402, 318, 348, GOLD, 3)
    draw_chip(canvas, 152, 160, 164)
    draw_centred(canvas, 234, 336, "+33%", 5, GOLD)
    draw_centred(canvas, 234, 380, "NVIDIA SHARES", 2, PAPER)
    # headline + deck, right
    draw_kicker(canvas, 470, 138, 526, "TECH - SILICON VALLEY", LEAF_DARK)
    draw_right(canvas, 984, 146, "LEAD STORY", 2, PAPER)
    draw_text(canvas, 470, 182, "HUANG IS BACK", 5, PAPER)
    draw_text(canvas, 470, 222, "AT NVIDIA", 5, GOLD)
    draw_paragraph(
        canvas, 470, 268,
        "TRUMP PRESSED THE BOARD ALL WEEKEND. THE BOARD VOTED TO "
        "REINSTATE ITS CEO 11 DAYS AFTER HE QUIT OVER AN AFFAIR WITH "
        "AN ALLEGED CHINESE SPY. VANCE LED THE PUSH.",
        514, 2, PAPER, leading=5)
    canvas.hline(470, 388, 514, GOLD, 2)
    draw_text(canvas, 470, 400, "NASDAQ +6% - S&P +4% - SHARES +33%", 2, GOLD)

    # ---- middle left: COP31 collapses
    canvas.fill(28, 442, 468, 296, PANEL)
    canvas.frame(28, 442, 468, 296, PANEL_DARK, 2)
    draw_kicker(canvas, 28, 442, 468, "CLIMATE - ANTALYA, TURKEY", RUBY)
    draw_text(canvas, 44, 484, "COP31 COLLAPSES", 4, PAPER)
    draw_cracked_earth(canvas, 138, 618, 58)
    canvas.fill(84, 688, 108, 30, RUBY)
    draw_centred(canvas, 138, 695, "NO DEAL", 2, PAPER)
    draw_paragraph(
        canvas, 228, 540,
        "NO DEAL AFTER TWO WEEKS. THE FINAL TEXT DROPS FOSSIL FUELS. "
        "THE EU AND UK REJECT IT. FIRST FAILURE SINCE 2009.",
        250, 2, PAPER, leading=5)

    # ---- middle right: warship sunk off Libya
    canvas.fill(528, 442, 468, 296, PANEL)
    canvas.frame(528, 442, 468, 296, PANEL_DARK, 2)
    draw_kicker(canvas, 528, 442, 468, "WAR AT SEA - BENGHAZI, LIBYA", STEEL)
    draw_text(canvas, 544, 484, "WARSHIP SUNK", 4, PAPER)
    draw_sinking_ship(canvas, 544, 526, 436, 108)
    draw_paragraph(
        canvas, 544, 648,
        "SEVEN SEA DRONES SANK THE RUSSIAN CORVETTE MERKURY AND HIT "
        "THE MV ANGARA. A KA-27 HELICOPTER WAS DESTROYED. LIBYA "
        "CONDEMNS IT.",
        436, 2, PAPER, leading=5)

    # ---- also today strip
    draw_text(canvas, 28, 756, "ALSO TODAY", 3, GOLD)
    canvas.hline(28, 782, WIDTH - 56, GOLD, 3)
    cells = [
        ("INDONESIA", RUBY, "24 DEAD",
         "34 STILL MISSING AFTER CANDY FACTORY FIRE"),
        ("IRAN", STEEL, "BLOCKADE",
         "TEHRAN WARNS THE US BLOCKADE MAY DRAW A RESPONSE"),
        ("VANUATU", LEAF_DARK, "6.5 QUAKE",
         "MAGNITUDE 6.5 QUAKE STRIKES OFF VANUATU"),
        ("BRAZIL", TANGERINE, "STORM",
         "DEADLY STORM DISPLACES THOUSANDS"),
    ]
    cell_w = 232
    for i, (place, band, big, small) in enumerate(cells):
        cx = 28 + i * (cell_w + 8)
        if i > 0:
            # thin divider so neighbouring columns never read as one line
            canvas.vline(cx - 5, 794, 136, GOLD_DARK, 2)
        canvas.fill(cx, 794, cell_w, 26, band)
        draw_text(canvas, cx + 10, 801, place, 2, PAPER)
        draw_text(canvas, cx, 830, big, 3, PAPER)
        draw_paragraph(canvas, cx, 862, small, cell_w, 2, PAPER, leading=4)

    # ---- footer
    canvas.hline(28, 942, WIDTH - 56, MUTED, 1)
    draw_centred(canvas, WIDTH // 2, 956,
                 "THE WORLD IN ONE DAY - TUESDAY 24 NOVEMBER 2026 - "
                 "NEWS AS REPORTED ON THE DAY",
                 1, MUTED)
    return canvas


# ------------------------------------------------------------------ png out
def png_chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(canvas, path):
    raw = bytearray()
    row_bytes = canvas.width * 3
    for yy in range(canvas.height):
        raw.append(0)
        start = yy * row_bytes
        raw += canvas.pixels[start:start + row_bytes]
    blob = b"\x89PNG\r\n\x1a\n"
    blob += png_chunk(b"IHDR", struct.pack(">IIBBBBB", canvas.width,
                                           canvas.height, 8, 2, 0, 0, 0))
    blob += png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    blob += png_chunk(b"IEND", b"")
    with open(path, "wb") as handle:
        handle.write(blob)
    return len(blob)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    canvas = build_picture()
    size = write_png(canvas, os.path.join(out_dir, "entry.png"))
    print("wrote entry.png (%d bytes, %dx%d)" % (size, WIDTH, HEIGHT))


if __name__ == "__main__":
    main()
