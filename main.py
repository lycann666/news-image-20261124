#!/usr/bin/env python3
"""THE WORLD IN ONE DAY - Tuesday, 24 November 2026.

A dark "night edition" magazine cover summing up the day's world news,
drawn with the Python standard library only (zlib + struct PNG writer,
hand-built 5x7 bitmap font). No network, no randomness, no clock: two
runs write identical bytes to /output/entry.png (falls back to
./out/entry.png locally).

Stories (all reported on 23-24 November 2026, verified from CNN, Reuters,
The Times, WSJ, Le Monde and AP coverage):
  Lead   Nvidia reinstates Jensen Huang as CEO after President Trump
         pressed the board all weekend; shares jump 33%, Nasdaq +6%.
  Second COP31 climate talks collapse in Antalya: final text drops all
         mention of fossil fuels; EU and UK reject the pact.
  Third  Ukraine sea drones sink the Russian corvette Merkury at the
         Benghazi naval base, Libya; MV Angara hit, Ka-27 lost.
  Strip  Indonesia: candy factory fire, 24 dead, 34 still missing.
         Iran warns the US naval blockade may draw a response.
         Vanuatu: magnitude 6.5 quake. Brazil: deadly storm.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
NAVY = (13, 27, 48)
PANEL = (24, 48, 76)
PAPER = (247, 242, 231)
INK = (26, 26, 26)
WHITE = (255, 255, 255)
BLACK = (10, 10, 10)
YELLOW = (232, 178, 44)
GREEN = (118, 185, 0)
GREEN_D = (52, 110, 20)
RED = (200, 40, 40)
BLUE = (31, 58, 110)
SEA = (24, 74, 96)
SKY = (214, 226, 232)
SAND = (216, 198, 162)
GREY = (150, 158, 172)
ORANGE = (204, 92, 18)
LIGHT = (180, 205, 225)

# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 bits ("#" on, "." off). Authored from scratch.
_G = {
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
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".#...", "#...."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".#...", "#...."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#.##."),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
}
_BLANK = (".....",) * 7


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def wrap(text, scale, max_w):
    """Greedy word wrap; returns list of lines fitting max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        for i in range(w * h):
            self.px[3 * i] = bg[0]
            self.px[3 * i + 1] = bg[1]
            self.px[3 * i + 2] = bg[2]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.rect(x - t // 2, y - t // 2, t, t, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            dx = int((r * r - dy * dy) ** 0.5) if r * r - dy * dy >= 0 else 0
            if fill:
                self.rect(cx - dx, yy, 2 * dx + 1, 1, c)
            else:
                self.set(cx - dx, yy, c)
                self.set(cx + dx, yy, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + ry + 1):
            dy = (yy - cy) / ry
            dx = int(rx * (max(0.0, 1 - dy * dy)) ** 0.5)
            self.rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def poly(self, pts, c):
        """Scanline fill of a simple polygon."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.rect(int(xs[k]), y, max(1, int(xs[k + 1]) - int(xs[k])), 1, c)

    def star(self, cx, cy, r_out, r_in, c, points=8):
        import math
        pts = []
        for i in range(points * 2):
            r = r_out if i % 2 == 0 else r_in
            a = 3.141592653589793 * i / points - 3.141592653589793 / 2
            pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
        self.poly(pts, c)

    # ------------------------------------------------------------- text
    def glyph(self, x, y, ch, scale, c):
        rows = _G.get(ch.upper(), _BLANK)
        for r, row in enumerate(rows):
            for col, bit in enumerate(row):
                if bit in ("1", "#"):
                    self.rect(x + col * scale, y + r * scale, scale, scale, c)

    def text(self, x, y, s, scale, c, align="left"):
        w = text_width(s, scale)
        if align == "center":
            x = x - w // 2
        elif align == "right":
            x = x - w
        for i, ch in enumerate(s):
            self.glyph(x + i * 6 * scale, y, ch, scale, c)
        return w

    def para(self, x, y, lines, scale, c, leading=None):
        lh = leading if leading is not None else 9 * scale
        for i, ln in enumerate(lines):
            self.text(x, y + i * lh, ln, scale, c)
        return y + len(lines) * lh

# ------------------------------------------------------------------ drawing
def draw_masthead(cv):
    cv.text(512, 26, "THE WORLD IN ONE DAY", 7, WHITE, align="center")
    cv.rect(28, 92, 968, 34, YELLOW)
    cv.text(44, 100, "TUESDAY, 24 NOVEMBER 2026", 3, INK)
    cv.text(980, 100, "WORLD NEWS", 3, INK, align="right")


def draw_chip(cv, cx, cy, size):
    """Green processor chip with pins and NVDA mark."""
    half = size // 2
    x0, y0 = cx - half, cy - half
    # Pins on all four sides.
    for i in range(7):
        off = 14 + i * ((size - 28) // 6)
        cv.rect(x0 + off, y0 - 14, 10, 14, LIGHT)
        cv.rect(x0 + off, y0 + size, 10, 14, LIGHT)
        cv.rect(x0 - 14, y0 + off, 14, 10, LIGHT)
        cv.rect(x0 + size, y0 + off, 14, 10, LIGHT)
    # Body and inner die.
    cv.rect(x0, y0, size, size, GREEN)
    cv.rect(x0 + 14, y0 + 14, size - 28, size - 28, GREEN_D)
    cv.rect(x0 + 30, y0 + 30, size - 60, size - 60, GREEN)
    cv.text(cx, y0 + size // 2 - 14, "NVDA", 4, WHITE, align="center")
    # Circuit traces running off the chip corners.
    cv.line(x0 - 40, y0 - 40, x0, y0, YELLOW, 3)
    cv.line(x0 + size + 40, y0 - 40, x0 + size, y0, YELLOW, 3)
    cv.line(x0 - 40, y0 + size + 40, x0, y0 + size, YELLOW, 3)
    cv.line(x0 + size + 40, y0 + size + 40, x0 + size, y0 + size, YELLOW, 3)


def draw_hero(cv):
    x0, y0, x1, y1 = 28, 140, 996, 516
    cv.rect(x0, y0, x1 - x0, y1 - y0, PANEL)
    cv.rect(x0, y0, x1 - x0, 5, YELLOW)
    # Left: the chip and the market jump.
    draw_chip(cv, 250, 300, 170)
    cv.text(250, 416, "+33%", 6, YELLOW, align="center")
    cv.text(250, 466, "NVIDIA SHARES", 2, WHITE, align="center")
    # Right: kicker, headline, deck, market line.
    cv.rect(480, 158, 488, 30, GREEN_D)
    cv.text(496, 165, "TECH - SILICON VALLEY", 2, WHITE)
    cv.text(980, 165, "LEAD STORY", 2, WHITE, align="right")
    cv.text(480, 204, "HUANG IS BACK", 6, WHITE)
    cv.text(480, 250, "AT NVIDIA", 6, YELLOW)
    deck = wrap("TRUMP PRESSED THE BOARD ALL WEEKEND. THE BOARD "
                "VOTED TO REINSTATE ITS CEO 11 DAYS AFTER HE QUIT "
                "OVER AN AFFAIR WITH AN ALLEGED CHINESE SPY. "
                "VANCE LED THE PUSH.", 2, 488)
    cv.para(480, 306, deck, 2, PAPER, leading=20)
    cv.hline(480, 436, 488, YELLOW, 2)
    cv.text(480, 452, "NASDAQ +6% - S&P +4% - SHARES +33%", 2, YELLOW)


def draw_cop31(cv):
    x0, y0, x1, y1 = 28, 532, 500, 800
    cv.rect(x0, y0, x1 - x0, y1 - y0, PANEL)
    cv.rect(x0, y0, x1 - x0, 30, RED)
    cv.text(x0 + 16, y0 + 8, "CLIMATE - ANTALYA, TURKEY", 2, WHITE)
    cv.text(x0 + 16, y0 + 44, "COP31 COLLAPSES", 4, WHITE)
    # Cracked-earth disc.
    cx, cy, r = 138, 692, 52
    cv.circle(cx, cy, r, SAND)
    for rr in (r, r - 1):
        for yy in range(cy - rr, cy + rr + 1):
            dy = yy - cy
            dx = int((rr * rr - dy * dy) ** 0.5)
            cv.set(cx - dx, yy, INK)
            cv.set(cx + dx, yy, INK)
    crack = [(cx - 40, cy - 48), (cx - 12, cy - 18), (cx - 28, cy + 8),
             (cx + 4, cy + 30), (cx - 8, cy + 50)]
    for a, b in zip(crack, crack[1:]):
        cv.line(a[0], a[1], b[0], b[1], BLACK, 4)
    crack2 = [(cx + 20, cy - 46), (cx + 34, cy - 16), (cx + 22, cy + 14),
              (cx + 42, cy + 40)]
    for a, b in zip(crack2, crack2[1:]):
        cv.line(a[0], a[1], b[0], b[1], BLACK, 3)
    # NO DEAL stamp.
    cv.rect(88, 748, 100, 30, RED)
    cv.text(138, 756, "NO DEAL", 2, WHITE, align="center")
    # Deck, right of the disc.
    deck = wrap("NO DEAL AFTER TWO WEEKS. THE FINAL TEXT DROPS "
                "FOSSIL FUELS. THE EU AND UK REJECT IT. FIRST "
                "FAILURE SINCE 2009.", 2, 258)
    cv.para(216, 636, deck, 2, PAPER, leading=19)


def draw_ukraine(cv):
    x0, y0, x1, y1 = 524, 532, 996, 800
    cv.rect(x0, y0, x1 - x0, y1 - y0, PANEL)
    cv.rect(x0, y0, x1 - x0, 30, BLUE)
    cv.text(x0 + 16, y0 + 8, "WAR AT SEA - BENGHAZI, LIBYA", 2, WHITE)
    cv.text(x0 + 16, y0 + 44, "WARSHIP SUNK", 4, WHITE)
    # Sea, sinking ship, explosion, sea drones.
    sx0, sy0, sx1, sy1 = x0 + 16, 626, x1 - 16, 706
    cv.rect(sx0, sy0, sx1 - sx0, sy1 - sy0, SKY)
    cv.rect(sx0, sy0 + 44, sx1 - sx0, sy1 - sy0 - 44, SEA)
    cv.hline(sx0, sy0 + 44, sx1 - sx0, WHITE, 2)
    # Ship hull, listing and half-submerged.
    hull = [(sx0 + 90, sy0 + 52), (sx0 + 330, sy0 + 52),
            (sx0 + 310, sy0 + 74), (sx0 + 110, sy0 + 74)]
    cv.poly(hull, BLACK)
    cv.rect(sx0 + 130, sy0 + 30, 120, 22, BLACK)
    cv.rect(sx0 + 260, sy0 + 18, 26, 34, BLACK)
    # Explosion at the bow.
    cv.star(sx0 + 348, sy0 + 34, 26, 11, ORANGE)
    cv.star(sx0 + 348, sy0 + 34, 15, 6, YELLOW)
    # Two sea drones racing in with wakes.
    for dx in (sx0 + 30, sx0 + 70):
        cv.rect(dx, sy0 + 62, 26, 8, WHITE)
        cv.hline(dx - 34, sy0 + 66, 32, WHITE, 2)
    deck = wrap("SEVEN SEA DRONES SANK THE RUSSIAN CORVETTE "
                "MERKURY AND HIT THE MV ANGARA. A KA-27 HELICOPTER "
                "WAS DESTROYED. LIBYA CONDEMNS IT.", 2, 440)
    cv.para(x0 + 16, 716, deck, 2, PAPER, leading=18)


def draw_strip(cv):
    y0, y1 = 816, 976
    cv.text(28, 820, "ALSO TODAY", 3, YELLOW)
    cv.hline(28, 846, 968, YELLOW, 2)
    cells = [
        ("INDONESIA", RED, "24 DEAD",
         "34 STILL MISSING AFTER CANDY FACTORY FIRE"),
        ("IRAN", BLUE, "BLOCKADE",
         "TEHRAN WARNS THE US BLOCKADE MAY DRAW A RESPONSE"),
        ("VANUATU", GREEN_D, "6.5 QUAKE",
         "MAGNITUDE 6.5 QUAKE STRIKES OFF VANUATU"),
        ("BRAZIL", ORANGE, "STORM",
         "DEADLY STORM DISPLACES THOUSANDS"),
    ]
    cw, gap = 236, 8
    for i, (kick, col, value, text) in enumerate(cells):
        x0 = 28 + i * (cw + gap)
        cv.rect(x0, 856, cw, 3, YELLOW)
        cv.rect(x0, 859, cw, 22, col)
        cv.text(x0 + 10, 865, kick, 2, WHITE)
        cv.text(x0 + 10, 890, value, 3, WHITE)
        lines = wrap(text, 2, cw - 20)
        cv.para(x0 + 10, 918, lines[:3], 2, PAPER, leading=18)


def draw_footer(cv):
    cv.hline(28, 986, 968, GREY, 1)
    cv.text(512, 994, "THE WORLD IN ONE DAY - TUESDAY 24 NOVEMBER 2026 - "
            "NEWS AS REPORTED ON THE DAY", 1, GREY, align="center")


# --------------------------------------------------------------------- PNG
def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw.extend(cv.px[y * cv.w * 3:(y + 1) * cv.w * 3])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        c += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    cv = Canvas(W, H, NAVY)
    draw_masthead(cv)
    draw_hero(cv)
    draw_cop31(cv)
    draw_ukraine(cv)
    draw_strip(cv)
    draw_footer(cv)
    out = "/output/entry.png"
    try:
        os.makedirs("/output", exist_ok=True)
        n = write_png(cv, out)
    except OSError:
        os.makedirs("out", exist_ok=True)
        out = os.path.join("out", "entry.png")
        n = write_png(cv, out)
    print("wrote %s (%d bytes, %dx%d)" % (out, n, W, H))


if __name__ == "__main__":
    main()
