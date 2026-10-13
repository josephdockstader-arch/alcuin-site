#!/usr/bin/env python3
"""WCAG contrast checker for the Alcuin site tokens.

Run after any token change: python3 tools/contrast_check.py
Exits 1 if any declared pair fails its threshold (4.5:1 text, 3:1 UI).
Also solves for candidate values when run with --solve.
"""
import sys

def lum(hexcolor):
    hexcolor = hexcolor.lstrip('#')
    r, g, b = (int(hexcolor[i:i+2], 16) / 255 for i in (0, 2, 4))
    def f(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def ratio(fg, bg):
    l1, l2 = sorted((lum(fg), lum(bg)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)

def composite(fg_hex, alpha, bg_hex):
    fg = [int(fg_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
    bg = [int(bg_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
    out = [round(f * alpha + b * (1 - alpha)) for f, b in zip(fg, bg)]
    return '#%02x%02x%02x' % tuple(out)

# ---- current tokens (keep in sync with build_redesign.py :root) ----
TEAL = '#17313b'; TEAL_DEEP = '#10242c'
EMBER = '#e8501e'; EMBER_STRONG = '#c23c10'; EMBER_DARK = '#a8360c'
CREAM = '#f6f1e5'; PAPER = '#fbf8f1'; SEAFOAM = '#a9c3c0'
INK = '#1d2a30'; INK_SOFT = '#44565e'; WHITE = '#ffffff'
ERROR = '#a3341c'
LINE_STRONG_ALPHA = 0.55  # rgba(23,49,59,.55)

PAIRS = [
    # (label, fg, bg, threshold)
    ('body ink on cream', INK, CREAM, 4.5),
    ('ink on paper', INK, PAPER, 4.5),
    ('ink on white', INK, WHITE, 4.5),
    ('ink-soft on cream', INK_SOFT, CREAM, 4.5),
    ('ink-soft on paper', INK_SOFT, PAPER, 4.5),
    ('ink-soft on white (placeholder)', INK_SOFT, WHITE, 4.5),
    ('ember-strong text on cream', EMBER_STRONG, CREAM, 4.5),
    ('ember-strong text on paper', EMBER_STRONG, PAPER, 4.5),
    ('ember-strong text on white', EMBER_STRONG, WHITE, 4.5),
    ('white label on ember-strong (btn)', WHITE, EMBER_STRONG, 4.5),
    ('white label on ember-dark (btn hover)', WHITE, EMBER_DARK, 4.5),
    ('cream on teal (hero text)', CREAM, TEAL, 4.5),
    ('seafoam on teal (kicker on dark)', SEAFOAM, TEAL, 4.5),
    ('seafoam on teal-deep', SEAFOAM, TEAL_DEEP, 4.5),
    ('error red on white', ERROR, WHITE, 4.5),
    ('error red on paper', ERROR, PAPER, 4.5),
    ('line-strong border vs white field', composite(TEAL, LINE_STRONG_ALPHA, WHITE), WHITE, 3.0),
    ('line-strong border vs cream page', composite(TEAL, LINE_STRONG_ALPHA, CREAM), CREAM, 3.0),
    ('line-strong border vs paper page', composite(TEAL, LINE_STRONG_ALPHA, PAPER), PAPER, 3.0),
]

def main():
    if '--solve' in sys.argv:
        print('candidate rust values (need >=4.5 on cream AND white-label >=4.5):')
        for hexv in ('#cf4315', '#c23c10', '#b83c0e', '#b0380d', '#a8360c', '#96300a'):
            print(f'  {hexv}: on cream {ratio(hexv, CREAM):.2f}, on paper '
                  f'{ratio(hexv, PAPER):.2f}, on white {ratio(hexv, WHITE):.2f}, '
                  f'white-on-it {ratio(WHITE, hexv):.2f}')
        print('line-strong alpha sweep (border vs white field, need >=3):')
        for a in (0.35, 0.45, 0.5, 0.55, 0.6):
            c = composite(TEAL, a, WHITE)
            print(f'  alpha {a}: {c} vs white {ratio(c, WHITE):.2f}, '
                  f'vs cream {ratio(composite(TEAL, a, CREAM), CREAM):.2f}')
        return 0
    failed = 0
    for label, fg, bg, need in PAIRS:
        r = ratio(fg, bg)
        mark = 'ok  ' if r >= need else 'FAIL'
        if r < need:
            failed += 1
        print(f'{mark} {r:5.2f} (need {need}) {label}')
    print(f'\n{len(PAIRS) - failed}/{len(PAIRS)} pass')
    return 1 if failed else 0

if __name__ == '__main__':
    sys.exit(main())
