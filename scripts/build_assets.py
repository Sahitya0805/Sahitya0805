#!/usr/bin/env python3
"""
sahitya0805 / profile renderer
------------------------------
Quiet dark canvas, a spectrum of accents, a lot going on underneath.
Every graphic on the README is hand-built, animated SVG.

  python scripts/build_assets.py                    static pieces
  GITHUB_TOKEN=... python scripts/build_assets.py   + live stats, rhythm, projects

Drawn at 830px wide (GitHub's README column) so nothing gets shrunk.
Edit the CONTENT section below to change any wording.
"""
import datetime as dt
import html
import json
import math
import os
import random
import re
import sys
import urllib.request

USER = os.environ.get("GH_USER", "Sahitya0805")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
README = os.path.join(ROOT, "README.md")
W = 830

SANS = "Inter,'Segoe UI',-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','SF Mono',SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

BG = "#0a0a0a"
CARD = "#0c0c0c"
HAIR = "#1f1f1f"
HAIR2 = "#2a2a2a"
WHITE = "#ededed"
GREY = "#8f8f8f"
DARK = "#5a5a5a"

MINT = "#34D399"
SKY = "#38BDF8"
VIOLET = "#A78BFA"
PINK = "#F472B6"
CORAL = "#FB7185"
AMBER = "#FBBF24"
SPECTRUM = [VIOLET, SKY, MINT, AMBER, CORAL]

GLYPHS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&*+=<>/?$"

# =================================================================== CONTENT
ROLES = [("Tech Explorer", MINT), ("1st Year Student at NST Bengaluru", SKY),
         ("Dreaming in Algorithms, Debugging in Style", VIOLET)]

ABOUT_PARA = ["Hi, I'm Sahitya Singh!",
              "Tech Explorer.",
              "1st Year Student at NST Bengaluru.",
              "Dreaming in Algorithms,",
              "Debugging in Style."]
ABOUT_ROWS = [("NAME", "Sahitya Singh", CORAL), ("ROLE", "Tech Explorer", MINT),
              ("STUDYING", "1st Year · NST Bengaluru", SKY), ("LANGUAGES", "JavaScript · Python · Java", AMBER),
              ("FRONTEND", "HTML5 · CSS3", VIOLET), ("TOOLS", "Git", PINK)]



FORTUNES = [("Why do programmers prefer dark mode?", "because light attracts bugs!", MINT)]

STACK_1 = [("JavaScript", "#f1e05a"), ("Python", "#3572A5"), ("Java", "#b07219")]
STACK_2 = [("HTML5", "#e34c26"), ("CSS3", "#663399"), ("Git", "#f05032")]


# =================================================================== helpers
def esc(s):
    return html.escape(str(s), quote=True)


