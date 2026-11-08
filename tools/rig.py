#!/usr/bin/env python3
"""
Generates the side-view illustration of the rig for the Trucking page -> src/_parts/rig.svg

Drawn from the reference photos in Drive/Shard (IMG_5595, 5596, 5599, 5600, 5601): a Freightliner Cascadia
(raised-roof 72-in sleeper) pulling a 53-ft reefer. Key facts taken from the photos:
  * tractor frame runs BEHIND the cab to the fifth wheel, which sits over the drive tandem
  * the trailer nose sits a short gap behind the sleeper
  * the refrigeration unit is bolted to the OUTSIDE of the trailer's front wall, in that gap, top flush with the roof
  * aerodynamic side skirts, landing gear forward of the skirts, tandem axles slid toward the rear
Every position below is in FEET (f = distance behind the steer-axle centre, h = height above ground).
Not branded: no carrier names or logos. Colours follow the RoadCodez palette.
Facing left, so the viewer sees the driver's (left) side.
"""
import math
from pathlib import Path

# ---------------- dimensions (ft) ----------------
GAP = 5.0            # sleeper back wall -> trailer nose (Matt: ~5 ft). 1.5 ft of it is the cab fairings, leaving ~3.5 ft visible
FAIRING = 1.5        # side/roof extenders that stick out behind the sleeper
DOOR_REAR = 6.35     # rear edge of the door; sleeper = CAB_BACK - DOOR_REAR = ~6 ft (72-inch sleeper)
CAB_BACK = 12.3      # steer-axle centre -> back of sleeper
REEFER_D = 2.2       # how far the reefer unit sticks out in front of the trailer's front wall
NOSE = CAB_BACK + GAP            # trailer front wall
TRL = 53.0
REAR = NOSE + TRL
KINGPIN = NOSE + 3.0             # 3 ft behind the nose
WHEELBASE = KINGPIN              # fifth wheel sits ~over the drive-tandem centre
DRIVE = (WHEELBASE - 2.1, WHEELBASE + 2.1)
TAND = (NOSE + 43.0, NOSE + 47.0)
TIRE_R = 1.7
TOP = 13.5
FLOOR = 4.0

S = 15.0                  # px per foot
GX, GY = 100.0, 272.0     # px of steer-axle centre line / ground
VBW = math.ceil(GX + S * REAR + 120)
VBH = 372

def X(f): return GX + S * f
def Y(h): return GY - S * h
def P(f, h): return f"{X(f):.1f},{Y(h):.1f}"

def path(*segs):
    out = []
    for s in segs:
        c, *a = s
        if c == "Z": out.append("Z"); continue
        pts = " ".join(P(a[i], a[i + 1]) for i in range(0, len(a), 2))
        out.append(f"{c}{pts}")
    return " ".join(out)

def rect(f0, h0, f1, h1, rx=0, **kw):
    attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<rect x="{X(f0):.1f}" y="{Y(h1):.1f}" width="{S*(f1-f0):.1f}" height="{S*(h1-h0):.1f}" rx="{rx}" {attrs}/>'

def line(f0, h0, f1, h1, **kw):
    attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<line x1="{X(f0):.1f}" y1="{Y(h0):.1f}" x2="{X(f1):.1f}" y2="{Y(h1):.1f}" {attrs}/>'

def circ(f, h, r_ft, **kw):
    attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<circle cx="{X(f):.1f}" cy="{Y(h):.1f}" r="{S*r_ft:.1f}" {attrs}/>'

def coil(f0, h0, f1, h1, sag, amp, turns, color):
    n = 120; pts = []
    x0, y0, x1, y1 = X(f0), Y(h0), X(f1), Y(h1)
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    for i in range(n + 1):
        u = i / n
        bx, by = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u + S * sag * math.sin(math.pi * u)
        w = amp * math.sin(2 * math.pi * turns * u)
        pts.append(f"{bx + nx * w:.1f},{by + ny * w:.1f}")
    return f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"/>'

def wheel(f, accent, ring):
    cx, cy = X(f), Y(TIRE_R)
    r = S * TIRE_R
    g = []
    g.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="url(#tire)" stroke="#000" stroke-width="1.2"/>')
    g.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r*0.93:.1f}" fill="none" stroke="#2a303b" stroke-width="1.1"/>')
    # tread notches
    for i in range(36):
        a = i * math.pi / 18
        g.append(f'<line x1="{cx+math.cos(a)*r*0.97:.1f}" y1="{cy+math.sin(a)*r*0.97:.1f}" x2="{cx+math.cos(a)*r:.1f}" y2="{cy+math.sin(a)*r:.1f}" stroke="#14171d" stroke-width="1.6"/>')
    g.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r*0.62:.1f}" fill="url(#rim)" stroke="#59616f" stroke-width="1"/>')
    g.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r*0.5:.1f}" fill="none" stroke="#7d8796" stroke-width=".8"/>')
    for i in range(10):   # lug nuts
        a = i * math.pi / 5
        g.append(f'<circle cx="{cx+math.cos(a)*r*0.36:.1f}" cy="{cy+math.sin(a)*r*0.36:.1f}" r="1.5" fill="#39404c"/>')
    g.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r*0.24:.1f}" fill="url(#rim)" stroke="{ring}" stroke-width="2"/>')
    g.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r*0.11:.1f}" fill="{accent}"/>')
    # sidewall highlight
    g.append(f'<path d="M{cx-r*0.78:.1f} {cy-r*0.3:.1f} A{r*0.84:.1f} {r*0.84:.1f} 0 0 1 {cx+r*0.1:.1f} {cy-r*0.83:.1f}" fill="none" stroke="rgba(255,255,255,.14)" stroke-width="2" stroke-linecap="round"/>')
    return "".join(g)


def band(f0, h0, f1, h1, t0, t1, notch=None, n=28):
    """Tapered streak from (f0,h0) to (f1,h1), thickness t0->t1. Returns (upper_half, lower_half) polygons (two-tone decal).
       notch=(pos 0..1, depth ft, width ft) cuts a V into the LOWER edge."""
    Ln = math.hypot(f1 - f0, h1 - h0); ux, uy = (f1 - f0) / Ln, (h1 - h0) / Ln; nx, ny = -uy, ux
    cen, up, lo = [], [], []
    for i in range(n + 1):
        u = i / n; t = t0 + (t1 - t0) * u
        cx, cy = f0 + (f1 - f0) * u, h0 + (h1 - h0) * u
        d = 0.0
        if notch:
            pos, depth, w = notch; half = w / Ln / 2
            if abs(u - pos) < half: d = depth * (1 - abs(u - pos) / half)
        cen.append((cx, cy)); up.append((cx + nx * t / 2, cy + ny * t / 2)); lo.append((cx - nx * max(0.0, t / 2 - d), cy - ny * max(0.0, t / 2 - d)))
    return up + cen[::-1], cen + lo[::-1]

