#!/usr/bin/env python3
"""news-image-20261124: draw a 1024x1024 newspaper front page summing
up Tuesday 24 November 2026, and write it to /output/entry.png.

Standard library only, no network, fully deterministic: the same
bytes come out on every run. Run with:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)   # warm newsprint
INK = (20, 20, 20)
RED = (176, 30, 30)
BLUE = (31, 58, 110)
GRAY = (107, 107, 107)
CARD = (255, 255, 255)
RULE = (201, 194, 176)
SKY = (191, 217, 232)
SEA = (46, 107, 138)
LEAF = (62, 122, 62)
DARK = (34, 34, 34)
GREEN = (28, 120, 60)
GOLD = (176, 132, 24)

# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 cells; '1' is on, '0' is off.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
}
BLANK = ("00000", "00000", "00000", "00000", "00000", "00000", "00000")


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def wrap_text(text, max_w, scale):
    """Greedy word wrap. Returns a list of lines, each fitting max_w."""
    cw = 6 * scale
    limit = max(1, max_w // cw)
    lines = []
    for chunk in text.split("\n"):
        words = chunk.split(" ")
        cur = ""
        for w in words:
            trial = w if not cur else cur + " " + w
            if len(trial) <= limit:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = w
                while len(cur) > limit:  # one very long word: hard cut
                    lines.append(cur[:limit])
                    cur = cur[limit:]
        if cur:
            lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def _off(self, x, y):
        return (y * self.w + x) * 3

    def set_px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            o = self._off(x, y)
            self.px[o] = c[0]
            self.px[o + 1] = c[1]
            self.px[o + 2] = c[2]

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            o = self._off(x0, yy)
            self.px[o:o + len(row)] = row

    def border(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set_px(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_tri(self, p0, p1, p2, c):
        xs = sorted([p0[0], p1[0], p2[0]])
        ys = sorted([p0[1], p1[1], p2[1]])
        for yy in range(ys[0], ys[2] + 1):
            row = []
            for a, b in ((p0, p1), (p1, p2), (p2, p0)):
                if a[1] == b[1]:
                    continue
                if min(a[1], b[1]) <= yy <= max(a[1], b[1]):
                    t = (yy - a[1]) / (b[1] - a[1])
                    row.append(a[0] + t * (b[0] - a[0]))
            if len(row) >= 2:
                for xx in range(int(min(row)), int(max(row)) + 1):
                    self.set_px(xx, yy, c)

    def fill_poly(self, pts, c):
        ys = sorted(p[1] for p in pts)
        for yy in range(ys[0], ys[-1] + 1):
            row = []
            n = len(pts)
            for i in range(n):
                a = pts[i]
                b = pts[(i + 1) % n]
                if a[1] == b[1]:
                    continue
                if min(a[1], b[1]) <= yy < max(a[1], b[1]):
                    t = (yy - a[1]) / (b[1] - a[1])
                    row.append(a[0] + t * (b[0] - a[0]))
            row.sort()
            for k in range(0, len(row) - 1, 2):
                for xx in range(int(row[k]), int(row[k + 1]) + 1):
                    self.set_px(xx, yy, c)

    def fill_circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set_px(xx, yy, c)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            g = FONT.get(ch, BLANK)
            for r in range(7):
                row = g[r]
                for col in range(5):
                    if row[col] == '1':
                        self.fill_rect(cx + col * scale, y + r * scale,
                                       scale, scale, c)
            cx += 6 * scale
        return cx

    def text_center(self, y, s, scale, c, cx0=0, cx1=W):
        w = text_width(s, scale)
        self.text(cx0 + (cx1 - cx0 - w) // 2, y, s, scale, c)


# ---------------------------------------------------------------- PNG out
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        o = y * cv.w * 3
        raw += cv.px[o:o + cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    blob = b"\x89PNG\r\n\x1a\n"
    blob += _chunk(b"IHDR", ihdr)
    blob += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    blob += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(blob)
    return len(blob)


# ---------------------------------------------------------------- content
# All facts verified 2026-11-25 against named wires; see
# news-image-20261124-research.md (outside the repo). Every card
# carries one source and one confidence tag. Dates in decks are the
# event dates; cards whose news is a Tuesday follow-up say so.

LEADS = [
    {
        "kicker": "ULLEUNG - 07:52 KST TUE",
        "head": "RUSSIAN JETS AT ULLEUNG",
        "deck": "ABOUT FIVE JETS ENTER KOREA'S AIR-DEFENCE ZONE. "
                "FIRST ALERT OF ITS KIND. F-15KS SCRAMBLE. "
                "ALERT LIFTED IN 3 MIN.",
        "src": "YONHAP",
        "tag": "CONFIRMED",
        "scene": "jets",
    },
    {
        "kicker": "NEW YORK - MARKETS",
        "head": "NVIDIA RALLY FADES",
        "deck": "JENSEN HUANG BACK AS NVIDIA CEO MONDAY. "
                "SHARES -5.9% TUE TO $155.38. DOW JONES TOPS "
                "50,000 AS NASDAQ FALLS.",
        "src": "DOW JONES",
        "tag": "CONFIRMED",
        "scene": "market",
    },
    {
        "kicker": "STRAIT OF HORMUZ",
        "head": "MORE TANKERS HIT MINES",
        "deck": "IRAN'S REV. GUARD SAYS TANKERS CAUGHT FIRE "
                "TUESDAY. QATAR'S PM MEETS US VP VANCE. "
                "US DEBATES HITTING IRAN LEADERS.",
        "src": "GULF NEWS",
        "tag": "CLAIM",
        "scene": "tanker",
    },
]

MEDIUM = [
    ("KOREA'S KOSPI RETAKES 5,000 - UP 6.3%",
     "KOREA'S STOCK INDEX CLOSES AT 5,006.03, FIRST ABOVE 5,000 IN 3 YEARS",
     "MAEIL SHINMUN", "CONFIRMED"),
    ("SANOFI BUYS US BIOTECH INSMED FOR $41B",
     "$175 PER INSMED SHARE. $41B ALL-CASH DEAL.",
     "REUTERS", "CONFIRMED"),
    ("DELL Q3 REVENUE DOUBLES TO $54.9B",
     "AI ORDERS $60.2B IN THE QUARTER, BACKLOG A RECORD $132.3B.",
     "MORNINGSTAR", "CONFIRMED"),
    ("US CONSUMER CONFIDENCE JUMPS TO 103.3",
     "INDEX UP FROM 91.9, BEATING THE 92.2 FORECAST.",
     "CONFERENCE BOARD", "OFFICIAL"),
    ("INDONESIA FACTORY FIRE TOLL RISES TO 26",
     "BANTEN FIRE SAT 21 NOV. DEATH TOLL 26. SEARCH FOR TRAPPED WORKERS GOES ON.",
     "KHAAMA", "REPORTED"),
    ("AFTER CLIMATE TALKS FAIL: WHAT NOW?",
     "COLLAPSED SUN 22 NOV. FIRST NO-DEAL CLIMATE COP SINCE 2009. COP32 NEXT.",
     "REUTERS", "CONFIRMED"),
    ("REAL MADRID BEAT PSV 5-1",
     "MAN CITY 2-2 NAPOLI. ARSENAL 1-1 DORTMUND. CHAMPIONS LEAGUE, MATCHDAY 5.",
     "UEFA", "CONFIRMED"),
    ("THREE ROCKETS, ONE DAY",
     "SOYUZ, ARIANE, FALCON 9 FLY TUESDAY.",
     "NASA SPACEFLIGHT", "CONFIRMED"),
    ("FLORIDA STILL UNDER WATER",
     "ST. JOHNS RIVER STILL HIGH AFTER SAT 21 NOV RECORD. NEARLY 500 RESCUED.",
     "FOX35", "CONFIRMED"),
    ("INDIA CAPTAIN GILL UNDER FIRE FOR EARLY END",
     "DRAW MON 23 NOV. NZ 239 RUNS, 5 OUT. INDIA NEEDED 5 WICKETS IN 15 OVERS.",
     "NDTV", "REPORTED"),
]

ALSO_ON = [
    ["GOLD -2.6% ON MARGIN HIKES (DJ C)",
     "BITCOIN -2.7% TO $59,655 (VOSS R)",
     "ANTHROPIC -12%, BELOW IPO $83 (DSO R)",
     "XIAOMI Q3 PROFIT FALLS 56.8% (DSO R)",
     "BEST BUY BEATS, SAME-STORE +6.1% (DSO R)",
     "US HOME PRICES STEADY IN SEPT (DJ R)",
     "GERMAN BUSINESS MOOD RISES (DJ O)",
     "CANADA: INFLATION PERSISTS (DJ R)"],
    ["CHINA DRUG STOCKS SINK (DSO R)",
     "BLACKROCK HK TOKENISED FUND (DSO R)",
     "CHINA BOND CASH FUNDS HOUSING (DSO R)",
     "TRUMP'S NVIDIA GAIN UP TO $15M (DSO R)",
     "MEGASPEED ON ENTITY LIST (23 NOV) (AR R)",
     "DUTCH MINISTER IN CHINA (DSO R)",
     "AMAZON DRONE CRASH, DETROIT (DSO R)",
     "EU HYBRID CAP: 350K TARIFF-FREE (DSO R)"],
    ["TRUMP PLANS TARIFFS ON CHINA (DJ R)",
     "CHINA PAUSES EXPORT CURBS, JAN (DJ C)",
     "US SUSPECTS IRAN IN SHIP HACKS (NQ R)",
     "PALESTINE-EU ELECTION PANEL (WISE R)",
     "INDIA-NEPAL $1.62B (23 NOV) (NHK C)",
     "DYMER TOLL 12 (STRIKE 22 NOV) (UP C)",
     "BRAZIL STORM 5 DEAD, 19.8K FLED (IOM C)",
     "DR CONGO: 447,000+ DISPLACED (OCHA O)"],
    ["MALI ATTACK KILLS 1 (21 NOV) (MSF C)",
     "FED WILLIAMS: INFLATION TOO HIGH (NQ R)",
     "FRANCE RARE-EARTH STOCKPILE (DSO R)",
     "FRANCE PMI AT 6-MONTH LOW (DSO R)",
     "OIL REBOUNDS ON SHIPPING RISKS (DJ R)",
     "VENEZUELA PUBLISHES $237.5B DEBT (DJ R)",
     "ARMY TO DETONATE 68 BARRELS (RTRS R)",
     "B'DESH GARMENT 15% WAGE RISE (RTRS R)"],
]

DATE_CHECK_2 = ("SOUTH AFRICA JOBS (10 NOV) - BEPICOLOMBO MERCURY "
                "(21 NOV) - NASA NEON DEAL (23 NOV)")

# Footer: line 1 decodes the ALSO ON source codes, line 2 the tags
# (C CONFIRMED, R REPORTED, CL CLAIM, O OFFICIAL),
# the lead source, and the Ulleung time in both zones.
FOOTER_LINES = [
    "SOURCES: RTRS REUTERS, DJ DOW JONES, DSO SUMMARY, AR ARGUS, "
    "UP UKR. PRAVDA, NQ NEWSQUAWK, VOSS REPORT, WISE WISEVOTER, "
    "NHK JAPAN, IOM MIGRATION, OCHA UN, MSF DOCTORS",
    "TAGS: C CONFIRMED, R REPORTED, CL CLAIM, O OFFICIAL - "
    "LEAD SOURCE: CENSUS STUDIO (YOUTUBE) - ULLEUNG ALERT 22:52 UTC "
    "23 NOV = 07:52 KST 24 NOV (KST IS KOREA TIME)",
]

TIMELINE = [
    ("00:56", "DRONE CRASH", 0),
    ("05:05", "HORMUZ CLAIM", 1),
    ("09:59", "SANOFI", 0),
    ("16:03", "US CONFIDENCE", 1),
    ("21:14", "DELL RESULTS", 0),
]

# (lon, lat, label, label dx, label dy) — dots on the world map.
MAP_DOTS = [
    (-120.6, 34.6, "VANDENBERG", 6, -3),
    (-81.0, 28.0, "FLORIDA", -6, 8),
    (-74.0, 40.7, "NEW YORK", -12, -10),
    (-52.8, 5.2, "KOUROU", -10, 8),
    (-53.8, -29.0, "BRAZIL", -8, 8),
    (-3.7, 40.4, "MADRID", -8, -10),
    (2.3, 48.9, "PARIS", -4, 8),
    (28.5, -2.5, "SOUTH KIVU", -6, 8),
    (56.5, 26.5, "HORMUZ", -10, -10),
    (63.3, 45.6, "BAIKONUR", -14, 8),
    (77.2, 28.6, "DELHI", 2, -10),
    (106.0, -6.2, "BANTEN", -8, 8),
    (130.9, 37.5, "ULLEUNG", 4, -10),
    (174.8, -41.3, "WELLINGTON", -56, -10),
]

CONTINENTS = [
    [(-168, 65), (-140, 70), (-120, 72), (-100, 73), (-85, 70),
     (-75, 62), (-60, 50), (-65, 44), (-75, 35), (-80, 25),
     (-90, 20), (-100, 18), (-110, 25), (-125, 35), (-125, 49),
     (-145, 60), (-160, 58)],
    [(-80, 10), (-75, 5), (-60, -5), (-50, -10), (-40, -20),
     (-48, -28), (-58, -35), (-70, -40), (-73, -50), (-70, -55),
     (-75, -40), (-80, -20), (-80, -5)],
    [(-10, 36), (-5, 43), (0, 50), (5, 55), (10, 58), (20, 60),
     (25, 65), (30, 70), (35, 68), (40, 60), (30, 55), (25, 50),
     (20, 45), (12, 44), (5, 43), (-2, 37)],
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31),
     (35, 28), (40, 20), (48, 11), (51, 10), (45, 0), (40, -10),
     (35, -20), (30, -30), (20, -35), (15, -30), (12, -18), (9, -5),
     (8, 4), (-8, 5)],
    [(40, 70), (60, 72), (80, 73), (100, 76), (120, 73), (140, 72),
     (160, 70), (178, 66), (170, 60), (160, 55), (150, 60),
     (140, 50), (135, 43), (127, 40), (120, 35), (110, 25),
     (105, 15), (100, 8), (95, 15), (90, 22), (80, 25), (75, 20),
     (70, 25), (60, 25), (50, 30), (45, 35), (40, 40)],
    [(113, -22), (122, -15), (132, -12), (142, -11), (150, -20),
     (153, -28), (150, -37), (140, -38), (130, -32), (122, -34),
     (115, -35), (113, -26)],
    [(166, -34), (170, -38), (174, -41), (176, -38), (173, -35),
     (168, -34)],
]

# Sea gaps drawn over the continents (CARD white) so the landmasses
# read as separate continents at this size: Mediterranean, Red Sea,
# Panama isthmus, Urals. Each is (lon0, lon1, lat0, lat1).
SEA_GAPS = [
    (-6, 36, 34, 38),
    (38, 43, 12, 28),
    (-83, -77, 6, 12),
    (40, 46, 52, 70),
]

# ---------------------------------------------------------------- scenes
def scene_jets(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, SKY)
    cv.fill_rect(x, y + h - 12, w, 12, SEA)
    # island
    cv.fill_tri((x + 120, y + h - 12), (x + 150, y + h - 28),
                (x + 180, y + h - 12), LEAF)
    cv.fill_tri((x + 150, y + h - 28), (x + 157, y + h - 32),
                (x + 164, y + h - 28), LEAF)
    cv.text(x + 100, y + 2, "KADIZ", 1, INK)
    # two jets: larger swept triangles with contrails
    for jx, jy in ((x + 30, y + 8), (x + 190, y + 4)):
        cv.fill_tri((jx, jy), (jx + 34, jy + 6), (jx, jy + 12), DARK)
        cv.line(jx - 28, jy + 6, jx - 2, jy + 6, CARD)
    # red alert mark, captioned on the sea
    cv.fill_circle(x + w - 26, y + 18, 9, RED)
    cv.text(x + w - 29, y + 11, "!", 1, CARD)
    cv.text(x + 6, y + h - 10, "ALERT", 1, CARD)


def scene_market(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, CARD)
    base = y + h - 6
    cv.fill_rect(x, base, w, 2, RULE)
    cv.text(x + 8, y + 2, "MON", 1, GREEN)
    cv.text(x + 150, y + 2, "TUE", 1, RED)
    bars = [(26, 20, GREEN), (66, 15, GREEN), (106, 12, RED),
            (146, 10, RED), (186, 13, RED), (226, 8, RED)]
    for bx, bh, bc in bars:
        cv.fill_rect(x + bx, base - bh, 24, bh, bc)
    cv.fill_tri((x + 258, y + 6), (x + 274, y + 6), (x + 266, y + 16), RED)
    cv.fill_rect(x + 263, y + 14, 6, 12, RED)


def scene_tanker(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, SKY)
    cv.fill_rect(x, y + h - 14, w, 14, SEA)
    for wx in range(x + 4, x + w - 20, 18):
        cv.line(wx, y + h - 10, wx + 8, y + h - 6, CARD)
        cv.line(wx + 8, y + h - 6, wx + 16, y + h - 10, CARD)
    # hull and containers, with flame over the middle container
    cv.fill_rect(x + 60, y + 20, 170, 8, DARK)
    cv.fill_rect(x + 76, y + 10, 26, 10, RED)
    cv.fill_rect(x + 106, y + 10, 26, 10, BLUE)
    cv.fill_rect(x + 136, y + 10, 26, 10, GOLD)
    cv.fill_rect(x + 216, y + 8, 8, 12, DARK)
    cv.fill_tri((x + 112, y + 10), (x + 119, y + 1), (x + 126, y + 10), RED)
    cv.fill_tri((x + 116, y + 10), (x + 119, y + 4), (x + 122, y + 10),
                GOLD)
    # two spiked mines
    for mx, my in ((x + 30, y + h - 7), (x + 262, y + h - 7)):
        cv.fill_circle(mx, my, 3, DARK)
        for dx, dy in ((-6, 0), (6, 0), (0, -6), (0, 6),
                       (-4, -4), (4, -4), (-4, 4), (4, 4)):
            cv.line(mx, my, mx + dx, my + dy, DARK)


SCENES = {"jets": scene_jets, "market": scene_market, "tanker": scene_tanker}

# ---------------------------------------------------------------- cards
MX = 16
CW = 992


def draw_lead(cv, x, y, w, h, card):
    cv.fill_rect(x, y, w, h, CARD)
    cv.border(x, y, w, h, INK, 2)
    cv.fill_rect(x, y, w, 5, RED)
    SCENES[card["scene"]](cv, x + 10, y + 6, w - 20, 32)
    ty = y + 42
    cv.text(x + 10, ty, card["kicker"], 2, RED)
    ty += 16
    lines = wrap_text(card["head"], w - 20, 3)
    for ln in lines[:2]:
        cv.text(x + 10, ty, ln, 3, INK)
        ty += 24
    dlines = wrap_text(card["deck"], w - 20, 2)
    for ln in dlines[:5]:
        cv.text(x + 10, ty, ln, 2, INK)
        ty += 16
    cv.text(x + 10, y + h - 16, card["src"], 2, BLUE)
    tag = card["tag"]
    cv.text(x + w - 10 - text_width(tag, 2), y + h - 16, tag, 2, RED)


def draw_medium(cv, x, y, w, h, head, deck, src, tag):
    cv.fill_rect(x, y, w, h, CARD)
    cv.border(x, y, w, h, RULE, 1)
    cv.fill_rect(x, y, 4, h, BLUE)
    hx = x + 12
    lines = wrap_text(head, w - 24, 3)
    # One-line heads sit lower so the head+deck block stays centred
    # instead of leaving a dead band under the head (egm-review r2).
    hy = y + 4 if len(lines) >= 2 else y + 16
    ty = hy
    for ln in lines[:2]:
        cv.text(hx, ty, ln, 3, INK)
        ty += 24
    dlines = wrap_text(deck, w - 24, 1)
    ty = hy + 24 * len(lines)
    for ln in dlines[:2]:
        cv.text(hx, ty, ln, 1, INK)
        ty += 10
    cv.text(hx, y + h - 15, src, 2, BLUE)
    cv.text(x + w - 12 - text_width(tag, 2), y + h - 15, tag, 2, RED)


# ---------------------------------------------------------------- page
def draw_masthead(cv):
    cv.fill_rect(MX, 6, CW, 4, RED)
    cv.text_center(16, "THE WORLD IN ONE DAY", 3, INK)
    cv.text_center(46, "TUESDAY 24 NOVEMBER 2026", 5, RED)
    cv.text_center(88, "45 STORIES - 9 REGIONS - 12 FIELDS", 2, BLUE)
    cv.fill_rect(MX, 102, CW, 2, INK)
    cv.fill_rect(MX, 106, CW, 1, INK)


def draw_date_check(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, CARD)
    cv.border(x, y, w, h, RED, 2)
    cv.fill_rect(x, y, 6, h, RED)
    cv.text(x + 14, y + 4, "DATE CHECK - LEFT OUT AS OLDER NEWS:", 2, RED)
    cv.text(x + 14, y + 20, DATE_CHECK_2, 1, INK)


def draw_also_on(cv, x, y, w):
    cv.text(x, y, "ALSO ON", 2, INK)
    note = "SOURCE + TAG IN ( ) - SEE FOOTER"
    cv.text(x + w - text_width(note, 1), y + 3, note, 1, INK)
    cv.fill_rect(x + text_width("ALSO ON", 2) + 8, y + 6,
                 w - text_width("ALSO ON", 2) - 8 - text_width(note, 1) - 16,
                 2, INK)
    col_w = (w - 3 * 8) // 4
    for ci, col in enumerate(ALSO_ON):
        cx = x + ci * (col_w + 8)
        for ri, item in enumerate(col):
            cv.text(cx, y + 20 + ri * 12, item, 1, INK)


def map_label(cv, x, y, s, x0, y0, x1, y1):
    """Label with a white backing, clamped inside the map box."""
    w = text_width(s, 1)
    x = max(x0 + 2, min(x, x1 - 2 - w))
    y = max(y0 + 2, min(y, y1 - 2 - 7))
    cv.fill_rect(x - 1, y - 1, w + 2, 9, CARD)
    cv.text(x, y, s, 1, INK)


def draw_map(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, CARD)
    cv.border(x, y, w, h, RULE, 1)
    cv.text(x + 8, y + 4, "WHERE IT HAPPENED", 2, INK)
    mx, my, mw, mh = x + 6, y + 20, w - 12, h - 26
    for poly in CONTINENTS:
        pts = []
        for lon, lat in poly:
            lat = max(-45.0, min(75.0, lat))
            px = mx + (lon + 180.0) / 360.0 * mw
            py = my + (75.0 - lat) / 120.0 * mh
            pts.append((int(px), int(py)))
        cv.fill_poly(pts, BLUE)
    for lon0, lon1, lat0, lat1 in SEA_GAPS:
        gx0 = mx + (lon0 + 180.0) / 360.0 * mw
        gx1 = mx + (lon1 + 180.0) / 360.0 * mw
        gy0 = my + (75.0 - lat1) / 120.0 * mh
        gy1 = my + (75.0 - lat0) / 120.0 * mh
        cv.fill_rect(int(gx0), int(gy0), max(1, int(gx1 - gx0)),
                     max(1, int(gy1 - gy0)), CARD)
    for lon, lat, label, dx, dy in MAP_DOTS:
        px = mx + (lon + 180.0) / 360.0 * mw
        py = my + (75.0 - lat) / 120.0 * mh
        cv.fill_circle(int(px), int(py), 3, RED)
        cv.fill_circle(int(px), int(py), 1, CARD)
        if label:
            map_label(cv, int(px) + dx, int(py) + dy, label,
                      x, y, x + w, y + h)


def draw_timeline(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, CARD)
    cv.border(x, y, w, h, RULE, 1)
    cv.text(x + 8, y + 4, "UTC: WHEN STORIES BROKE", 2, INK)
    ax0 = x + 14
    ax1 = x + w - 14
    ay = y + 44
    for hr in (0, 6, 12, 18, 24):
        tx = ax0 + (ax1 - ax0) * hr // 24
        lab = "%02d:00" % hr
        lx = tx - text_width(lab, 1) // 2
        lx = max(x + 4, min(lx, x + w - 4 - text_width(lab, 1)))
        cv.text(lx, y + 32, lab, 1, INK)
    cv.fill_rect(ax0, ay, ax1 - ax0, 2, INK)
    for hr in (0, 6, 12, 18, 24):
        tx = ax0 + (ax1 - ax0) * hr // 24
        cv.fill_rect(tx, ay - 3, 2, 8, INK)
    for hhmm, lab, row in TIMELINE:
        hh, mm = int(hhmm[:2]), int(hhmm[3:])
        frac = (hh * 60 + mm) / (24 * 60)
        ex = ax0 + int((ax1 - ax0) * frac)
        cv.fill_circle(ex, ay, 4, RED)
        full = hhmm + " " + lab
        lx = ex - text_width(full, 1) // 2
        lx = max(x + 4, min(lx, x + w - 4 - text_width(full, 1)))
        ly = ay + 8 if row == 0 else ay + 17
        cv.text(lx, ly, full, 1, INK)


def draw_footer(cv, y):
    for i, line in enumerate(FOOTER_LINES):
        cv.text_center(y + i * 9, line, 1, INK)


def check_layout():
    """Fail loudly instead of silently truncating text (egm-review r1).
    Call before drawing; every wrapped block must fit its line budget
    and no timeline labels on the same row may overlap.
    Single-word second lines in HEADS are accepted display-head
    convention (L1 .../ULLEUNG, M7 .../LEAGUE); only deck orphans
    are asserted, because a deck orphan drops a fact."""
    for card in LEADS:
        assert text_width(card["kicker"], 2) <= 322 - 20, (
            "lead kicker too wide: %r" % card["kicker"])
        hl = wrap_text(card["head"], 322 - 20, 3)
        assert len(hl) <= 2, "lead head wraps past 2 lines: %r" % card["head"]
        dl = wrap_text(card["deck"], 322 - 20, 2)
        assert len(dl) <= 5, "lead deck wraps past 5 lines: %r" % card["deck"]
        assert len(dl[-1].split()) > 1, "lead deck orphan last line: %r" % dl[-1]
    assert text_width("THE WORLD IN ONE DAY", 3) <= CW
    assert text_width("TUESDAY 24 NOVEMBER 2026", 5) <= CW
    assert text_width("45 STORIES - 9 REGIONS - 12 FIELDS", 2) <= CW
    assert text_width("DATE CHECK - LEFT OUT AS OLDER NEWS:", 2) <= CW - 28
    for head, deck, src, tag in MEDIUM:
        hl = wrap_text(head, 490 - 24, 3)
        assert len(hl) <= 2, "medium head wraps past 2 lines: %r" % head
        dl = wrap_text(deck, 490 - 24, 1)
        assert len(dl) <= 2, "medium deck wraps past 2 lines: %r" % deck
        assert len(dl[-1].split()) > 1, "medium deck orphan last line: %r" % dl[-1]
        # Deck must end above the src/tag row (card h82, src at +67).
        hy = 4 if len(hl) >= 2 else 16
        deck_end = hy + 24 * len(hl) + 10 * len(dl)
        assert deck_end <= 67, "medium deck runs into src/tag row: %r" % deck
    for col in ALSO_ON:
        for item in col:
            assert len(item) <= 40, "ALSO ON line too long (%d): %r" % (
                len(item), item)
    assert len(DATE_CHECK_2) <= 160, "DATE CHECK line 2 too long"
    for line in FOOTER_LINES:
        assert len(line) <= 165, "footer line too long (%d): %r" % (
            len(line), line)
    x, w = 640, 368
    ax0, ax1 = x + 14, x + w - 14
    rows = {0: [], 1: []}
    for hhmm, lab, row in TIMELINE:
        hh, mm = int(hhmm[:2]), int(hhmm[3:])
        frac = (hh * 60 + mm) / (24 * 60)
        ex = ax0 + int((ax1 - ax0) * frac)
        full = hhmm + " " + lab
        lx = ex - text_width(full, 1) // 2
        lx = max(x + 4, min(lx, x + w - 4 - text_width(full, 1)))
        rows[row].append((lx, lx + text_width(full, 1), full))
    for row, items in rows.items():
        items.sort()
        prev = -1
        for lx, rx, full in items:
            assert lx >= prev, "timeline row %d labels overlap: %r" % (
                row, full)
            prev = max(prev, rx)
    # Map labels (post-clamp) must sit inside the box and not overlap.
    mx, my, mw, mh = 16 + 6, 912 + 20, 612 - 12, 84 - 26
    rects = []
    for lon, lat, label, dx, dy in MAP_DOTS:
        if not label:
            continue
        px = mx + (lon + 180.0) / 360.0 * mw
        py = my + (75.0 - lat) / 120.0 * mh
        lw = text_width(label, 1)
        lx = max(16 + 2, min(int(px) + dx, 16 + 612 - 2 - lw))
        ly = max(912 + 2, min(int(py) + dy, 912 + 84 - 2 - 7))
        rects.append((lx - 1, ly - 1, lx + lw + 1, ly + 8, label))
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            a, b = rects[i], rects[j]
            overlap = a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]
            assert not overlap, "map labels overlap: %r vs %r" % (a[4], b[4])


def build():
    check_layout()
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    # lead row: 3 cards
    lx = [MX, 351, 686]
    for i, card in enumerate(LEADS):
        draw_lead(cv, lx[i], 112, 322, 200, card)
    # medium grid: 2 columns x 5 rows
    for i, (head, deck, src, tag) in enumerate(MEDIUM):
        col = i % 2
        row = i // 2
        x = MX + col * 502
        y = 320 + row * 86
        draw_medium(cv, x, y, 490, 82, head, deck, src, tag)
    # date check, also on, map + timeline, footer
    draw_date_check(cv, MX, 754, CW, 32)
    draw_also_on(cv, MX, 794, CW)
    draw_map(cv, MX, 912, 612, 84)
    draw_timeline(cv, 640, 912, 368, 84)
    draw_footer(cv, 1000)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    cv = build()
    n = write_png(path, cv)
    print("wrote %s (%d bytes, %dx%d)" % (path, n, W, H))


if __name__ == "__main__":
    main()