def write(name, svg):
    path = os.path.join(ASSETS, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(re.sub(r"\n\s*\n", "\n", svg.strip()) + "\n")
    print(f"wrote {os.path.relpath(path, ROOT)}  ({os.path.getsize(path)//1024} KB)")


def svg_open(w, h, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{esc(label)}"><title>{esc(label)}</title>')


def fade_in(delay, dur=0.6):
    total = delay + dur
    return (f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{delay/total:.4f};1" '
            f'dur="{total:.2f}s" fill="freeze"/>')


def rise(x, y, delay, dur=0.8):
    """Wrap content so it grows up from baseline point (x, y) once."""
    tot = delay + dur
    return (f'<g transform="translate({x:.1f},{y:.1f})"><g>'
            f'<animateTransform attributeName="transform" type="scale" values="1 0.02;1 0.02;1 1" '
            f'keyTimes="0;{delay/tot:.3f};1" dur="{tot:.2f}s" fill="freeze" calcMode="spline" '
            f'keySplines="0 0 1 1;0.2 0.8 0.2 1"/><g transform="translate({-x:.1f},{-y:.1f})">'), "</g></g></g>"


def mix(c1, c2, t):
    a = [int(c1[i:i+2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i+2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def shade(c, f):
    return mix("#000000", c, f)


def spectrum(t, cols=SPECTRUM):
    t = max(0.0, min(1.0, t)) * (len(cols) - 1)
    i = min(int(t), len(cols) - 2)
    return mix(cols[i], cols[i + 1], t - i)


def defs_common(w, h, c1=MINT, c2=VIOLET):
    return f"""<defs>
  <linearGradient id="beam" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{w}" y2="{h}">
    <stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>
  <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#ffffff" stroke-opacity="0.04"/></pattern>
  <radialGradient id="fadeR" cx="0.3" cy="0.35" r="0.75"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
  <mask id="gridmask"><rect width="{w}" height="{h}" fill="url(#fadeR)"/></mask>
  <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
  <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>
</defs>"""


def card(w, h, rx=16, beam=True, beam_dur=9):
    """Hairline card + a short coloured light segment travelling around the border."""
    per = 2 * (w + h) - (8 - 2 * math.pi) * rx
    b = ""
    if beam:
        b = (f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="{rx}" fill="none" stroke="url(#beam)" '
             f'stroke-width="1.3" stroke-dasharray="110 {per-110:.0f}" stroke-linecap="round">'
             f'<animate attributeName="stroke-dashoffset" values="0;-{per:.0f}" dur="{beam_dur}s" repeatCount="indefinite"/></rect>')
    return f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="{rx}" fill="{CARD}" stroke="{HAIR}"/>{b}'


def glow_blob(cx, cy, r, color, op=0.13, drift=60, dur=16):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" opacity="{op}" filter="url(#blur)">'
            f'<animate attributeName="cx" values="{cx};{cx+drift};{cx}" dur="{dur}s" repeatCount="indefinite"/></circle>')


def head(text, color, right="", right_color=DARK, w=W):
    r = (f'<text x="{w-36}" y="46" text-anchor="end" font-family="{MONO}" font-size="11" fill="{right_color}">{esc(right)}</text>'
         if right else "")
    return f'<text x="36" y="46" font-family="{MONO}" font-size="11" fill="{color}">{esc(text)}</text>{r}'


def wrap(text, n):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        if len(cur) + len(wd) + (1 if cur else 0) > n:
            lines.append(cur)
            cur = wd
        else:
            cur = f"{cur} {wd}" if cur else wd
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------ scramble text
def scramble(text, x0, y, size, colors, T, start=0.25, step=0.06, frames=7, fdur=0.055,
             weight=500, adv=None, seed=0, hold_end=0.5, ls=0, window=None):
    """Decode effect: each character flickers through random glyphs, then locks in.
    `colors` is one colour or a list (spread across the characters)."""
    rnd = random.Random(seed)
    adv = adv or size * 0.6 + ls
    n = len(text)
    out = []
    end = window[1] if window else T - hold_end
    begin = window[0] if window else 0
    for i, ch in enumerate(text):
        if ch == " ":
            continue
        col = colors if isinstance(colors, str) else spectrum(i / max(1, n - 1), colors)
        cx = x0 + i * adv + adv / 2
        t0 = begin + start + i * step
        common = (f'x="{cx:.1f}" y="{y}" text-anchor="middle" font-family="{MONO}" '
                  f'font-size="{size}" font-weight="{weight}"')
        for k in range(frames):
            a, b = t0 + k * fdur, t0 + (k + 1) * fdur
            g = esc(rnd.choice(GLYPHS))
            out.append(f'<text {common} fill="{DARK if k % 2 else GREY}" opacity="0">{g}'
                       f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;{a/T:.4f};{b/T:.4f}" '
                       f'calcMode="discrete" dur="{T}s" repeatCount="indefinite"/></text>')
        te = t0 + frames * fdur
        out.append(f'<text {common} fill="{col}" opacity="0">{esc(ch)}'
                   f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;{te/T:.4f};{end/T:.4f}" '
                   f'calcMode="discrete" dur="{T}s" repeatCount="indefinite"/></text>')
    return "\n".join(out)


# ------------------------------------------------------------ dot globe
def globe(cx, cy, R, n=150, frames=40, dur=36, pin=(12.97, 77.59)):
    tilt = 0.38
    golden = math.pi * (3 - math.sqrt(5))
    pts = []
    for i in range(n):
        y = 1 - 2 * (i + 0.5) / n
        r = math.sqrt(1 - y * y)
        th = i * golden
        pts.append((math.cos(th) * r, y, math.sin(th) * r))

    def project(p, a):
        x, y, z = p
        x1 = x * math.cos(a) + z * math.sin(a)
        z1 = -x * math.sin(a) + z * math.cos(a)
        y2 = y * math.cos(tilt) - z1 * math.sin(tilt)
        z2 = y * math.sin(tilt) + z1 * math.cos(tilt)
        return cx + R * x1, cy - R * y2, z2

    angles = [2 * math.pi * f / frames for f in range(frames + 1)]
    dots = []
    for i, p in enumerate(pts):
        col = spectrum((p[1] + 1) / 2, [CORAL, AMBER, MINT, SKY, VIOLET])
        xs, ys, os_ = [], [], []
        for a in angles:
            X, Y, Z = project(p, a)
            xs.append(f"{X:.1f}")
            ys.append(f"{Y:.1f}")
            os_.append(f"{0.08 + 0.8 * ((Z + 1) / 2) ** 2.2:.2f}")
        dots.append(f'<circle r="1.4" fill="{col}" cx="{xs[0]}" cy="{ys[0]}" opacity="{os_[0]}">'
                    f'<animate attributeName="cx" values="{";".join(xs)}" dur="{dur}s" repeatCount="indefinite"/>'
                    f'<animate attributeName="cy" values="{";".join(ys)}" dur="{dur}s" repeatCount="indefinite"/>'
                    f'<animate attributeName="opacity" values="{";".join(os_)}" dur="{dur}s" repeatCount="indefinite"/></circle>')
    la, lo = map(math.radians, pin)
    pp = (math.cos(la) * math.sin(lo), math.sin(la), math.cos(la) * math.cos(lo))
    xs, ys, os_ = [], [], []
    for a in angles:
        X, Y, Z = project(pp, a)
        xs.append(f"{X:.1f}")
        ys.append(f"{Y:.1f}")
        os_.append("1" if Z > -0.05 else "0")
    anim = (f'<animate attributeName="cx" values="{";".join(xs)}" dur="{dur}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cy" values="{";".join(ys)}" dur="{dur}s" repeatCount="indefinite"/>')
    vis = f'<animate attributeName="opacity" values="{";".join(os_)}" dur="{dur}s" repeatCount="indefinite"/>'
    pin_svg = f"""
<g>{vis}
  <circle r="4" fill="none" stroke="{CORAL}" stroke-width="1.2" cx="{xs[0]}" cy="{ys[0]}">{anim}
    <animate attributeName="r" values="3;16" dur="2.2s" repeatCount="indefinite"/>
    <animate attributeName="stroke-opacity" values="0.9;0" dur="2.2s" repeatCount="indefinite"/></circle>
  <circle r="3.4" fill="{CORAL}" cx="{xs[0]}" cy="{ys[0]}">{anim}</circle>
</g>"""
    rx, ry = R * 1.42, R * 0.36
    ring = (f'<g transform="rotate(-14 {cx} {cy})">'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx:.0f}" ry="{ry:.0f}" fill="none" stroke="{VIOLET}" stroke-opacity="0.22"/>'
            f'<circle r="2.6" fill="{AMBER}"><animateMotion dur="14s" repeatCount="indefinite" '
            f'path="M{cx - rx:.1f},{cy} a{rx:.1f},{ry:.1f} 0 1,0 {2*rx:.1f},0 a{rx:.1f},{ry:.1f} 0 1,0 -{2*rx:.1f},0"/></circle></g>')
    halo = (f'<circle cx="{cx}" cy="{cy}" r="{R+2}" fill="none" stroke="#ffffff" stroke-opacity="0.06"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{R*0.9:.0f}" fill="{SKY}" opacity="0.05" filter="url(#soft)"/>')
    return halo + "".join(dots) + pin_svg + ring


# ============================================================ HERO
def hero():
    H = 380
    T = 12
    name = "SAHITYA SINGH"
    size, ls = 44, 2
    adv = size * 0.6 + ls
    RT = len(ROLES) * 3.5
    role_svg = ""
    for i, (r, col) in enumerate(ROLES):
        s, e = i / len(ROLES), (i + 1) / len(ROLES)
        kt = f"0;{s:.4f};{s+0.02:.4f};{e-0.03:.4f};{e-0.005:.4f};1"
        role_svg += (f'<text x="148" y="266" font-family="{MONO}" font-size="13" fill="{col}" opacity="0">{esc(r)}'
                     f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kt}" dur="{RT}s" repeatCount="indefinite"/>'
                     f'<animate attributeName="y" values="272;272;266;266;262;262" keyTimes="{kt}" dur="{RT}s" repeatCount="indefinite"/></text>')
    bar = "".join(f'<rect x="{36 + i*26}" y="166" width="22" height="3" rx="1.5" fill="{c}">{fade_in(1.0 + i*0.08)}</rect>'
                  for i, c in enumerate(SPECTRUM))
    return f"""{svg_open(W, H, "Hi, I'm Sahitya Singh — Tech Explorer, 1st Year Student at NST Bengaluru")}
{defs_common(W, H, VIOLET, MINT)}
<defs><clipPath id="clip"><rect width="{W}" height="{H}" rx="16"/></clipPath>
<linearGradient id="beamV" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{SKY}" stop-opacity="0"/><stop offset="0.85" stop-color="{SKY}" stop-opacity="0.06"/><stop offset="1" stop-color="#fff" stop-opacity="0.18"/></linearGradient>
<filter id="arcglow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
{card(W, H, beam_dur=11)}
<g clip-path="url(#clip)">
  <rect width="{W}" height="{H}" fill="url(#grid)" mask="url(#gridmask)"/>
  {glow_blob(140, 110, 120, VIOLET, 0.16, 80, 18)}
  {glow_blob(330, 260, 110, MINT, 0.10, -70, 15)}
  {glow_blob(700, 90, 110, CORAL, 0.08, -50, 20)}
  {globe(640, 178, 118)}
  {orbit_tags(640, 178, 118)}
  {arcs(640, 178, 118)}
  {meteors()}
  {sparks(20, W-20, 30, H-10)}
  <rect x="0" y="-80" width="{W}" height="80" fill="url(#beamV)"><animate attributeName="y" values="-80;{H}" dur="5.5s" repeatCount="indefinite"/></rect>
  {glitch_bars(W, H, 5, 0.86, 8)}
</g>
<text x="36" y="42" font-family="{MONO}" font-size="11" letter-spacing="1" fill="{DARK}">{USER.lower()} / README.md</text>
<g font-family="{MONO}" font-size="11" letter-spacing="1.5">
  <circle cx="{W-36-27*(11*0.6+1.5)-12:.0f}" cy="38" r="3.5" fill="{MINT}"><animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/></circle>
  <text x="{W-36}" y="42" text-anchor="end" fill="{GREY}">WELCOME TO MY DIGITAL WORLD</text>
</g>
<g>{scramble(name, 36, 146, size, WHITE, T, adv=adv, seed=8, ls=ls, weight=600)}{jitter(5, 0.86)}</g>
{rgb_split(name, 36, 146, size, adv, 5, 0.86)}
{bar}
<text x="36" y="200" font-family="{SANS}" font-size="16" fill="{GREY}"><tspan fill="{WHITE}">Tech Explorer.</tspan>{fade_in(0.9)}</text>
<text x="36" y="224" font-family="{SANS}" font-size="16" fill="{GREY}">1st Year Student at NST Bengaluru.{fade_in(1.1)}</text>
<text x="36" y="266" font-family="{MONO}" font-size="13" fill="{GREY}">currently →{fade_in(1.3)}</text>
{role_svg}
<line x1="36" x2="{W-36}" y1="318" y2="318" stroke="{HAIR}"/>
<g font-family="{MONO}" font-size="11" letter-spacing="1">
  <text x="36" y="347" fill="{CORAL}">●</text><text x="52" y="347" fill="{DARK}">NST BENGALURU</text>
  <text x="206" y="347" fill="{DARK}">1ST YEAR</text>
  <text x="{W-36}" y="347" text-anchor="end" fill="{DARK}">scroll ↓</text>
</g>
</svg>"""



# ------------------------------------------------------------ chaos helpers
def matrix_rain(w, h, cols=None, op=0.16, seed=11):
    rnd = random.Random(seed)
    cols = cols or int(w / 22)
    out = ""
    for i in range(cols):
        x = 12 + i * (w - 24) / (cols - 1)
        n = rnd.randint(6, 12)
        col = SPECTRUM[i % len(SPECTRUM)]
        dur = rnd.uniform(3.5, 8)
        start = rnd.uniform(0, dur)
        glyphs = ""
        for k in range(n):
            g = esc(rnd.choice("01アイウエオカキクケコｱｲｳｴｵ{}<>/=*#$"))
            fo = (k + 1) / n
            glyphs += f'<text x="0" y="{k*15}" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{"#ffffff" if k == n-1 else col}" opacity="{fo:.2f}">{g}</text>'
        out += (f'<g transform="translate({x:.1f},-200)">{glyphs}'
                f'<animateTransform attributeName="transform" type="translate" values="{x:.1f} {-n*15};{x:.1f} {h+20}" '
                f'dur="{dur:.1f}s" begin="-{start:.1f}s" repeatCount="indefinite"/></g>')
    return f'<g opacity="{op}">{out}</g>'


def jitter(dur=6, at=0.82):
    """Occasional 'bad signal' shake applied to the parent group."""
    vals = "0 0;0 0;-4 1;5 -1;-2 0;3 1;0 0;0 0"
    kt = f"0;{at:.3f};{at+0.01:.3f};{at+0.02:.3f};{at+0.03:.3f};{at+0.04:.3f};{at+0.05:.3f};1"
    return (f'<animateTransform attributeName="transform" type="translate" values="{vals}" keyTimes="{kt}" '
            f'calcMode="discrete" dur="{dur}s" repeatCount="indefinite"/>')


def glitch_bars(w, h, dur=6, at=0.82, seed=3):
    rnd = random.Random(seed)
    out = ""
    for i in range(5):
        y = rnd.uniform(0.1, 0.9) * h
        hh = rnd.uniform(3, 14)
        col = [SKY, PINK, MINT, VIOLET, AMBER][i]
        t = at + i * 0.008
        out += (f'<rect x="{rnd.uniform(-40, 40):.0f}" y="{y:.0f}" width="{w}" height="{hh:.0f}" fill="{col}" opacity="0">'
                f'<animate attributeName="opacity" values="0;0;0.35;0;0" keyTimes="0;{t:.3f};{t+0.006:.3f};{t+0.02:.3f};1" '
                f'calcMode="discrete" dur="{dur}s" repeatCount="indefinite"/></rect>')
    return out


def sparks(x0, x1, y0, y1, n=22, seed=5):
    rnd = random.Random(seed)
    out = ""
    for i in range(n):
        x = rnd.uniform(x0, x1)
        col = SPECTRUM[i % len(SPECTRUM)]
        dur = rnd.uniform(4, 9)
        r = rnd.choice([1, 1.3, 1.6, 2])
        out += (f'<circle cx="{x:.0f}" cy="{y1}" r="{r}" fill="{col}">'
                f'<animate attributeName="cy" values="{y1};{y0}" dur="{dur:.1f}s" begin="-{rnd.uniform(0, dur):.1f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0;1;0" dur="{dur:.1f}s" begin="-{rnd.uniform(0, dur):.1f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="cx" values="{x:.0f};{x+rnd.uniform(-20, 20):.0f};{x:.0f}" dur="{dur/2:.1f}s" repeatCount="indefinite"/></circle>')
    return out


def arcs(cx, cy, R, seed=9):
    """Electric arcs that crackle from the globe out to the orbit."""
    rnd = random.Random(seed)
    out = ""
    T = 7
    for i in range(5):
        a = rnd.uniform(0, 2 * math.pi)
        x0, y0 = cx + R * 0.9 * math.cos(a), cy + R * 0.9 * math.sin(a)
        x1, y1 = cx + R * 1.45 * math.cos(a), cy + R * 1.1 * math.sin(a)
        pts = [(x0, y0)]
        for k in range(1, 6):
            t = k / 6
            pts.append((x0 + (x1 - x0) * t + rnd.uniform(-9, 9), y0 + (y1 - y0) * t + rnd.uniform(-9, 9)))
        pts.append((x1, y1))
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        col = [SKY, VIOLET, PINK, MINT, AMBER][i]
        b = rnd.uniform(0, T - 0.6)
        kt = f"0;{b/T:.3f};{(b+0.05)/T:.3f};{(b+0.12)/T:.3f};{(b+0.18)/T:.3f};{(b+0.3)/T:.3f};1"
        out += (f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1.6" stroke-linejoin="round" filter="url(#arcglow)" opacity="0">'
                f'<animate attributeName="opacity" values="0;0;1;0.2;1;0;0" keyTimes="{kt}" dur="{T}s" repeatCount="indefinite"/></path>')
    return out


def static_chars(text, x0, y, size, adv, color, weight=600):
    return "".join(f'<text x="{x0 + i*adv + adv/2:.1f}" y="{y}" text-anchor="middle" font-family="{MONO}" font-size="{size}" font-weight="{weight}" fill="{color}">{esc(ch)}</text>'
                   for i, ch in enumerate(text) if ch != " ")


def rgb_split(text, x0, y, size, adv, dur=5, at=0.86):
    out = ""
    for col, dx, dy, off in ((SKY, -4, -1, 0), (PINK, 4, 1, 0.004)):
        t = at + off
        out += (f'<g opacity="0" style="mix-blend-mode:screen">{static_chars(text, x0 + dx, y + dy, size, adv, col)}'
                f'<animate attributeName="opacity" values="0;0;0.9;0;0.7;0;0" keyTimes="0;{t:.3f};{t+0.01:.3f};{t+0.025:.3f};{t+0.035:.3f};{t+0.05:.3f};1" '
                f'calcMode="discrete" dur="{dur}s" repeatCount="indefinite"/></g>')
    return out


# ============================================================ BOOT sequence (top of page)
BOOT_LINES = [("OK", MINT, "user: sahitya singh"),
              ("OK", SKY, "role: tech explorer"),
              ("OK", VIOLET, "status: 1st year student @ NST Bengaluru"),
              ("OK", AMBER, "languages: javascript · python · java"),
              ("OK", PINK, "frontend: html5 · css3 · tools: git"),
              ("OK", CORAL, "dreaming in algorithms, debugging in style")]


def boot():
    H = 236
    T = 13.0
    y0, lh = 74, 21
    out = ""
    for i, (tag, col, msg) in enumerate(BOOT_LINES):
        t0 = 0.4 + i * 0.55
        full = f"[{tag:^4}] {msg}"
        w = len(full) * 12.5 * 0.6 + 6
        k = f"0;{t0/T:.4f};{(t0+0.35)/T:.4f};{(T-0.6)/T:.4f};{(T-0.5)/T:.4f};1"
        out += (f'<clipPath id="b{i}"><rect x="36" y="{y0+i*lh-15}" height="20" width="0">'
                f'<animate attributeName="width" values="0;0;{w:.0f};{w:.0f};0;0" keyTimes="{k}" dur="{T}s" repeatCount="indefinite"/></rect></clipPath>'
                f'<text clip-path="url(#b{i})" x="36" y="{y0+i*lh}" font-family="{MONO}" font-size="12.5" xml:space="preserve">'
                f'<tspan fill="{DARK}">[</tspan><tspan fill="{col}" font-weight="700">{tag:^4}</tspan><tspan fill="{DARK}">]</tspan>'
                f'<tspan fill="#cfcfcf"> {esc(msg)}</tspan></text>')
    pb_t0 = 0.4 + len(BOOT_LINES) * 0.55 + 0.2
    pb_t1 = pb_t0 + 1.6
    bx, by, bw = 36, 208, 420
    stops = "".join(f'<stop offset="{i/(len(SPECTRUM)-1):.2f}" stop-color="{c}"/>' for i, c in enumerate(SPECTRUM))
    kt = f"0;{pb_t0/T:.4f};{pb_t1/T:.4f};{(T-0.5)/T:.4f};1"
    seg = "".join(f'<rect x="{bx + i*(bw/24):.1f}" y="{by-8}" width="{bw/24-3:.1f}" height="10" rx="2" fill="#161616"/>' for i in range(24))
    granted = pb_t1 + 0.2
    gk = f"0;{granted/T:.4f};{(granted+0.05)/T:.4f};{(T-0.5)/T:.4f};{(T-0.45)/T:.4f};1"
    # radar on the right
    rx, ry, rr = 690, 122, 64
    rings = "".join(f'<circle cx="{rx}" cy="{ry}" r="{rr*k/3:.0f}" fill="none" stroke="{MINT}" stroke-opacity="0.18"/>' for k in (1, 2, 3))
    rnd = random.Random(42)
    blips = ""
    for j in range(7):
        ang = rnd.uniform(0, 2 * math.pi)
        dist = rnd.uniform(0.25, 0.92) * rr
        bxp, byp = rx + dist * math.cos(ang), ry + dist * math.sin(ang)
        frac = ((math.degrees(ang) + 90) % 360) / 360
        col = SPECTRUM[j % len(SPECTRUM)]
        blips += (f'<circle cx="{bxp:.1f}" cy="{byp:.1f}" r="3" fill="{col}" opacity="0">'
                  f'<animate attributeName="opacity" values="0;0;1;0.15;0" keyTimes="0;{max(0,frac-0.001):.3f};{frac:.3f};{min(1,frac+0.35):.3f};1" dur="4s" repeatCount="indefinite"/></circle>')
    cpu = ""
    for j in range(14):
        x = 628 + j * 9
        hs = ";".join(str(random.Random(j * 7 + k).randint(3, 18)) for k in range(8))
        ys = ";".join(str(216 - int(v)) for v in hs.split(";"))
        cpu += (f'<rect x="{x}" y="200" width="6" height="16" rx="1.5" fill="{spectrum(j/13)}">'
                f'<animate attributeName="height" values="{hs}" dur="{1.2 + (j % 4)*0.15:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="y" values="{ys}" dur="{1.2 + (j % 4)*0.15:.2f}s" repeatCount="indefinite"/></rect>')
    cpu += f'<text x="{628+14*9+8}" y="214" font-family="{MONO}" font-size="9.5" letter-spacing="1.5" fill="{DARK}">CPU</text>'
    return f"""{svg_open(W, H, "Boot sequence: Sahitya Singh, tech explorer, 1st year student at NST Bengaluru")}
{defs_common(W, H, MINT, VIOLET)}
<defs>
  <linearGradient id="pb" x1="0" x2="1">{stops}</linearGradient>
  <clipPath id="pbc"><rect x="{bx}" y="{by-8}" height="10" width="0"><animate attributeName="width" values="0;0;{bw};{bw};0" keyTimes="{kt}" dur="{T}s" repeatCount="indefinite"/></rect></clipPath>
  <radialGradient id="sweep" cx="0" cy="0" r="1"><stop offset="0" stop-color="{MINT}" stop-opacity="0.45"/><stop offset="1" stop-color="{MINT}" stop-opacity="0"/></radialGradient>
  <clipPath id="clip"><rect width="{W}" height="{H}" rx="16"/></clipPath>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" opacity="0.03"/></pattern>
</defs>
{card(W, H, beam_dur=8)}
<g clip-path="url(#clip)">{matrix_rain(W, H, op=0.13)}<rect width="{W}" height="{H}" fill="url(#scan)"/>{glow_blob(700, 130, 90, MINT, 0.08, -30, 10)}{glitch_bars(W, H, 6, 0.8)}</g>
<circle cx="30" cy="26" r="5" fill="#ff5f57"/><circle cx="48" cy="26" r="5" fill="#febc2e"/><circle cx="66" cy="26" r="5" fill="#28c840"/>
<text x="{W/2}" y="30" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{DARK}">sahitya@nst — boot.sh</text>
<line x1="0" x2="{W}" y1="46" y2="46" stroke="{HAIR}"/>
<g>{out}{jitter(6, 0.8)}</g>
{cpu}
{seg}
<g clip-path="url(#pbc)"><rect x="{bx}" y="{by-8}" width="{bw}" height="10" fill="url(#pb)"/></g>
<rect x="{bx}" y="{by-8}" width="{bw}" height="10" fill="none"/>
<text x="{bx+bw+14}" y="{by+1}" font-family="{MONO}" font-size="11.5" font-weight="700" fill="{MINT}" opacity="0">ACCESS GRANTED ▸
  <animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{gk}" dur="{T}s" repeatCount="indefinite"/>
  <animate attributeName="fill" values="{MINT};{SKY};{VIOLET};{PINK};{AMBER};{MINT}" dur="1.2s" repeatCount="indefinite"/></text>
{rings}
<line x1="{rx-rr}" x2="{rx+rr}" y1="{ry}" y2="{ry}" stroke="{MINT}" stroke-opacity="0.12"/>
<line x1="{rx}" x2="{rx}" y1="{ry-rr}" y2="{ry+rr}" stroke="{MINT}" stroke-opacity="0.12"/>
<g><path d="M{rx},{ry} L{rx},{ry-rr} A{rr},{rr} 0 0,1 {rx+rr*math.sin(math.radians(40)):.1f},{ry-rr*math.cos(math.radians(40)):.1f} Z" fill="url(#sweep)"/>
  <line x1="{rx}" y1="{ry}" x2="{rx}" y2="{ry-rr}" stroke="{MINT}" stroke-width="1.5"/>
  <animateTransform attributeName="transform" type="rotate" values="0 {rx} {ry};360 {rx} {ry}" dur="4s" repeatCount="indefinite"/></g>
{blips}
<circle cx="{rx}" cy="{ry}" r="3" fill="{MINT}"/>
<text x="{rx}" y="{ry-rr-8}" text-anchor="middle" font-family="{MONO}" font-size="9.5" letter-spacing="2" fill="{DARK}">WELCOME TO MY DIGITAL WORLD</text>
</svg>"""


# ============================================================ hero extras
def meteors():
    out = ""
    for i, (x, y, d, b, c) in enumerate([(120, -20, 1.4, 0.5, WHITE), (420, -30, 1.2, 3.1, SKY), (300, -10, 1.6, 6.3, VIOLET), (560, -25, 1.3, 8.8, PINK)]):
        T = 10
        out += (f'<g opacity="0"><line x1="0" y1="0" x2="-70" y2="-34" stroke="url(#met{i})" stroke-width="1.6" stroke-linecap="round"/>'
                f'<circle r="1.8" fill="#fff"/>'
                f'<animateTransform attributeName="transform" type="translate" values="{x} {y};{x} {y};{x+260} {y+126};{x+260} {y+126}" '
                f'keyTimes="0;{b/T:.3f};{(b+d)/T:.3f};1" dur="{T}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;{b/T:.3f};{(b+0.2)/T:.3f};{(b+d)/T:.3f};1" dur="{T}s" repeatCount="indefinite"/></g>'
                f'<defs><linearGradient id="met{i}" x1="0" x2="1"><stop offset="0" stop-color="{c}"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></linearGradient></defs>')
    return out


def orbit_tags(cx, cy, R):
    rx, ry = R * 1.42, R * 0.36
    path = f"M{cx - rx:.1f},{cy} a{rx:.1f},{ry:.1f} 0 1,0 {2*rx:.1f},0 a{rx:.1f},{ry:.1f} 0 1,0 -{2*rx:.1f},0"
    out = f'<g transform="rotate(-14 {cx} {cy})">'
    for i, (t, c) in enumerate([("JS", AMBER), ("PY", SKY), ("JAVA", CORAL), ("HTML", PINK), ("CSS", VIOLET), ("GIT", MINT)]):
        out += (f'<g><rect x="{-(len(t)*3.3+9):.1f}" y="-10" width="{len(t)*6.6+18:.1f}" height="20" rx="10" fill="{CARD}" stroke="{c}" stroke-opacity="0.7"/>'
                f'<text y="4" text-anchor="middle" font-family="{MONO}" font-size="10" font-weight="700" fill="{c}">{t}</text>'
                f'<animateMotion dur="22s" begin="-{i*22/6:.1f}s" repeatCount="indefinite" path="{path}"/></g>')
    return out + "</g>"


# ============================================================ DNA helix divider
def helix():
    H = 96
    n, frames, dur = 46, 24, 6
    cy, amp = H / 2, 26
    x0, x1 = 30, W - 30
    out = ""
    for i in range(n):
        x = x0 + (x1 - x0) * i / (n - 1)
        col = spectrum(i / (n - 1))
        ph = i * 0.42
        ya, yb, oa, ob = [], [], [], []
        for f in range(frames + 1):
            t = 2 * math.pi * f / frames + ph
            ya.append(f"{cy + amp*math.sin(t):.1f}")
            yb.append(f"{cy - amp*math.sin(t):.1f}")
            oa.append(f"{0.35 + 0.65*(math.cos(t)+1)/2:.2f}")
            ob.append(f"{0.35 + 0.65*(1-math.cos(t))/2:.2f}")
        A = f'dur="{dur}s" repeatCount="indefinite"'
        out += (f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{ya[0]}" y2="{yb[0]}" stroke="{col}" stroke-opacity="0.18">'
                f'<animate attributeName="y1" values="{";".join(ya)}" {A}/><animate attributeName="y2" values="{";".join(yb)}" {A}/></line>'
                f'<circle cx="{x:.1f}" cy="{ya[0]}" r="3.2" fill="{col}"><animate attributeName="cy" values="{";".join(ya)}" {A}/>'
                f'<animate attributeName="opacity" values="{";".join(oa)}" {A}/></circle>'
                f'<circle cx="{x:.1f}" cy="{yb[0]}" r="3.2" fill="{col}"><animate attributeName="cy" values="{";".join(yb)}" {A}/>'
                f'<animate attributeName="opacity" values="{";".join(ob)}" {A}/></circle>')
    return f"""{svg_open(W, H, "divider")}
{out}
</svg>"""


# ============================================================ section label
def label(idx, title, tag, color):
    H = 56
    tw = len(title) * (12 * 0.6 + 3)
    x1 = 36 + 34 + tw + 16
    return f"""{svg_open(W, H, f"{idx} {title}")}
<defs><linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="{color}" stop-opacity="0.6"/><stop offset="1" stop-color="{HAIR2}"/></linearGradient></defs>
<rect x="2" y="17" width="28" height="18" rx="9" fill="{color}" fill-opacity="0.12" stroke="{color}" stroke-opacity="0.4"/>
<text x="16" y="30" text-anchor="middle" font-family="{MONO}" font-size="11" font-weight="600" fill="{color}">{idx}</text>
<text x="42" y="31" font-family="{MONO}" font-size="12" font-weight="600" letter-spacing="3" fill="{WHITE}">{esc(title.upper())}</text>
<rect x="{x1:.0f}" y="26" width="{W-140-x1:.0f}" height="1" fill="url(#ln)"/>
<circle cy="26.5" r="2" fill="{color}"><animate attributeName="cx" values="{x1:.0f};{W-140}" dur="6s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.9;1" dur="6s" repeatCount="indefinite"/></circle>
<text x="{W-6}" y="31" text-anchor="end" font-family="{MONO}" font-size="11" fill="{DARK}">{esc(tag)}</text>
</svg>"""


# ============================================================ about
def about():
    H = 296
    p = "".join(f'<text x="36" y="{100 + i*25}" font-family="{SANS}" font-size="15.5" fill="{"#d4d4d4" if i < 3 else GREY}">{esc(l)}{fade_in(0.15 + i*0.12)}</text>'
                for i, l in enumerate(ABOUT_PARA))
    rx = 470
    r = ""
    for i, (k, v, c) in enumerate(ABOUT_ROWS):
        y = 70 + i * 33
        r += (f'<g>{fade_in(0.3 + i*0.1)}'
              f'<circle cx="{rx+3}" cy="{y+15}" r="3" fill="{c}"/>'
              f'<text x="{rx+14}" y="{y+19}" font-family="{MONO}" font-size="10.5" letter-spacing="1.5" fill="{DARK}">{k}</text>'
              f'<text x="{rx+108}" y="{y+19}" font-family="{MONO}" font-size="12.5" fill="{WHITE}">{esc(v)}</text>'
              f'<line x1="{rx}" x2="{W-36}" y1="{y+32}" y2="{y+32}" stroke="{HAIR}"/></g>')
    return f"""{svg_open(W, H, "About: Sahitya Singh, Tech Explorer, 1st Year Student at NST Bengaluru. Dreaming in Algorithms, Debugging in Style.")}
{defs_common(W, H, MINT, SKY)}
<defs><clipPath id="clip"><rect width="{W}" height="{H}" rx="16"/></clipPath></defs>
{card(W, H, beam_dur=10)}
<g clip-path="url(#clip)">{glow_blob(120, 260, 110, SKY, 0.08, 60, 17)}</g>
{head("~/whoami", MINT)}
<line x1="{rx-34}" x2="{rx-34}" y1="36" y2="{H-36}" stroke="{HAIR}"/>
{p}
{r}
</svg>"""


# ============================================================ stack marquee
def chip_w(t):
    return len(t) * 7.6 + 40


def chips_row(items):
    x, out = 0, ""
    for name, col in items:
        w = chip_w(name)
        out += (f'<g transform="translate({x:.1f},0)"><rect width="{w:.1f}" height="34" rx="17" fill="{col}" fill-opacity="0.07" stroke="{col}" stroke-opacity="0.35"/>'
                f'<circle cx="17" cy="17" r="3.5" fill="{col}"/>'
                f'<text x="29" y="21.5" font-family="{MONO}" font-size="12.5" fill="{WHITE}">{esc(name)}</text></g>')
        x += w + 10
    return out, x


def stack(row1=None, row2=None, note="tools i reach for"):
    H = 130
    row1, row2 = row1 or STACK_1, row2 or STACK_2
    a, wa = chips_row(row1)
    b, wb = chips_row(row2)
    # repeat each row enough times to always overflow the card while scrolling
    rep = lambda s, w, n: "".join(f'<g transform="translate({i*w:.1f},0)">{s}</g>' for i in range(n))
    na, nb = max(3, math.ceil(2 * W / wa) + 1), max(3, math.ceil(2 * W / wb) + 1)
    names = ", ".join(n for n, _ in row1 + row2)
    return f"""{svg_open(W, H, "Stack: " + names)}
{defs_common(W, H)}
<defs>
  <linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.12" stop-color="#fff"/><stop offset="0.88" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <mask id="edges"><rect width="{W}" height="{H}" fill="url(#edge)"/></mask>
</defs>
{card(W, H, beam=False)}
<g mask="url(#edges)">
  <g transform="translate(0,22)"><g>{rep(a, wa, na)}<animateTransform attributeName="transform" type="translate" values="0 0;-{wa:.1f} 0" dur="38s" repeatCount="indefinite"/></g></g>
  <g transform="translate(0,72)"><g>{rep(b, wb, nb)}<animateTransform attributeName="transform" type="translate" values="-{wb:.1f} 0;0 0" dur="44s" repeatCount="indefinite"/></g></g>
</g>
</svg>"""


# ============================================================ live data
def gql(token, query, variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": USER})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    return data["data"]


REPO_FIELDS = "name description url stargazerCount forkCount isFork pushedAt owner{login} primaryLanguage{name color}"


def fetch_stats(token):
    q = f"""query($u:String!){{user(login:$u){{createdAt
      followers{{totalCount}} pullRequests{{totalCount}}
      pinnedItems(first:6,types:REPOSITORY){{nodes{{... on Repository{{{REPO_FIELDS}}}}}}}
      repositories(ownerAffiliations:OWNER,privacy:PUBLIC,first:100,isFork:false,orderBy:{{field:PUSHED_AT,direction:DESC}}){{totalCount
        nodes{{{REPO_FIELDS} repositoryTopics(first:10){{nodes{{topic{{name}}}}}} languages(first:10,orderBy:{{field:SIZE,direction:DESC}}){{edges{{size node{{name color}}}}}}}}}}}}}}"""
    u = gql(token, q, {"u": USER})["user"]
    langs, stars = {}, 0
    for r in u["repositories"]["nodes"]:
        stars += r["stargazerCount"]
        for e in r["languages"]["edges"]:
            n = e["node"]["name"]
            langs.setdefault(n, [0, e["node"]["color"] or GREY])
            langs[n][0] += e["size"]
    # latest projects = my own repos, most recently pushed first (skip this profile repo)
    recent = [r for r in u["repositories"]["nodes"] if r["name"].lower() != USER.lower()]
    projects = recent[:6]
    start = dt.datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00")).date()
    today = dt.datetime.now(dt.timezone.utc).date()
    cq = """query($u:String!,$f:DateTime,$t:DateTime){user(login:$u){contributionsCollection(from:$f,to:$t){
      totalCommitContributions contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}"""
    days, commits, y0 = {}, 0, start
    while y0 <= today:
        y1 = min(today, y0 + dt.timedelta(days=364))
        c = gql(token, cq, {"u": USER, "f": f"{y0}T00:00:00Z", "t": f"{y1}T23:59:59Z"})["user"]["contributionsCollection"]
        commits += c["totalCommitContributions"]
        for w in c["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                days[d["date"]] = d["contributionCount"]
        y0 = y1 + dt.timedelta(days=1)
    return dict(today=today, start=start, days=days, commits=commits, prs=u["pullRequests"]["totalCount"],
                repos=u["repositories"]["totalCount"], stars=stars, followers=u["followers"]["totalCount"],
                langs=sorted(((k, v[0], v[1]) for k, v in langs.items()), key=lambda x: -x[1]),
                projects=projects[:6])


def streaks(days, today):
    ds = sorted(days)
    longest = cur = 0
    for d in ds:
        cur = cur + 1 if days[d] > 0 else 0
        longest = max(longest, cur)
    current, i = 0, len(ds) - 1
    if i >= 0 and ds[i] == str(today) and days[ds[i]] == 0:
        i -= 1
    while i >= 0 and days[ds[i]] > 0:
        current, i = current + 1, i - 1
    return current, longest


# ============================================================ stats + city
GH_LEVELS = ["#0e4429", "#006d32", "#26a641", "#39d353"]   # GitHub's own dark-mode greens
EMPTY_TOP, EMPTY_SIDE = "#161b22", "#0d1117"


def levels_for(values):
    """GitHub-style quartile buckets over non-zero days -> level 1..4."""
    nz = sorted(v for v in values if v > 0)
    if not nz:
        return lambda v: 0
    q = [nz[int(len(nz) * p)] if int(len(nz) * p) < len(nz) else nz[-1] for p in (0.25, 0.5, 0.75)]
    return lambda v: 0 if v <= 0 else 1 + sum(v > t for t in q)


def lighten(c, t):
    return mix(c, "#ffffff", t)


def city(days, today, weeks=53, oy=128, ox=96, u=(12.6, 3.0), v=(-5.2, 6.4), maxh=64):
    """Full-year contribution graph as a lit 3D city on a ground slab.
    weeks run left->right (u), weekdays Sun..Sat run back->front (v)."""
    sunday = today - dt.timedelta(days=(today.weekday() + 1) % 7)
    first = sunday - dt.timedelta(weeks=weeks - 1)
    cells = []
    for c in range(weeks):
        for r in range(7):
            d = first + dt.timedelta(days=c * 7 + r)
            if d <= today:
                cells.append((c, r, d, days.get(str(d), 0)))
    vals = [x[3] for x in cells]
    lvl = levels_for(vals)
    mx = max(vals + [1])

    def P(c, r):
        return ox + c * u[0] + r * v[0], oy + c * u[1] + r * v[1]

    out = []
    # ground slab + soft shadow
    a, b_, cc, d_ = P(0, 0), P(weeks, 0), P(weeks, 7), P(0, 7)
    th = 9
    out.append(f'<polygon points="{a[0]-6:.1f},{a[1]+8:.1f} {b_[0]+10:.1f},{b_[1]+8:.1f} {cc[0]+14:.1f},{cc[1]+22:.1f} {d_[0]-2:.1f},{d_[1]+22:.1f}" fill="#000" opacity="0.55" filter="url(#shadow)"/>')
    out.append(f'<polygon points="{d_[0]:.1f},{d_[1]:.1f} {cc[0]:.1f},{cc[1]:.1f} {cc[0]:.1f},{cc[1]+th:.1f} {d_[0]:.1f},{d_[1]+th:.1f}" fill="#11161d"/>')
    out.append(f'<polygon points="{b_[0]:.1f},{b_[1]:.1f} {cc[0]:.1f},{cc[1]:.1f} {cc[0]:.1f},{cc[1]+th:.1f} {b_[0]:.1f},{b_[1]+th:.1f}" fill="#0b0f14"/>')
    out.append(f'<polygon points="{a[0]:.1f},{a[1]:.1f} {b_[0]:.1f},{b_[1]:.1f} {cc[0]:.1f},{cc[1]:.1f} {d_[0]:.1f},{d_[1]:.1f}" fill="#0f141a" stroke="#1d242d" stroke-width="0.8"/>')
    out.append(f'<line x1="{d_[0]:.1f}" y1="{d_[1]:.1f}" x2="{cc[0]:.1f}" y2="{cc[1]:.1f}" stroke="#2b3440" stroke-width="0.8"/>')

    g = 0.12  # gap between blocks
    cells.sort(key=lambda t: (P(t[0], t[1])[1], t[0]))
    peak = max(cells, key=lambda t: t[3])
    peak_pos = None
    for c, r, d, val in cells:
        L = lvl(val)
        p0 = P(c + g, r + g)
        p1 = P(c + 1 - g, r + g)
        p2 = P(c + 1 - g, r + 1 - g)
        p3 = P(c + g, r + 1 - g)
        if L == 0:
            pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (p0, p1, p2, p3))
            out.append(f'<polygon points="{pts}" fill="{EMPTY_TOP}"><title>{d:%a %d %b %Y}: no contributions</title></polygon>')
            continue
        # log scale: one huge day (e.g. a bulk import) should not flatten the rest of the year
        h = 5 + (maxh - 5) * math.log1p(val) / math.log1p(mx)
        base = GH_LEVELS[L - 1]
        top, front, right = lighten(base, 0.10), shade(base, 0.72), shade(base, 0.48)
        up = lambda p: (p[0], p[1] - h)
        q0, q1, q2, q3 = up(p0), up(p1), up(p2), up(p3)
        fmt = lambda *ps: " ".join(f"{x:.1f},{y:.1f}" for x, y in ps)
        body = (f'<polygon points="{fmt(p3, p2, q2, q3)}" fill="{front}"/>'
                f'<polygon points="{fmt(p1, p2, q2, q1)}" fill="{right}"/>'
                f'<polygon points="{fmt(q0, q1, q2, q3)}" fill="{top}"/>'
                f'<polyline points="{fmt(q3, q0, q1)}" fill="none" stroke="#ffffff" stroke-opacity="{0.10 + 0.05*L:.2f}" stroke-width="0.7"/>')
        o, cl = rise(p2[0], (p2[1] + p3[1]) / 2, 0.15 + c * 0.022 + r * 0.01, 0.7)
        out.append(f'<g><title>{d:%a %d %b %Y}: {val} contribution{"s" if val != 1 else ""}</title>{o}{body}{cl}</g>')
        if (c, r) == (peak[0], peak[1]):
            peak_pos = ((q0[0] + q2[0]) / 2, (q0[1] + q2[1]) / 2)
    # month labels along the front edge, weekday labels on the left
    lab = ""
    seen = set()
    for c in range(weeks):
        d = first + dt.timedelta(days=c * 7)
        if d.day <= 7 and (d.year, d.month) not in seen:
            seen.add((d.year, d.month))
            x, y = P(c + 0.5, 7)
            lab += f'<text x="{x:.1f}" y="{y+th+16:.1f}" text-anchor="middle" font-family="{MONO}" font-size="10" fill="{GREY}">{d:%b}</text>'
    for r, nm in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        x, y = P(0, r + 0.5)
        lab += f'<text x="{x-8:.1f}" y="{y+3:.1f}" text-anchor="end" font-family="{MONO}" font-size="10" fill="{DARK}">{nm}</text>'
    callout = ""
    if peak_pos and peak[3] > 0:
        px, py = peak_pos
        callout = (f'<g>{fade_in(1.8)}<line x1="{px:.1f}" x2="{px:.1f}" y1="{py-2:.1f}" y2="{py-28:.1f}" stroke="{GREY}" stroke-dasharray="2 2"/>'
                   f'<circle cx="{px:.1f}" cy="{py-2:.1f}" r="2" fill="{WHITE}"/>'
                   f'<text x="{px:.1f}" y="{py-34:.1f}" text-anchor="middle" font-family="{MONO}" font-size="10" fill="{WHITE}">best day · {peak[3]} · {peak[2]:%d %b}</text></g>')
    total = sum(vals)
    active = sum(1 for x in vals if x > 0)
    return "".join(out) + lab + callout, total, active


def stats_card(s):
    H = 600
    cur, longest = streaks(s["days"], s["today"])
    total_all = sum(s["days"].values())
    cty, total_y, active_y = city(s["days"], s["today"])
    legend = "".join(f'<rect x="{W-36-5*16+i*16}" y="{386}" width="11" height="11" rx="2.5" fill="{c}"/>'
                     for i, c in enumerate([EMPTY_TOP] + GH_LEVELS))
    items = [("CONTRIBUTIONS", f"{total_all:,}", "all time", SKY),
             ("CURRENT STREAK", f"{cur}", "days", MINT),
             ("LONGEST STREAK", f"{longest}", "days", AMBER),
             ("COMMITS", f"{s['commits']:,}", "all time", VIOLET),
             ("PULL REQUESTS", f"{s['prs']:,}", "raised", PINK),
             ("REPOSITORIES", f"{s['repos']:,}", f"{s['stars']} ★ earned", CORAL)]
    colw = (W - 72) / 6
    nums = ""
    for i, (k, v, sub, col) in enumerate(items):
        x = 36 + i * colw
        y = 440
        nums += (f'<g>{fade_in(0.5 + i*0.1)}'
                 f'<rect x="{x:.0f}" y="{y-8}" width="6" height="6" rx="1.5" fill="{col}"/>'
                 f'<text x="{x+11:.0f}" y="{y-2}" font-family="{MONO}" font-size="9.5" letter-spacing="1" fill="{DARK}">{k}</text>'
                 f'<text x="{x-1:.0f}" y="{y+34}" font-family="{SANS}" font-size="32" font-weight="300" letter-spacing="-1" fill="{col}">{v}</text>'
                 f'<text x="{x:.0f}" y="{y+52}" font-family="{MONO}" font-size="10" fill="{GREY}">{esc(sub)}</text></g>')
    allt = sum(v for _, v, _ in s["langs"]) or 1
    langs = [l for l in s["langs"] if l[1] / allt >= 0.01][:6]
    lt = sum(v for _, v, _ in langs) or 1
    bx, bw, by = 36, W - 72, 534
    bar, leg, x = "", "", bx
    for i, (n, v, col) in enumerate(langs):
        w = bw * v / lt
        bar += f'<rect x="{x:.1f}" y="{by}" width="{max(0, w-3):.1f}" height="5" rx="2.5" fill="{col}"/>'
        nm = n if len(n) <= 11 else n[:10] + "…"
        lx = bx + i * bw / 6
        leg += (f'<rect x="{lx:.1f}" y="{by+20}" width="8" height="8" rx="2" fill="{col}"/>'
                f'<text x="{lx+14:.1f}" y="{by+28}" font-family="{MONO}" font-size="11" fill="{WHITE}">{esc(nm)} '
                f'<tspan fill="{DARK}">{100*v/lt:.0f}%</tspan></text>')
        x += w
    return f"""{svg_open(W, H, f"{USER} GitHub stats: {total_y} contributions in the last year, {cur}-day current streak, {s['commits']} commits")}
{defs_common(W, H, SKY, MINT)}
<defs><clipPath id="clip"><rect width="{W}" height="{H}" rx="16"/></clipPath>
<filter id="shadow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>
<radialGradient id="lamp" cx="0.5" cy="0.15" r="0.7"><stop offset="0" stop-color="#ffffff" stop-opacity="0.05"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></radialGradient></defs>
{card(W, H, beam_dur=13)}
<g clip-path="url(#clip)"><rect width="{W}" height="400" fill="url(#lamp)"/>{glow_blob(420, 250, 160, "#26a641", 0.06, 60, 20)}</g>
{head("~/stats --live", SKY, f"synced {s['today']:%d %b %Y}")}
<text x="36" y="72" font-family="{SANS}" font-size="15" fill="{WHITE}">{total_y:,} contributions in the last year<tspan fill="{GREY}"> · {active_y} active days</tspan></text>
{cty}
<text x="{W-36-5*16-8}" y="395" text-anchor="end" font-family="{MONO}" font-size="10" fill="{DARK}">less</text>
{legend}
<text x="{W-30}" y="395" font-family="{MONO}" font-size="10" fill="{DARK}">more</text>
<line x1="36" x2="{W-36}" y1="412" y2="412" stroke="{HAIR}"/>
{nums}
<line x1="36" x2="{W-36}" y1="508" y2="508" stroke="{HAIR}"/>
<text x="{bx}" y="{by-8}" font-family="{MONO}" font-size="10" letter-spacing="1.5" fill="{DARK}">LANGUAGES</text>
<g>{fade_in(0.8, 0.8)}{bar}</g>
{leg}
</svg>"""


# ============================================================ rhythm (weekday + months)
def rhythm_card(s):
    H = 330
    days, today = s["days"], s["today"]
    since = today - dt.timedelta(days=364)
    recent = {dt.date.fromisoformat(k): v for k, v in days.items() if dt.date.fromisoformat(k) >= since}
    wd = [0] * 7
    wn = [0] * 7
    for d, v in recent.items():
        i = (d.weekday() + 1) % 7  # Sun=0
        wd[i] += v
        wn[i] += 1
    avg = [wd[i] / wn[i] if wn[i] else 0 for i in range(7)]
    names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    months = []
    m = dt.date(today.year, today.month, 1)
    for _ in range(12):
        tot = sum(v for d, v in recent.items() if d.year == m.year and d.month == m.month)
        months.append((m, tot))
        m = (m - dt.timedelta(days=1)).replace(day=1)
    months.reverse()
    active = sum(1 for v in recent.values() if v > 0)
    best_day = names[max(range(7), key=lambda i: avg[i])]
    best_m = max(months, key=lambda t: t[1])

    # weekday bars
    bx, by, bh, bw = 36, 236, 140, 40
    gap = (360 - 7 * bw) / 6
    mx = max(avg) or 1
    bars = ""
    for i in range(7):
        h = 4 + (bh - 4) * avg[i] / mx
        x = bx + i * (bw + gap)
        col = spectrum(i / 6)
        o, cl = rise(x + bw / 2, by, 0.2 + i * 0.07)
        bars += (f'{o}<rect x="{x:.1f}" y="{by-h:.1f}" width="{bw}" height="{h:.1f}" rx="6" fill="{col}" fill-opacity="0.85"/>'
                 f'<rect x="{x:.1f}" y="{by-h:.1f}" width="{bw}" height="3" rx="1.5" fill="#fff" opacity="0.35"/>{cl}'
                 f'<text x="{x+bw/2:.1f}" y="{by+20}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{GREY}">{names[i]}</text>'
                 f'<text x="{x+bw/2:.1f}" y="{by-h-8:.1f}" text-anchor="middle" font-family="{MONO}" font-size="10" fill="{WHITE}">{avg[i]:.1f}{fade_in(1.0)}</text>')
    # monthly bars
    mx2 = max(t for _, t in months) or 1
    mxs, mw = 466, 22
    mgap = (W - 36 - mxs - 12 * mw) / 11
    mbars = ""
    for i, (mm, tot) in enumerate(months):
        h = 3 + (bh - 3) * tot / mx2
        x = mxs + i * (mw + mgap)
        col = spectrum(i / 11, [SKY, VIOLET, PINK, CORAL, AMBER])
        o, cl = rise(x + mw / 2, by, 0.4 + i * 0.05)
        mbars += (f'{o}<rect x="{x:.1f}" y="{by-h:.1f}" width="{mw}" height="{h:.1f}" rx="4" fill="{col}" fill-opacity="0.85"><title>{mm:%b %Y}: {tot}</title></rect>{cl}'
                  f'<text x="{x+mw/2:.1f}" y="{by+20}" text-anchor="middle" font-family="{MONO}" font-size="10.5" fill="{GREY}">{mm.strftime("%b")[0]}</text>')
    facts = [(f"most active day", best_day, MINT), (f"busiest month", f"{best_m[0]:%b %Y} · {best_m[1]}", AMBER),
             (f"active days, last year", f"{active} / {len(recent)}", VIOLET)]
    fx = ""
    for i, (k, v, c) in enumerate(facts):
        x = 36 + i * (W - 72) / 3
        fx += (f'<circle cx="{x+4:.0f}" cy="{288}" r="3" fill="{c}"/>'
               f'<text x="{x+14:.0f}" y="292" font-family="{MONO}" font-size="10.5" fill="{DARK}">{k} </text>'
               f'<text x="{x+14:.0f}" y="310" font-family="{MONO}" font-size="12.5" fill="{WHITE}">{esc(v)}</text>')
    return f"""{svg_open(W, H, f"Rhythm: most active on {best_day}; busiest month {best_m[0]:%B %Y}")}
{defs_common(W, H, MINT, PINK)}
{card(W, H, beam_dur=11)}
{head("~/rhythm", PINK, "last 12 months")}
<text x="36" y="76" font-family="{MONO}" font-size="10" letter-spacing="1.5" fill="{DARK}">AVG CONTRIBUTIONS BY WEEKDAY</text>
<text x="{mxs}" y="76" font-family="{MONO}" font-size="10" letter-spacing="1.5" fill="{DARK}">CONTRIBUTIONS PER MONTH</text>
<line x1="{mxs-34}" x2="{mxs-34}" y1="66" y2="{by+24}" stroke="{HAIR}"/>
<line x1="36" x2="{bx+360}" y1="{by}" y2="{by}" stroke="{HAIR2}"/>
<line x1="{mxs}" x2="{W-36}" y1="{by}" y2="{by}" stroke="{HAIR2}"/>
{bars}
{mbars}
<line x1="36" x2="{W-36}" y1="266" y2="266" stroke="{HAIR}"/>
{fx}
</svg>"""


# ============================================================ project cards
def ago(iso):
    t = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    d = (dt.datetime.now(dt.timezone.utc) - t).days
    if d <= 0:
        return "today"
    if d == 1:
        return "yesterday"
    if d < 31:
        return f"{d}d ago"
    if d < 365:
        return f"{d // 30}mo ago"
    return f"{d // 365}y ago"


def project_card(p, i):
    w, H = 405, 160
    lang = (p.get("primaryLanguage") or {}) or {}
    col = lang.get("color") or SPECTRUM[i % len(SPECTRUM)]
    accent = SPECTRUM[i % len(SPECTRUM)]
    desc = p.get("description") or ""
    lines = wrap(desc, 50)
    if len(lines) > 2:
        lines = lines[:2]
        lines[1] = lines[1][:47].rstrip() + "…"
    name = p["name"] if len(p["name"]) <= 34 else p["name"][:33] + "…"
    owner = ((p.get("owner") or {}).get("login") or USER)
    contributed = owner.lower() != USER.lower()
    dl = "".join(f'<text x="28" y="{86 + k*20}" font-family="{SANS}" font-size="13" fill="{GREY}">{esc(l)}</text>' for k, l in enumerate(lines))
    meta = ""
    if lang.get("name"):
        meta += (f'<circle cx="32" cy="132" r="5" fill="{col}"/>'
                 f'<text x="44" y="136" font-family="{MONO}" font-size="11.5" fill="#bdbdbd">{esc(lang["name"])}</text>')
    mx = 44 + len(lang.get("name") or "") * 7.2 + 22 if lang.get("name") else 28
    if contributed:
        room = int((405 - mx - 24) / 7.0) - len("↳ contributed to ")
        owner = owner if len(owner) <= room else owner[:max(4, room - 1)] + "…"
        meta += (f'<text x="{mx:.0f}" y="136" font-family="{MONO}" font-size="11.5" fill="{VIOLET}">↳ <tspan fill="#bdbdbd">contributed to {esc(owner)}</tspan></text>')
    else:
        meta += (f'<text x="{mx:.0f}" y="136" font-family="{MONO}" font-size="11.5" fill="{AMBER}">★ <tspan fill="#bdbdbd">{p.get("stargazerCount", 0)}</tspan></text>')
    if p.get("pushedAt"):
        meta += (f'<text x="{w-26}" y="136" text-anchor="end" font-family="{MONO}" font-size="11" fill="{DARK}">'
                 f'<tspan fill="{MINT}">●</tspan> updated {ago(p["pushedAt"])}</text>')
    return f"""{svg_open(w, H, f"{p['name']}: {desc}")}
{defs_common(w, H, accent, col)}
<defs><clipPath id="clip"><rect width="{w}" height="{H}" rx="14"/></clipPath></defs>
{card(w, H, rx=14, beam_dur=8 + i)}
<g clip-path="url(#clip)"><circle cx="{w-40}" cy="20" r="70" fill="{accent}" opacity="0.10" filter="url(#blur)"/></g>
<rect x="28" y="0.5" width="40" height="2" fill="{accent}"/>
<g transform="translate(28,34)" fill="none" stroke="{accent}" stroke-width="1.4" stroke-linejoin="round">
  <path d="M1 2.5 A1.5 1.5 0 0 1 2.5 1 H13 V15 H2.5 A1.5 1.5 0 0 1 1 13.5 Z"/><path d="M1 13.5 A1.5 1.5 0 0 1 2.5 12 H13"/></g>
<text x="52" y="47" font-family="{MONO}" font-size="14" font-weight="600" fill="{WHITE}">{esc(name)}</text>
<text x="{w-26}" y="47" text-anchor="end" font-family="{MONO}" font-size="13" fill="{accent}">↗</text>
{dl}
{meta}
</svg>"""


def update_readme_projects(projects):
    if not os.path.exists(README):
        return
    s = open(README, encoding="utf-8").read()
    links = []
    for i, p in enumerate(projects, 1):
        links.append(f'<a href="{esc(p["url"])}"><img src="assets/proj_{i}.svg" width="49%" alt="{esc(p["name"])}" /></a>')
    body = "\n".join(links)
    new = re.sub(r"(<!--PROJECTS:START-->)(.*?)(<!--PROJECTS:END-->)", lambda m: f"{m.group(1)}\n{body}\n{m.group(3)}", s, flags=re.S)
    if new != s:
        open(README, "w", encoding="utf-8").write(new)
        print("README project links updated")


# ============================================================ fortune (rotating)
def qotd():
    H = 150
    per = 9.0
    T = per * len(FORTUNES)
    out = ""
    for i, (q, a, col) in enumerate(FORTUNES):
        s, e = i * per, (i + 1) * per
        out += (f'<text x="36" y="86" font-family="{SANS}" font-size="20" fill="{WHITE}" opacity="0">{esc(q)}'
                f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{s/T:.4f};{(s+0.4)/T:.4f};{(e-0.5)/T:.4f};{(e-0.1)/T:.4f};1" dur="{T}s" repeatCount="indefinite"/></text>')
        out += scramble(a, 58, 118, 15, col, T, start=1.6, step=0.035, frames=6, fdur=0.05, seed=3 + i,
                        window=(s, e - 0.5))
    dots = "".join(f'<circle cx="{W-36-(len(FORTUNES)-1-i)*14}" cy="118" r="3" fill="{c}" opacity="0.25">'
                   f'<animate attributeName="opacity" values="0.25;0.25;1;1;0.25;0.25" keyTimes="0;{i*per/T:.4f};{i*per/T+0.001:.4f};{(i+1)*per/T-0.001:.4f};{(i+1)*per/T:.4f};1" dur="{T}s" repeatCount="indefinite"/></circle>'
                   for i, (*_, c) in enumerate(FORTUNES))
    return f"""{svg_open(W, H, " · ".join(f"{q} {a}" for q, a, _ in FORTUNES))}
{defs_common(W, H, CORAL, AMBER)}
{card(W, H, beam=False)}
{head("~/fortune", CORAL, "a new one every few seconds")}
<text x="36" y="118" font-family="{MONO}" font-size="15" fill="{DARK}">→</text>
{out}
{dots}
</svg>"""


# ============================================================ achievements
def achievement(title, sub, kind, color):
    w, H = 405, 104
    if kind == "shark":
        icon = (f'<path d="M0 22 C10 22 14 6 26 0 C24 10 26 16 34 22 Z" fill="{color}" fill-opacity="0.15" stroke="{color}" stroke-width="1.6" stroke-linejoin="round"/>'
                f'<path d="M-4 28 Q8 24 20 28 T44 28" fill="none" stroke="{GREY}" stroke-width="1.2">'
                f'<animate attributeName="d" values="M-4 28 Q8 24 20 28 T44 28;M-4 28 Q8 32 20 28 T44 28;M-4 28 Q8 24 20 28 T44 28" dur="3s" repeatCount="indefinite"/></path>')
    else:
        icon = (f'<polygon points="20,0 38,10 38,30 20,40 2,30 2,10" fill="none" stroke="{color}" stroke-width="1.6"/>'
                f'<polygon points="20,10 29,15 29,25 20,30 11,25 11,15" fill="{color}" opacity="0.25">'
                f'<animate attributeName="opacity" values="0.1;0.5;0.1" dur="3s" repeatCount="indefinite"/></polygon>')
    return f"""{svg_open(w, H, title)}
{defs_common(w, H, color, WHITE)}
<defs><clipPath id="clip"><rect width="{w}" height="{H}" rx="16"/></clipPath></defs>
{card(w, H, beam_dur=7)}
<g clip-path="url(#clip)"><circle cx="50" cy="50" r="60" fill="{color}" opacity="0.10" filter="url(#blur)"/></g>
<g transform="translate(30,32)">{icon}</g>
<text x="96" y="46" font-family="{MONO}" font-size="12.5" font-weight="600" letter-spacing="2.5" fill="{color}">{esc(title)}</text>
<text x="96" y="68" font-family="{SANS}" font-size="13" fill="{GREY}">{esc(sub)}</text>
<text x="{w-28}" y="46" text-anchor="end" font-family="{MONO}" font-size="13" fill="{DARK}">↗</text>
</svg>"""


# ============================================================ connect + footer
def button(idx, name, color):
    w, H = 196, 52
    return f"""{svg_open(w, H, name)}
<rect x="0.5" y="0.5" width="{w-1}" height="{H-1}" rx="12" fill="{color}" fill-opacity="0.06" stroke="{color}" stroke-opacity="0.35"/>
<text x="18" y="31" font-family="{MONO}" font-size="10" fill="{color}" opacity="0.7">{idx}</text>
<text x="42" y="31.5" font-family="{MONO}" font-size="13" fill="{WHITE}">{esc(name)}</text>
<text x="{w-18}" y="31.5" text-anchor="end" font-family="{MONO}" font-size="13" fill="{color}">↗</text>
</svg>"""


def footer():
    H = 90
    stops = "".join(f'<stop offset="{i/(len(SPECTRUM)-1):.2f}" stop-color="{c}"/>' for i, c in enumerate(SPECTRUM))
    return f"""{svg_open(W, H, "Thanks for stopping by")}
<defs><linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.5" stop-color="#fff" stop-opacity="0.18"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="sp" x1="0" x2="1">{stops}</linearGradient>
<linearGradient id="pl" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.5" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<mask id="m"><rect y="19" width="160" height="3" fill="url(#pl)"><animate attributeName="x" values="-160;{W}" dur="5s" repeatCount="indefinite"/></rect></mask></defs>
<rect x="0" y="20" width="{W}" height="1" fill="url(#ln)"/>
<rect x="0" y="19.5" width="{W}" height="2" fill="url(#sp)" mask="url(#m)"/>
<text x="{W/2}" y="58" text-anchor="middle" font-family="{MONO}" font-size="11" letter-spacing="2" fill="{DARK}">THANKS FOR STOPPING BY <tspan fill="{VIOLET}">·</tspan> SAHITYA SINGH <tspan fill="{MINT}">·</tspan> {dt.date.today().year}</text>
</svg>"""


def placeholder(name, title, H=200, w=W):
    write(name, f"""{svg_open(w, H, title)}
{defs_common(w, H)}{card(w, H)}
<text x="28" y="46" font-family="{MONO}" font-size="11" fill="{MINT}">{esc(title)}</text>
<text x="{w/2}" y="{H/2+12}" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{GREY}">warming up… syncs on the next workflow run</text>
</svg>""")


# ============================================================ build
LABELS = [("about", "01", "About", "who i am", MINT), ("stack", "02", "Tech Arsenal", "what i use", SKY),
          ("projects", "03", "Projects", "latest first", VIOLET), ("stats", "04", "GitHub Stats", "synced daily", SKY),
          ("rhythm", "05", "Rhythm", "when i commit", PINK), ("snake", "06", "Snake", "eats my contributions", MINT),
          ("ach", "07", "Trophies & Badges", "earned", AMBER), ("qotd", "08", "Question of the Day", "", CORAL),
          ("connect", "09", "Connect", "", SKY)]


def build_static():
    write("boot.svg", boot())
    write("hero.svg", hero())
    write("helix.svg", helix())
    write("about.svg", about())
    write("stack.svg", stack())
    write("qotd.svg", qotd())
    write("footer.svg", footer())
    write("ach_pullshark.svg", achievement("PULL SHARK", "GitHub Achievement", "shark", SKY))
    write("ach_layer5.svg", achievement("FIRST DESIGN", "LAYER5 Badge", "hex", VIOLET))
    for i, (k, n, c) in enumerate([("email", "Email", CORAL), ("linkedin", "LinkedIn", SKY),
                                   ("instagram", "Instagram", PINK), ("github", "GitHub", MINT)], 1):
        write(f"btn_{k}.svg", button(f"0{i}", n, c))
    for k, i, t, tag, c in LABELS:
        write(f"label_{k}.svg", label(i, t, tag, c))


def build_live(s):
    write("stats.svg", stats_card(s))
    write("rhythm.svg", rhythm_card(s))
    for i, p in enumerate(s["projects"], 1):
        write(f"proj_{i}.svg", project_card(p, i - 1))
    update_readme_projects(s["projects"])


def main():
    os.makedirs(ASSETS, exist_ok=True)
    build_static()
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        for n, t in (("stats.svg", "~/stats --live"), ("rhythm.svg", "~/rhythm")):
            if not os.path.exists(os.path.join(ASSETS, n)):
                placeholder(n, t)
        for i in range(1, 7):
            if not os.path.exists(os.path.join(ASSETS, f"proj_{i}.svg")):
                placeholder(f"proj_{i}.svg", "~/projects", 160, 405)
        print("no GITHUB_TOKEN: live cards skipped")
        return
    try:
        s = fetch_stats(token)
    except (OSError, RuntimeError, ValueError) as e:  # network/API trouble: keep the last good cards
        print("stats fetch failed, keeping previous cards:", e, file=sys.stderr)
        return
    build_live(s)


if __name__ == "__main__":
    main()