def poly(points, **kw):
    attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<polygon points="{" ".join(P(f, h) for f, h in points)}" {attrs}/>'

def build():
    o = []
    A = o.append
    A(f'<svg class="rig-art" viewBox="0 0 {VBW} {VBH}" role="img" aria-labelledby="rigT rigD" xmlns="http://www.w3.org/2000/svg">')
    A('<title id="rigT">Illustration of the rig: a Freightliner Cascadia tractor and 53-foot refrigerated trailer</title>')
    A('<desc id="rigD">Side view. The tractor frame runs behind the sleeper cab to the fifth wheel. Fairings come off the back of the cab, and a gap of about five feet in all separates the back of the cab from the trailer, and the refrigeration unit is mounted on the outside of the trailer front wall inside that gap. Steer axle, two drive axles and two trailer axles are marked.</desc>')

    # ---------------- defs ----------------
    A('''<defs>
<linearGradient id="cabfill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6a2c64"/><stop offset=".13" stop-color="#4a1b44"/><stop offset=".55" stop-color="#260a24"/><stop offset="1" stop-color="#0f0410"/></linearGradient>
<linearGradient id="skirtblk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#241b2b"/><stop offset=".25" stop-color="#120c16"/><stop offset="1" stop-color="#040306"/></linearGradient>
<linearGradient id="glass2" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#34274a"/><stop offset=".5" stop-color="#150f20"/><stop offset="1" stop-color="#08060c"/></linearGradient>
<linearGradient id="extfill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a1236"/><stop offset="1" stop-color="#10050f"/></linearGradient>
<linearGradient id="goldfill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff0a0"/><stop offset=".5" stop-color="#f3c62d"/><stop offset="1" stop-color="#b98a16"/></linearGradient>
<linearGradient id="valance" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c3cad6"/><stop offset=".5" stop-color="#8d97a6"/><stop offset="1" stop-color="#4b5361"/></linearGradient>
<linearGradient id="gloss" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".22"/><stop offset=".5" stop-color="#fff" stop-opacity=".03"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#27384f"/><stop offset=".55" stop-color="#0d1622"/><stop offset="1" stop-color="#070b11"/></linearGradient>
<linearGradient id="trl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4f7fb"/><stop offset=".5" stop-color="#e0e5ed"/><stop offset="1" stop-color="#b4bcc9"/></linearGradient>
<linearGradient id="skirt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a414d"/><stop offset="1" stop-color="#14181f"/></linearGradient>
<linearGradient id="steel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e9edf3"/><stop offset=".45" stop-color="#9aa3b1"/><stop offset="1" stop-color="#4b5361"/></linearGradient>
<linearGradient id="gold" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7a4d06"/><stop offset=".35" stop-color="#f4a81d"/><stop offset=".7" stop-color="#ffd36b"/><stop offset="1" stop-color="#f4a81d" stop-opacity="0"/></linearGradient>
<linearGradient id="unit" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#cfd6e1"/><stop offset=".5" stop-color="#f6f8fb"/><stop offset="1" stop-color="#bcc4d1"/></linearGradient>
<linearGradient id="louver" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3b424e"/><stop offset="1" stop-color="#1b1f27"/></linearGradient>
<radialGradient id="tire" cx=".4" cy=".35" r=".8"><stop offset="0" stop-color="#2b303a"/><stop offset="1" stop-color="#07080b"/></radialGradient>
<radialGradient id="rim" cx=".38" cy=".32" r=".9"><stop offset="0" stop-color="#f6f8fb"/><stop offset=".55" stop-color="#a9b2c0"/><stop offset="1" stop-color="#5a6270"/></radialGradient>
<linearGradient id="road" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#232a35"/><stop offset="1" stop-color="#232a35" stop-opacity="0"/></linearGradient>
<radialGradient id="lamp" cx=".4" cy=".4" r=".7"><stop offset="0" stop-color="#fff1c2"/><stop offset="1" stop-color="#f4a81d"/></radialGradient>
<pattern id="ribs" width="10" height="9.6" patternUnits="userSpaceOnUse"><line x1="0" y1="9" x2="10" y2="9" stroke="#9aa3b1" stroke-opacity=".55" stroke-width="1"/><line x1="0" y1="8" x2="10" y2="8" stroke="#fff" stroke-opacity=".5" stroke-width=".8"/></pattern>
<filter id="soft" x="-10%" y="-200%" width="120%" height="500%"><feGaussianBlur stdDeviation="4"/></filter>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.2"/></filter>
</defs>''')

    # ---------------- ground ----------------
    A(f'<rect x="0" y="{GY:.1f}" width="{VBW}" height="60" fill="url(#road)"/>')
    A(f'<rect x="{X(-3.4):.1f}" y="{GY-3:.1f}" width="{S*(REAR+3.9):.1f}" height="12" rx="6" fill="#000" opacity=".6" filter="url(#soft)"/>')
    A(f'<line x1="14" y1="{GY:.1f}" x2="{VBW-14}" y2="{GY:.1f}" stroke="#3a4252" stroke-width="1.5"/>')

    # ---------------- trailer undercarriage (behind everything) ----------------
    A('<g id="undercarriage">')
    A(rect(NOSE + 1.0, 3.15, REAR - 2.5, FLOOR + 0.02, fill="#0b0d12", stroke="#2b323d", stroke_width="1"))                       # main beams
    for k in range(0, 14):                                                                                                        # cross-members
        f = NOSE + 3.2 + k * 3.35
        if f < REAR - 3: A(line(f, 3.2, f, FLOOR, stroke="#2b323d", stroke_width="1"))
    A(rect(TAND[0] - 2.5, 1.9, TAND[1] + 2.4, 3.3, rx=2, fill="#0e1117", stroke="#343c49", stroke_width="1.2"))                  # slider sub-frame
    A(rect(TAND[0], 1.55, TAND[1], 2.05, fill="#161a22", stroke="#343c49"))                                                      # axle beam
    # landing gear (legs + foot + crank)
    lg = NOSE + 10.2
    A(rect(lg - .2, 0.55, lg + .25, FLOOR, fill="url(#steel)", stroke="#2a303b", stroke_width="1.2"))
    A(rect(lg - .75, 0.0, lg + .8, 0.6, rx=1.5, fill="#1b2029", stroke="#59616f", stroke_width="1.2"))
    A(rect(lg - .45, 0.6, lg + .5, 1.0, fill="#2a303b"))
    A(circ(lg + .02, 2.55, 0.28, fill="#2a303b", stroke="#9aa3b1", stroke_width="1.2"))
    A(line(lg + .02, 2.55, lg + 1.25, 2.1, stroke="#9aa3b1", stroke_width="2.2", stroke_linecap="round"))
    A(circ(lg + 1.3, 2.08, 0.16, fill="#d3d9e2"))
    A(rect(lg - 2.2, 3.2, lg + 2.4, FLOOR, fill="#12151b", stroke="#2b323d"))                                                    # cross-tube
    A('</g>')

    # ---------------- trailer box ----------------
    A('<g id="trailer">')
    A(f'<path d="{path(("M", NOSE, TOP - .25), ("Q", NOSE, TOP, NOSE + .25, TOP), ("L", REAR - .25, TOP), ("Q", REAR, TOP, REAR, TOP - .25), ("L", REAR, FLOOR), ("L", NOSE, FLOOR), ("Z",))}" fill="url(#trl)" stroke="#7d8796" stroke-width="1.6" stroke-linejoin="round"/>')
    A(f'<path d="{path(("M", NOSE, TOP - .25), ("Q", NOSE, TOP, NOSE + .25, TOP), ("L", REAR - .25, TOP), ("Q", REAR, TOP, REAR, TOP - .25), ("L", REAR, FLOOR), ("L", NOSE, FLOOR), ("Z",))}" fill="url(#ribs)"/>')
    # sheen
    A(f'<path d="{path(("M", NOSE + 6, TOP), ("L", NOSE + 17, TOP), ("L", NOSE + 9.5, FLOOR), ("L", NOSE - .0 + 0, FLOOR), ("L", NOSE, TOP - .3), ("Z",))}" fill="url(#gloss)" opacity=".55"/>')
    A(f'<path d="{path(("M", NOSE + 28, TOP), ("L", NOSE + 36, TOP), ("L", NOSE + 28.5, FLOOR), ("L", NOSE + 22, FLOOR), ("Z",))}" fill="url(#gloss)" opacity=".4"/>')
    # "PRIME inc." decal: heavy black block capitals with a down-left 3D extrusion, lowercase "inc." (as on the real trailers)
    px0, base = X(NOSE + 22.4), Y(9.75)
    ff = 'font-family="\'Arial Black\',\'Helvetica Neue\',Arial,sans-serif" font-weight="900"'
    for k in range(5, 0, -1):
        A(f'<text x="{px0 - k*0.7:.1f}" y="{base + k*0.7:.1f}" {ff} font-size="47" textLength="{S*8.5:.0f}" lengthAdjust="spacingAndGlyphs" fill="#6b7482">PRIME</text>')
        A(f'<text x="{px0 + S*9.0 - k*0.7:.1f}" y="{base + k*0.7:.1f}" {ff} font-size="33" textLength="{S*3.7:.0f}" lengthAdjust="spacingAndGlyphs" fill="#6b7482">inc.</text>')
    A(f'<text x="{px0:.1f}" y="{base:.1f}" {ff} font-size="47" textLength="{S*8.5:.0f}" lengthAdjust="spacingAndGlyphs" fill="#0a0b0e">PRIME</text>')
    A(f'<text x="{px0 + S*9.0:.1f}" y="{base:.1f}" {ff} font-size="33" textLength="{S*3.7:.0f}" lengthAdjust="spacingAndGlyphs" fill="#0a0b0e">inc.</text>')
    # green "eco" badge, low and forward on the trailer side
    A(f'<ellipse cx="{X(NOSE + 12.0):.1f}" cy="{Y(5.55):.1f}" rx="{S*1.9:.1f}" ry="{S*0.42:.1f}" fill="#7cc244" stroke="#2d5a12" stroke-width="1.2"/>')
    A(f'<text x="{X(NOSE + 12.0):.1f}" y="{Y(5.55)+4.2:.1f}" font-family="Arial,sans-serif" font-weight="800" font-style="italic" font-size="12.5" text-anchor="middle" fill="#173508">eco</text>')
    A(rect(NOSE, TOP - .38, REAR, TOP, rx=2, fill="#c3cad6", stroke="#7d8796", stroke_width="1"))                                   # roof rail
    A(rect(NOSE, FLOOR, REAR, FLOOR + .55, fill="#9aa3b1", stroke="#59616f", stroke_width="1"))                                    # bottom rail
    # DOT conspicuity tape (red/white)
    x = NOSE + .6
    while x < REAR - 1:
        A(rect(x, FLOOR + .16, x + .6, FLOOR + .36, fill="#d8362b")); A(rect(x + .6, FLOOR + .16, x + 1.2, FLOOR + .36, fill="#f4f6fa")); x += 1.2
    # front post & rear frame / doors
    A(rect(NOSE, FLOOR, NOSE + .55, TOP, fill="#aeb6c3", stroke="#59616f", stroke_width="1"))
    A(rect(REAR - 1.0, FLOOR, REAR, TOP, fill="#8d97a6", stroke="#3a4250", stroke_width="1.2"))
    for hh in (5.6, 8.4, 11.2, 12.9): A(rect(REAR - 1.0, hh - .12, REAR - .35, hh + .12, fill="#2b323d"))                         # door hinges
    A(line(REAR - .72, FLOOR + .1, REAR - .72, TOP - .1, stroke="#3a4250", stroke_width="1"))
    # markers
    for f in (NOSE + .9, NOSE + 26.5, REAR - .7):
        A(circ(f, FLOOR + .8, .2, fill="url(#lamp)", stroke="#8a5a05", stroke_width="1"))
    A(circ(REAR - .45, FLOOR - 0.0 + 0.8 + 0.0, 0.0, fill="none"))
    A('</g>')

    # side skirts
    a, b = NOSE + 11.4, NOSE + 38.2
    A(f'<path d="{path(("M", a, FLOOR), ("L", b, FLOOR), ("L", b - .6, 1.35), ("L", a + .5, 1.35), ("Z",))}" fill="url(#skirt)" stroke="#4b5361" stroke-width="1.2"/>')
    A(line(a + .6, 2.8, b - .8, 2.8, stroke="#59616f", stroke_width="1", stroke_opacity=".6"))
    A(line(a + .5, 1.45, b - .6, 1.45, stroke="#9aa3b1", stroke_width="1.4", stroke_opacity=".55"))
    for f in (a + 6.6, a + 13.2, a + 19.8): A(line(f, FLOOR, f - .1, 1.4, stroke="#0b0d12", stroke_width="1.2"))

    # ---------------- tractor chassis ----------------
    A('<g id="chassis">')
    A(rect(-1.2, 2.75, WHEELBASE + 3.4, 3.55, fill="#0b0d12", stroke="#343c49", stroke_width="1.2"))                               # frame rail
    A(rect(-0.6, 2.9, WHEELBASE + 3.2, 3.0, fill="#1a1f28"))
    # air tanks behind cab
    for k, f0 in enumerate((CAB_BACK + .35, CAB_BACK + 1.05)):
        pass
    # (the APU is strapped to the PASSENGER-side frame just behind the fairings, so it is not visible from this driver's-side view)
    # fifth wheel
    fw0, fw1 = KINGPIN - 1.55, KINGPIN + 1.5
    A(f'<path d="{path(("M", fw0, 3.62), ("L", fw1, 3.62), ("L", fw1 - .25, 3.95), ("L", fw0 + .5, 3.95), ("Z",))}" fill="url(#steel)" stroke="#2a303b" stroke-width="1.4"/>')
    A(rect(fw0 + .9, 3.0, fw1 - .9, 3.62, fill="#2a303b", stroke="#59616f"))
    A(rect(KINGPIN - 1.25, 3.93, KINGPIN + 1.2, FLOOR + .04, fill="#0b0d12", stroke="#59616f", stroke_width="1"))                 # trailer apron plate
    A(rect(KINGPIN - .17, FLOOR - .28, KINGPIN + .17, FLOOR + .05, fill="#d3d9e2", stroke="#2a303b"))                              # kingpin
    A('</g>')

    # reefer unit on the trailer's OUTSIDE front wall
    A('<g id="reefer">')
    u0, u1, uh0, uh1 = NOSE - REEFER_D, NOSE, 6.05, TOP - .25
    A(f'<path d="{path(("M", u1, uh1), ("L", u0 + .5, uh1), ("Q", u0, uh1, u0, uh1 - .5), ("L", u0, uh0 + .4), ("Q", u0, uh0, u0 + .4, uh0), ("L", u1, uh0), ("Z",))}" fill="url(#unit)" stroke="#59616f" stroke-width="1.5" stroke-linejoin="round"/>')
    # condenser grille (top)
    A(rect(u0 + .22, uh1 - 2.6, u1 - .12, uh1 - .22, rx=2, fill="url(#louver)", stroke="#59616f", stroke_width="1"))
    for k in range(11): A(line(u0 + .32, uh1 - .4 - k * .2, u1 - .22, uh1 - .4 - k * .2, stroke="#7d8796", stroke_width=".9", stroke_opacity=".7"))
    # access panel + control box + latch
    A(rect(u0 + .2, uh0 + .3, u1 - .12, uh1 - 2.85, rx=2, fill="#eef1f6", stroke="#8d97a6", stroke_width="1.1"))
    A(rect(u0 + .45, uh0 + 1.6, u1 - .55, uh0 + 2.45, rx=2, fill="#1a1f28", stroke="#59616f", stroke_width="1"))
    A(rect(u0 + .6, uh0 + 1.78, u1 - .7, uh0 + 2.0, fill="#4ee08a", opacity=".85"))
    A(rect(u0 + .6, uh0 + 2.1, u1 - .7, uh0 + 2.28, fill="#7d8796"))
    A(rect(u1 - .72, uh0 + .55, u1 - .5, uh0 + 1.25, rx=2, fill="#59616f"))
    A(line(u0 + .2, uh1 - 2.85, u1 - .12, uh1 - 2.85, stroke="#8d97a6", stroke_width="1.3"))
    # mounting brackets to the trailer wall
    A(rect(u1 - .08, uh0 + .6, u1 + .12, uh0 + 1.0, fill="#59616f")); A(rect(u1 - .08, uh1 - 3.2, u1 + .12, uh1 - 2.8, fill="#59616f"))
    A('</g>')

    # glad-hands + air lines (red = emergency, blue = service) in the gap
    A(rect(NOSE - .22, 4.75, NOSE, 5.45, rx=1, fill="#59616f"))
    A(circ(NOSE - .12, 4.82, .13, fill="#d8362b")); A(circ(NOSE - .12, 5.3, .13, fill="#3d8bff"))
    A(coil(CAB_BACK + FAIRING - .05, 5.75, NOSE - .22, 4.82, .5, 1.9, 6.5, "#d8362b"))
    A(coil(CAB_BACK + FAIRING - .05, 5.45, NOSE - .22, 5.3, .38, 1.9, 6.5, "#3d8bff"))

    # ---------------- drive tires + fenders ----------------
    for f in DRIVE:
        A(wheel(f, "#f4a81d", "#7a5208"))
    A(f'<path d="{path(("M", DRIVE[0] - 2.2, 1.9), ("Q", DRIVE[0] - 2.1, 3.75, DRIVE[0], 3.75), ("L", DRIVE[1], 3.75), ("Q", DRIVE[1] + 2.1, 3.75, DRIVE[1] + 2.2, 1.9), ("L", DRIVE[1] + 1.9, 1.9), ("Q", DRIVE[1] + 1.9, 3.45, DRIVE[1], 3.45), ("L", DRIVE[0], 3.45), ("Q", DRIVE[0] - 1.9, 3.45, DRIVE[0] - 1.9, 1.9), ("Z",))}" fill="#14181f" stroke="#59616f" stroke-width="1.4"/>')
    A(rect(DRIVE[1] + 2.0, 0.55, DRIVE[1] + 2.22, 2.2, fill="#14181f", stroke="#3a4250"))                                         # mud flap
    A(line(DRIVE[0] - 1.4, 3.67, DRIVE[1] + 1.4, 3.67, stroke="#e9edf3", stroke_width="1", stroke_opacity=".25"))

    # ---------------- cab (new-generation Cascadia, Gold on Purple; front end redrawn from the close-ups) ----------------
    A('<g id="cab">')
    FB = CAB_BACK + FAIRING                      # rear edge of the fairings
    # body silhouette: raked fascia -> hood -> raked windshield -> header -> domed sleeper roof (full trailer height) -> fairings -> side fairing -> wheel opening
    cab_d = path(("M", -3.38, 1.5), ("L", -3.4, 2.95), ("L", -3.0, 3.05), ("L", -2.8, 4.7), ("Q", -2.76, 4.95, -2.45, 5.0), ("Q", -0.9, 5.2, 1.2, 5.85), ("L", 3.7, 8.95),
                 ("Q", 3.85, 9.15, 4.15, 9.2), ("C", 5.0, 10.2, 6.4, 13.35, 9.0, TOP - .02), ("L", FB - .3, TOP - .02), ("Q", FB, TOP - .02, FB, TOP - .3),
                 ("L", FB, 4.5), ("L", CAB_BACK, 4.0), ("L", CAB_BACK, 1.2), ("L", CAB_BACK - .18, 1.0), ("L", 2.8, 1.0), ("L", 2.4, 1.7), ("L", -2.4, 1.7), ("Z",))
    A(f'<path d="{cab_d}" fill="url(#cabfill)" stroke="#16071a" stroke-width="2" stroke-linejoin="round"/>')
    A(f'<path d="{cab_d}" fill="url(#gloss)"/>')
    # rim light along the top contour
    A(f'<path d="{path(("M", -2.7, 4.78), ("Q", -2.66, 5.05, -2.4, 5.08), ("Q", -0.9, 5.28, 1.2, 5.93), ("L", 3.7, 9.03), ("Q", 3.85, 9.23, 4.15, 9.28), ("C", 5.0, 10.28, 6.4, 13.43, 9.0, TOP - .1), ("L", FB - .3, TOP - .1))}" fill="none" stroke="#e7b6e1" stroke-opacity=".38" stroke-width="1.3" stroke-linecap="round"/>')
    # cab fairings: attach to the back of the sleeper, read as ~1.5 ft more sleeper (same colour, flush with the roof)
    fr = path(("M", CAB_BACK, TOP - .02), ("L", FB - .3, TOP - .02), ("Q", FB, TOP - .02, FB, TOP - .3), ("L", FB, 4.5), ("L", CAB_BACK, 4.0), ("Z",))
    A(f'<path d="{fr}" fill="#000" fill-opacity=".16"/>')
    A(line(CAB_BACK, TOP - .1, CAB_BACK, 4.0, stroke="#0b0310", stroke_width="1.3"))
    A(line(CAB_BACK + .08, TOP - .1, CAB_BACK + .08, 4.05, stroke="#e7b6e1", stroke_opacity=".22", stroke_width="1"))
    A(line(FB - .02, TOP - .35, FB - .02, 4.55, stroke="#e7b6e1", stroke_opacity=".3", stroke_width="1.1"))
    # wheel opening + steer wheel
    A(f'<path d="M{X(-2.1):.1f} {Y(1.7):.1f} A{S*2.1:.1f} {S*2.1:.1f} 0 0 1 {X(2.1):.1f} {Y(1.7):.1f} L{X(2.1):.1f} {Y(1.7):.1f} L{X(-2.1):.1f} {Y(1.7):.1f}Z" fill="#050608" stroke="#59616f" stroke-width="1.6"/>')
    A(f'<path d="M{X(-2.38):.1f} {Y(1.7):.1f} A{S*2.38:.1f} {S*2.38:.1f} 0 0 1 {X(2.38):.1f} {Y(1.7):.1f}" fill="none" stroke="#e7b6e1" stroke-opacity=".3" stroke-width="1.5"/>')
    A(wheel(0.0, "#d3d9e2", "#9aa3b1"))

    # ---- FRONT END ----
    # bumper: painted gray upper part + BLACK plastic lower part (chin) that reaches nearly to the ground
    A(f'<g id="bumper"><path d="{path(("M", -3.5, 0.95), ("L", -3.56, 1.8), ("Q", -3.56, 1.95, -3.4, 1.97), ("L", -1.95, 1.98), ("Q", -1.62, 1.95, -1.6, 1.5), ("L", -1.62, 1.12), ("Q", -1.64, 0.96, -1.85, 0.95), ("Z",))}" fill="url(#skirtblk)" stroke="#6b6577" stroke-width="1.3" stroke-linejoin="round"/>')
    A(f'<path d="{path(("M", -3.42, 1.85), ("L", -3.44, 2.8), ("Q", -3.44, 3.0, -3.25, 3.04), ("L", -1.95, 3.07), ("Q", -1.62, 3.05, -1.6, 2.65), ("L", -1.58, 1.9), ("Z",))}" fill="url(#valance)" stroke="#2d3340" stroke-width="1.4" stroke-linejoin="round"/></g>')
    A(line(-3.3, 3.0, -1.9, 3.03, stroke="#fff", stroke_opacity=".55", stroke_width="1.3"))
    A(rect(-3.0, 1.3, -2.1, 1.5, rx=1, fill="#0a0810", stroke="#3a3344", stroke_width="1"))
    # raked grille: chrome surround + three slats on the fascia
    A(f'<path d="{path(("M", -3.04, 3.12), ("L", -2.82, 4.68), ("L", -2.96, 4.7), ("L", -3.2, 3.15), ("Z",))}" fill="url(#steel)" stroke="#39404c" stroke-width="1"/>')
    for hh in (3.55, 3.98, 4.4):
        A(line(-3.18 + (hh - 3.15) * .125, hh, -2.92 + (hh - 3.15) * .125, hh + .02, stroke="#1f242d", stroke_width="1.6"))
    # headlamp: long wraparound lens with an amber end + side marker below
    A(f'<path d="{path(("M", -3.04, 3.38), ("Q", -3.1, 4.05, -2.65, 4.2), ("L", -1.5, 4.02), ("L", -1.45, 3.42), ("L", -2.5, 3.3), ("Z",))}" fill="#eef2f7" stroke="#59616f" stroke-width="1.1" stroke-linejoin="round"/>')
    A(f'<path d="{path(("M", -2.0, 3.45), ("L", -1.5, 3.44), ("L", -1.52, 4.0), ("L", -2.05, 4.1), ("Z",))}" fill="#f2a31a" opacity=".85"/>')
    A(f'<path d="{path(("M", -2.9, 3.62), ("Q", -2.85, 3.95, -2.6, 4.0), ("L", -2.2, 3.95))}" fill="none" stroke="#9aa3b1" stroke-width="1.2"/>')
    A(f'<path d="{path(("M", -2.95, 4.05), ("L", -2.2, 4.12))}" stroke="#fff" stroke-width="1.6" stroke-linecap="round" opacity=".9"/>')
    A(rect(-1.28, 3.42, -0.8, 3.64, rx=1.5, fill="url(#lamp)", stroke="#8a5a05", stroke_width=".9"))
    # DEER GUARD: heavy black tube frame standing ~0.7 ft out in front of the bumper, from the bumper up to the hood nose
    A('<g id="deerguard">')
    dg = path(("M", -3.3, 1.9), ("L", -4.0, 2.05), ("Q", -4.16, 2.1, -4.16, 2.35), ("L", -4.16, 4.35), ("Q", -4.16, 4.84, -3.7, 4.88), ("L", -2.85, 4.9))
    A(f'<path d="{dg}" fill="none" stroke="#030304" stroke-width="7.5" stroke-linecap="round" stroke-linejoin="round"/>')
    A(f'<path d="{dg}" fill="none" stroke="#6a7282" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" stroke-opacity=".75" transform="translate(-1.8 0)"/>')
    for hh in (2.75, 3.45, 4.15): A(circ(-4.16, hh, .21, fill="#050507", stroke="#6a7282", stroke_width="1"))      # the horizontal bars, seen end-on
    A(line(-3.3, 3.45, -4.1, 3.45, stroke="#030304", stroke_width="4.6", stroke_linecap="round"))
    A(rect(-3.52, 1.6, -3.3, 2.3, rx=1.5, fill="#0a0810", stroke="#59616f", stroke_width="1"))                       # mounting plate
    A('</g>')
    # hood crease + hood/fender mirror (angled black stalk, chrome-ring convex head)
    A(f'<path d="{path(("M", -2.7, 4.35), ("Q", -0.9, 4.78, 1.0, 5.5))}" fill="none" stroke="#f0c8ec" stroke-opacity=".16" stroke-width="1.1"/>')
    A(line(-1.78, 5.1, -2.12, 6.2, stroke="#050507", stroke_width="3.2", stroke_linecap="round"))
    A(f'<ellipse cx="{X(-2.2):.1f}" cy="{Y(6.4):.1f}" rx="{S*0.24:.1f}" ry="{S*0.4:.1f}" transform="rotate(-8 {X(-2.2):.1f} {Y(6.4):.1f})" fill="#0a0a0d" stroke="#cfd6e1" stroke-width="1.6"/>')
    A(f'<ellipse cx="{X(-2.17):.1f}" cy="{Y(6.5):.1f}" rx="{S*0.1:.1f}" ry="{S*0.17:.1f}" fill="#fff" opacity=".35"/>')

    # ---- side fairing (hides the fuel tank), steps, door ----
    # BLACK plastic lower skirts: run the full length of cab + sleeper and the rear extenders, almost to the ground
    A('<g id="cabskirt">')
    A(f'<path d="{path(("M", 2.55, 3.4), ("L", CAB_BACK, 3.4), ("L", CAB_BACK, 0.9), ("L", CAB_BACK - .3, 0.78), ("L", 3.0, 0.78), ("L", 2.5, 1.7), ("L", 2.55, 2.5), ("Z",))}" fill="url(#skirtblk)" stroke="#6b6577" stroke-width="1.2" stroke-linejoin="round"/>')
    A(f'<path d="{path(("M", CAB_BACK, 4.0), ("L", FB, 4.5), ("L", FB, 1.0), ("L", CAB_BACK, 0.9), ("Z",))}" fill="url(#skirtblk)" stroke="#6b6577" stroke-width="1.2" stroke-linejoin="round"/>')
    for f in (5.9, 9.0): A(line(f, 3.35, f - .08, 0.85, stroke="#000", stroke_width="1.4", stroke_opacity=".8"))
    A(line(2.7, 3.36, CAB_BACK, 3.36, stroke="#cdbfd8", stroke_opacity=".3", stroke_width="1"))
    A(line(3.1, 0.84, CAB_BACK - .3, 0.84, stroke="#cdbfd8", stroke_opacity=".25", stroke_width="1"))
    A('</g>')
    A(line(2.95, 3.4, 12.3, 3.4, stroke="#f0c8ec", stroke_opacity=".22", stroke_width="1.2"))
    A(line(2.8, 1.1, 12.2, 1.1, stroke="#f0c8ec", stroke_opacity=".18", stroke_width="1"))
    for k in range(6): A(rect(7.6 + k * .62, 2.9, 8.05 + k * .62, 3.15, rx=1, fill="#0d040f"))
    A(rect(3.1, 2.4, 7.4, 3.0, rx=2, fill="url(#steel)", stroke="#39404c", stroke_width="1.1"))       # chrome sill plate
    for k in range(9): A(line(3.35 + k * .46, 2.5, 3.2 + k * .46, 2.9, stroke="#59616f", stroke_width=".9", stroke_opacity=".7"))
    A(rect(3.4, 1.28, 8.1, 1.58, rx=2, fill="url(#steel)", stroke="#39404c", stroke_width="1.1"))     # step
    A(f'<path d="{path(("M", 3.05, 3.4), ("L", 4.25, 8.85), ("L", DOOR_REAR, 8.85), ("L", DOOR_REAR, 3.4), ("Z",))}" fill="none" stroke="#f0c8ec" stroke-opacity=".28" stroke-width="1.2" stroke-linejoin="round"/>')
    A(f'<path d="{path(("M", 3.95, 6.5), ("L", 4.5, 8.4), ("L", DOOR_REAR - .4, 8.4), ("L", DOOR_REAR - .4, 6.68), ("Q", DOOR_REAR - .4, 6.5, DOOR_REAR - .58, 6.5), ("Z",))}" fill="url(#glass)" stroke="#8a6a88" stroke-width="1.6" stroke-linejoin="round"/>')
    A(f'<path d="{path(("M", 4.1, 8.25), ("L", 5.4, 8.3), ("L", 4.75, 6.65), ("L", 4.0, 6.65), ("Z",))}" fill="rgba(255,255,255,.1)"/>')
    # door lettering right under the window (gold), small second line, chrome cap, white plate at the sill
    A(f'<text x="{X(3.78):.1f}" y="{Y(5.95):.1f}" font-family="Arial Black,Arial,sans-serif" font-weight="900" font-size="8.4" textLength="{S*1.65:.0f}" lengthAdjust="spacingAndGlyphs" fill="#e9c23a">PRIME inc.</text>')
    A(rect(4.05, 5.52, 5.35, 5.62, fill="#e9c23a", opacity=".75"))
    A(circ(4.25, 4.85, .26, fill="url(#steel)", stroke="#39404c", stroke_width="1"))
    A(rect(3.55, 3.55, 6.15, 4.15, rx=1, fill="#e3e7ee", stroke="#9aa3b1", stroke_width="1"))
    A(line(3.7, 3.72, 5.4, 3.72, stroke="#c23b32", stroke_width="1.4", stroke_opacity=".7"))
    A(rect(DOOR_REAR - 0.8, 5.0, DOOR_REAR - .15, 5.28, rx=1.5, fill="url(#steel)", stroke="#2a303b"))        # door handle
    A(rect(DOOR_REAR - .32, 4.3, DOOR_REAR - .08, 8.1, rx=3, fill="url(#steel)", stroke="#39404c", stroke_width="1"))   # grab handle
    # seams
    A(line(DOOR_REAR, 8.85, 11.88, 8.85, stroke="#f0c8ec", stroke_opacity=".22", stroke_width="1.1"))
    A(line(DOOR_REAR + .18, 3.4, DOOR_REAR + .18, 8.85, stroke="#0b0310", stroke_width="1.1"))
    # UPPER sleeper window: wide arched dark glass above the header seam, with an oval vent in the arch
    A('<g id="upperwindow">')
    uw = path(("M", 6.9, 9.25), ("L", 6.9, 10.5), ("Q", 7.0, 11.5, 8.3, 11.9), ("Q", 9.7, 12.35, 11.1, 11.9), ("Q", 11.72, 11.62, 11.72, 11.0), ("L", 11.72, 9.25), ("Z",))
    A(f'<path d="{uw}" fill="url(#glass2)" stroke="#07040a" stroke-width="2.2" stroke-linejoin="round"/>')
    A(f'<path d="{path(("M", 7.0, 10.5), ("Q", 7.1, 11.4, 8.35, 11.78), ("Q", 9.7, 12.2, 11.05, 11.78))}" fill="none" stroke="#c9b3d8" stroke-opacity=".35" stroke-width="1.2" stroke-linecap="round"/>')
    A(f'<path d="{path(("M", 7.4, 10.3), ("L", 8.7, 11.3), ("L", 9.3, 11.0), ("L", 7.9, 9.4), ("L", 7.4, 9.6), ("Z",))}" fill="#fff" opacity=".06"/>')
    A(f'<ellipse cx="{X(10.9):.1f}" cy="{Y(11.25):.1f}" rx="{S*0.45:.1f}" ry="{S*0.17:.1f}" fill="#0c0712" stroke="#4a3a58" stroke-width="1"/>')
    A('</g>')
    # lower sleeper window: tall, framed
    A('<g id="lowerwindow">')
    A(rect(9.75, 5.7, 11.65, 8.4, rx=6, fill="url(#glass2)", stroke="#cfa9cb", stroke_width="1.8"))
    A(rect(9.9, 5.85, 11.5, 8.25, rx=4.5, fill="none", stroke="#8a6a88", stroke_width="1"))
    A(line(10.15, 8.05, 10.85, 7.0, stroke="#fff", stroke_opacity=".14", stroke_width="1.6"))
    A('</g>')

    # ---- GOLD two-tone decals (shapes measured from the photo close-ups): bright upper face over a darker gold lower face ----
    BR, DK, OUT = "#f7e45e", "#c99c1d", "#5a3d08"
    A('<g id="decals">')
    def two_tone(up, lo):
        A(poly(up, fill=BR, stroke=OUT, stroke_width=".5", stroke_linejoin="round", stroke_opacity=".6"))
        A(poly(lo, fill=DK, stroke=OUT, stroke_width=".5", stroke_linejoin="round", stroke_opacity=".6"))
    # hood: long wedge streak with a V-notch in its lower edge, rising toward the door, then a separate short bar past the seam
    two_tone(*band(-0.7, 4.12, 3.3, 5.08, 0.05, 0.7, notch=(0.5, 0.3, 0.9)))
    two_tone(*band(3.6, 5.2, 4.55, 5.42, 0.3, 0.32))
    # sleeper: long feather bolt with a pointed head and a small fin underneath, plus a short dash
    two_tone(*band(7.6, 5.7, 10.05, 6.28, 0.06, 0.74, notch=(0.78, 0.18, 0.6)))
    A(poly([(9.98, 6.66), (10.62, 6.04), (10.1, 5.92)], fill=BR, stroke=OUT, stroke_width=".5", stroke_opacity=".6"))
    A(poly([(9.45, 5.98), (9.78, 5.58), (9.95, 5.97)], fill=DK, stroke=OUT, stroke_width=".5", stroke_opacity=".6"))
    two_tone(*band(11.05, 6.42, 11.72, 6.62, 0.26, 0.3))
    A('</g>')
    A(rect(10.35, 3.95, 11.6, 4.65, rx=2, fill="none", stroke="#e9c23a", stroke_width="1"))
    for k in range(3): A(line(10.55, 4.12 + k * .19, 11.4 - (k == 2) * .5, 4.12 + k * .19, stroke="#e9c23a", stroke_width="1.2", stroke_opacity=".85"))

    # ---- visor with three amber lamps; windshield glimpse ----
    A(f'<path d="{path(("M", 3.72, 8.98), ("L", 3.0, 9.02), ("L", 3.08, 9.58), ("L", 4.7, 9.8), ("L", 4.25, 9.25), ("Z",))}" fill="#12061a" stroke="#8a6a88" stroke-width="1.1" stroke-linejoin="round"/>')
    for f, hh in ((3.3, 9.4), (3.62, 9.47), (3.95, 9.54)): A(f'<ellipse cx="{X(f):.1f}" cy="{Y(hh):.1f}" rx="{S*0.13:.1f}" ry="{S*0.09:.1f}" fill="url(#lamp)" stroke="#8a5a05" stroke-width=".8"/>')
    A(f'<path d="{path(("M", 1.6, 5.8), ("L", 3.55, 8.65), ("L", 3.3, 8.3), ("L", 2.0, 5.7), ("Z",))}" fill="url(#glass)" stroke="#8a6a88" stroke-width="1"/>')

    # ---- main door mirror: chrome West-Coast housing on two black arms ----
    A(line(3.3, 7.95, 3.85, 7.9, stroke="#050507", stroke_width="3", stroke_linecap="round"))
    A(line(3.3, 6.85, 3.85, 6.95, stroke="#050507", stroke_width="3", stroke_linecap="round"))
    A(rect(2.45, 6.3, 3.35, 8.45, rx=3.5, fill="url(#steel)", stroke="#1f242d", stroke_width="1.6"))
    A(rect(2.58, 6.45, 3.2, 8.3, rx=2.5, fill="none", stroke="#fff", stroke_opacity=".55", stroke_width="1"))
    A(rect(2.66, 7.9, 3.1, 8.2, rx=2, fill="#fff", opacity=".5"))
    A(rect(2.62, 6.5, 3.12, 7.0, rx=2, fill="#0a0a0d", opacity=".55"))
    A('</g>')

    # ---------------- trailer tires ----------------
    A(rect(TAND[1] + 1.95, 0.7, TAND[1] + 2.18, 3.3, fill="#14181f", stroke="#3a4250"))                                           # trailer mud flap
    for f in TAND: A(wheel(f, "#3d8bff", "#1d4f9c"))
    A(rect(REAR - .95, 1.75, REAR - .6, FLOOR, fill="#0b0d12", stroke="#3a4250"))                                                 # rear sill posts
    A(rect(REAR - .2, 1.75, REAR + .12, FLOOR, fill="#0b0d12", stroke="#3a4250"))
    A(rect(REAR - 1.5, 1.45, REAR + .25, 2.05, rx=2, fill="#161a22", stroke="#9aa3b1", stroke_width="1.2"))                      # ICC bumper
    A(rect(REAR - .14, 2.35, REAR + .1, 3.05, rx=2, fill="#d8362b", stroke="#7b1a14", stroke_width="1"))                          # tail lamps
    A(rect(REAR - .14, 3.2, REAR + .1, 3.7, rx=2, fill="#d8362b", stroke="#7b1a14", stroke_width="1"))

    # ---------------- callouts / dimensions ----------------
    lab = 'font-family="Inter,Arial,sans-serif"'
    def tag(x, y, head, sub=None, anchor="start"):
        s = f'<text x="{x:.1f}" y="{y:.1f}" fill="#e9edf3" {lab} font-size="13.5" font-weight="700" text-anchor="{anchor}">{head}</text>'
        if sub: s += f'<text x="{x:.1f}" y="{y+16:.1f}" fill="#a6afbd" {lab} font-size="12" text-anchor="{anchor}">{sub}</text>'
        return s
    def leader(x0, y0, x1, y1, color="#f4a81d"):
        return (f'<path d="M{x0:.1f} {y0:.1f} L{x1:.1f} {y1:.1f}" stroke="{color}" stroke-width="1.4" fill="none"/>'
                f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="3.4" fill="{color}" stroke="#07080b" stroke-width="1.2"/>')
    # reefer unit
    ux, uy = X(NOSE - REEFER_D / 2), Y(11.4)
    A(leader(ux, 62, ux, uy))
    A(tag(62, 28, "Reefer unit", "bolted to the outside of the trailer's front wall"))
    A(f'<path d="M{ux-4:.1f} 36 H{ux:.1f} V62" stroke="#f4a81d" stroke-width="1.4" fill="none"/>')
    # gap bracket
    gy = GY + 36
    A(f'<path d="M{X(CAB_BACK):.1f} {gy:.1f} H{X(NOSE):.1f} M{X(CAB_BACK):.1f} {gy-5:.1f} V{gy+5:.1f} M{X(NOSE):.1f} {gy-5:.1f} V{gy+5:.1f}" stroke="#a6afbd" stroke-width="1.3" fill="none"/>')
    A(tag(X(CAB_BACK) - 6, gy + 5, "Gap behind the cab", "about 5 ft, fairings included", "end"))
    fx_ = X(CAB_BACK + FAIRING / 2 + .1)
    A(leader(fx_, 66, fx_, Y(9.5), "#e7b6e1"))
    A(tag(fx_, 60, "Fairings", None, "middle"))
    # frame / fifth wheel
    fx = X(KINGPIN)
    A(leader(fx, GY + 66, fx, Y(3.62), "#e9edf3"))
    A(tag(fx + 12, GY + 70, "Fifth wheel", "the trailer pivots here"))
    # axle groups
    def axle_tag(f0, f1, text, color):
        x0, x1 = X(f0) - S * TIRE_R * .9, X(f1) + S * TIRE_R * .9
        yy = GY + 12
        return (f'<path d="M{x0:.1f} {yy:.1f} V{yy+6:.1f} H{x1:.1f} V{yy:.1f}" stroke="{color}" stroke-width="2" fill="none"/>'
                + f'<text x="{x1+8:.1f}" y="{yy+11:.1f}" fill="{color}" {lab} font-size="12.5" font-weight="600">{text}</text>')
    A(axle_tag(0, 0, "Steer axle", "#d3d9e2"))
    A(axle_tag(DRIVE[0], DRIVE[1], "Drive tandem", "#f4a81d"))
    A(axle_tag(TAND[0], TAND[1], "Trailer tandem", "#3d8bff"))
    # dimensions: trailer length (top) and overall height (right)
    dy = 30
    A(f'<g stroke="#7d8796" stroke-width="1.4" fill="none"><path d="M{X(NOSE):.1f} {dy} H{X(REAR):.1f} M{X(NOSE):.1f} {dy-6} V{dy+6} M{X(REAR):.1f} {dy-6} V{dy+6}"/></g>')
    A(f'<text x="{(X(NOSE)+X(REAR))/2:.1f}" y="{dy-9}" fill="#a6afbd" {lab} font-size="14" font-weight="600" text-anchor="middle">53 ft trailer</text>')
    hx = X(REAR) + 40
    A(f'<g stroke="#7d8796" stroke-width="1.4" fill="none"><path d="M{hx:.1f} {Y(TOP):.1f} V{Y(0):.1f} M{hx-6:.1f} {Y(TOP):.1f} H{hx+6:.1f} M{hx-6:.1f} {Y(0):.1f} H{hx+6:.1f}"/></g>')
    A(f'<text x="{hx+19:.1f}" y="{(Y(TOP)+Y(0))/2:.1f}" fill="#a6afbd" {lab} font-size="14" font-weight="600" text-anchor="middle" transform="rotate(90 {hx+19:.1f} {(Y(TOP)+Y(0))/2:.1f})">13 ft 6 in</text>')
    A('</svg>')
    return "\n".join(o)

if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "src" / "_parts" / "rig.svg"
    out.parent.mkdir(exist_ok=True)
    out.write_text(build())
    print("wrote", out, "viewBox", VBW, VBH)
