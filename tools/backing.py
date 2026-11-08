#!/usr/bin/env python3
"""
Generates the three top-view backing diagrams for the Training page -> src/_parts/backing_*.svg
and a verification report -> tools/backing_report.json

Every pose and arrow comes from tools/sim.py (a kinematic tractor-semitrailer model with the same dimensions
as the Trucking-page drawing). The trailer-axle path is planned, the tractor angle and steering are derived,
and the result is re-driven through the model to prove the steering really produces that path.
Scene: a loading dock at the top; two parked 53-ft trailers on 12-ft door spacing; the empty bay between
them is the target. Driver-side (left-hand) backing: the stall is on the driver's left.
"""
import json, math
from pathlib import Path
from sim import *

SC = 2.35                         # px per foot
XMIN, XMAX, YMIN, YMAX = -27.0, 133.0, -10.0, 160.0
VBW, VBH = round((XMAX - XMIN) * SC), round((YMAX - YMIN) * SC)

def PX(x): return (x - XMIN) * SC
def PY(y): return (y - YMIN) * SC

CASES = {
    "straight": dict(label="Straight-line", rear=(0.0, 62.5), t=(90, 90), M=None, ghosts=(0.5,)),
    "angle45":  dict(label="45-degree angle", rear=(26.0, 100.0), t=(45, 45), M=120, ghosts=(0.38, 0.7)),
    "offset90": dict(label="90-degree alley dock", rear=(55.0, 110.0), t=(0, 0), M=160, ghosts=(0.4, 0.72)),
}

def plan_case(c):
    rx, ry = c["rear"]; t2 = c["t"][1]
    P0 = (rx + 50 * math.cos(rad(t2)), ry + 50 * math.sin(rad(t2)))
    if c["M"] is None:
        # straight: kingpin simply moves up the page
        n = 600; st = []; sv = []
        for i in range(n + 1):
            y = P0[1] + (50.5 - P0[1]) * i / n
            st.append([0.0, y, rad(90), rad(90)]); sv.append(0.0)
        return st, sv
    st, sv, _ = plan_backing(P0, t2, c["M"], c["M"], n=1600)
    return st, sv

def rear_pt(s): return (s[0] + TR_REAR * math.cos(s[3]), s[1] + TR_REAR * math.sin(s[3]))

# ---------------------------------------------------------------------------------------------
def T(state_xy, ang_rad):
    return f'translate({PX(state_xy[0]):.2f} {PY(state_xy[1]):.2f}) rotate({deg(ang_rad):.3f}) scale({SC})'

def tractor_group(pfx, style):
    """top view of the tractor, local feet: kingpin at origin, +x forward, +y driver's RIGHT (screen-down when heading east).
       F(f) converts 'f ft behind the steer axle' (side-view measure) to x ahead of the kingpin."""
    F = lambda f: L1 - f
    xb, xf = F(12.38), F(13.88)           # sleeper back wall, rear edge of the fairings
    xw0, xw1 = F(3.7), F(1.2)             # windshield header, windshield base
    xh = F(-3.05)                         # hood nose
    g = []
    if style == "ghost":
        g.append(f'<rect x="{CAB_BACK}" y="-4.25" width="{TRACTOR_FRONT-CAB_BACK}" height="8.5" rx="1" fill="none" stroke="#e9edf3" stroke-width=".45"/>')
        return "".join(g)
    # drive tyres (peek out from under the trailer nose when the rig is articulated) + frame
    for sx in (-1, 1):
        for fx in (-2.1, 2.1):
            g.append(f'<rect x="{fx-1.7}" y="{2.4 if sx>0 else -4.2}" width="3.4" height="1.8" rx=".5" fill="#0a0c10" stroke="#2a303b" stroke-width=".15"/>')
    g.append(f'<rect x="-3.5" y="-1.4" width="{xf+3.5+0.5}" height="2.8" fill="#12151b" stroke="#2a303b" stroke-width=".15"/>')
    # steer tyres
    for sy in (-1, 1):
        y0 = 3.0 if sy > 0 else -4.3
        g.append(f'<rect x="{L1-1.7}" y="{y0}" width="3.4" height="1.3" rx=".55" fill="#0a0c10" stroke="#39404c" stroke-width=".15"/>')
    # cab fairings (side + roof extenders) behind the sleeper
    g.append(f'<rect x="{xf}" y="-4.15" width="{xb-xf+0.4}" height="8.3" rx=".5" fill="#1b0a1d" stroke="#8a4f85" stroke-width=".22"/>')
    g.append(f'<rect x="{xf+0.25}" y="-3.3" width="{xb-xf-0.1}" height="6.6" rx=".4" fill="#2a0d27" stroke="#5c3158" stroke-width=".15"/>')
    # cab + sleeper roof
    g.append(f'<rect x="{xb}" y="-4.25" width="{xw1-xb}" height="8.5" rx="1.1" fill="url(#{pfx}cab)" stroke="#8a4f85" stroke-width=".28"/>')
    g.append(f'<rect x="{xb+0.5}" y="-3.35" width="{xw0-xb-0.3}" height="6.7" rx="1.2" fill="#2a0d27" stroke="#8a4f85" stroke-width=".18"/>')   # roof panel
    g.append(f'<rect x="{xb+0.9}" y="-0.2" width="{xw0-xb-1.6}" height="0.4" fill="#f2bd2f" opacity=".95"/>')                                    # gold roof stripe
    g.append(f'<path d="M{xb+0.7} -3.1 L{xw0-0.6} -3.1" stroke="#fff" stroke-opacity=".18" stroke-width=".3"/>')
    g.append(f'<rect x="{xw0}" y="-3.7" width="{xw1-xw0}" height="7.4" rx=".5" fill="#10202f" stroke="#8a6a88" stroke-width=".2"/>')                # windshield
    g.append(f'<path d="M{xw0+0.2} -3.5 L{xw1-0.2} -3.5 L{xw1-0.7} -1.0 L{xw0+0.2} -1.0Z" fill="#fff" opacity=".12"/>')
    g.append(f'<rect x="{xw1}" y="-2.95" width="{xh-xw1}" height="5.9" rx="1.1" fill="url(#{pfx}hood)" stroke="#8a4f85" stroke-width=".25"/>')   # hood
    g.append(f'<path d="M{xw1+0.3} 0 L{xh-0.3} 0" stroke="#fff" stroke-opacity=".22" stroke-width=".25"/>')
    g.append(f'<rect x="{xh}" y="-3.6" width=".65" height="7.2" rx=".3" fill="#cdd4df" stroke="#59616f" stroke-width=".15"/>')            # bumper
    # mirrors
    for sy in (-1, 1):
        y0 = 4.25 if sy > 0 else -5.55
        g.append(f'<rect x="{F(3.3)}" y="{y0}" width=".8" height="1.3" rx=".3" fill="#0a0c10" stroke="#9aa3b1" stroke-width=".18"/>')
    return "".join(g)

def trailer_group(pfx, style):
    g = []
    hw = W / 2
    if style == "ghost":
        g.append(f'<rect x="{TR_REAR}" y="{-hw}" width="{TR_NOSE-TR_REAR}" height="{W}" rx=".6" fill="none" stroke="#e9edf3" stroke-width=".45"/>')
        return "".join(g)
    fill = f"url(#{pfx}trl)" if style == "main" else f"url(#{pfx}park)"
    edge = "#8d97a6" if style == "main" else "#59616f"
    g.append(f'<rect x="{TR_REAR}" y="{-hw}" width="{TR_NOSE-TR_REAR}" height="{W}" rx=".7" fill="{fill}" stroke="{edge}" stroke-width=".3"/>')
    for k in range(-47, 3, 4):                                  # roof ribs
        g.append(f'<line x1="{k}" y1="{-hw+.35}" x2="{k}" y2="{hw-.35}" stroke="#000" stroke-opacity=".10" stroke-width=".22"/>')
    g.append(f'<rect x="{TR_REAR+.9}" y="{-hw+.5}" width="{TR_NOSE-TR_REAR-1.8}" height="{W-1.0}" rx=".5" fill="none" stroke="#fff" stroke-opacity=".28" stroke-width=".22"/>')
    g.append(f'<rect x="{TR_REAR}" y="{-hw}" width="1.1" height="{W}" rx=".4" fill="#59616f" opacity=".85"/>')           # rear doors
    g.append(f'<line x1="{TR_REAR+.55}" y1="{-hw}" x2="{TR_REAR+.55}" y2="{hw}" stroke="#1a1f28" stroke-width=".2"/>')
    # reefer unit on the nose
    rw = 6.8 / 2
    g.append(f'<rect x="{TR_NOSE}" y="{-rw}" width="{REEFER}" height="{rw*2}" rx=".5" fill="{"#e7ebf1" if style=="main" else "#8d97a6"}" stroke="#59616f" stroke-width=".25"/>')
    for k in range(5): g.append(f'<line x1="{TR_NOSE+.35}" y1="{-rw+.8+k*1.2}" x2="{TR_NOSE+REEFER-.35}" y2="{-rw+.8+k*1.2}" stroke="#59616f" stroke-width=".2"/>')
    return "".join(g)

def rig_pose(pfx, s, style="main"):
    """returns svg for the whole rig at state s"""
    return (f'<g transform="{T((s[0], s[1]), s[2])}">{tractor_group(pfx, style)}</g>'
            f'<g transform="{T((s[0], s[1]), s[3])}">{trailer_group(pfx, style)}</g>')

def parked(pfx, nx):
    return f'<g transform="translate({PX(nx):.2f} {PY(DOCK_GAP):.2f}) rotate(90) scale({SC})"><g transform="translate({TR_NOSE} 0)">' \
           f'{trailer_group(pfx, "parked")}</g></g>'.replace(f'translate({TR_NOSE} 0)', f'translate({-(0)} 0)') if False else _parked(pfx, nx)

def _parked(pfx, nx):
    # a trailer heading DOWN the page (t=90deg) with its kingpin at (nx, DOCK_GAP+50)
    s = [nx, DOCK_GAP - TR_REAR, rad(90), rad(90)]
    return f'<g transform="{T((s[0], s[1]), s[3])}">{trailer_group(pfx, "parked")}</g>'

# ---------------------------------------------------------------------------------------------
def build(key, c):
    pfx = {"straight": "bs", "angle45": "ba", "offset90": "bo"}[key] + "_"
    states, steer = plan_case(c)
    n = len(states)
    # path of the trailer's rear centre, from start until it reaches the dock gap
    pts = []
    for s in states:
        r = rear_pt(s); pts.append(r)
        if r[1] <= DOCK_GAP + 0.02: break
    # arrow stops 7 ft before the dock face so the head is visible inside the stall
    cut = next(i for i, p in enumerate(pts) if p[1] <= 7.5) if pts[-1][1] <= 7.5 else len(pts) - 1
    apts = pts[:cut + 1]
    px = [(PX(p[0]), PY(p[1])) for p in apts]
    # arrowhead direction = direction of travel over the last ~3 ft of path
    j = len(apts) - 1
    while j > 0 and math.hypot(apts[-1][0] - apts[j][0], apts[-1][1] - apts[j][1]) < 3.0: j -= 1
    dx, dy = px[-1][0] - px[j][0], px[-1][1] - px[j][1]; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L
    tip = px[-1]; hl, hw_ = 13.0, 7.2
    base = (tip[0] - ux * hl, tip[1] - uy * hl)
    head = f"{tip[0]:.1f},{tip[1]:.1f} {base[0]-uy*hw_:.1f},{base[1]+ux*hw_:.1f} {base[0]+uy*hw_:.1f},{base[1]-ux*hw_:.1f}"
    # trim the polyline so the shaft ends at the arrowhead base (clean join)
    shaft = [p for p in px if math.hypot(p[0] - tip[0], p[1] - tip[1]) > hl * 0.9] + [base]
    line_d = "M" + " L".join(f"{p[0]:.1f},{p[1]:.1f}" for p in shaft[::4] + [shaft[-1]])

    o = []; A = o.append
    A(f'<svg class="back-art" viewBox="0 0 {VBW} {VBH}" role="img" aria-labelledby="{pfx}t {pfx}d" xmlns="http://www.w3.org/2000/svg">')
    A(f'<title id="{pfx}t">{c["label"]} backing, top view</title>')
    desc = {"straight": "Top view. A tractor-trailer is lined up straight below an empty loading-dock bay between two parked trailers. A gold arrow runs straight up the page: the trailer backs straight into the bay.",
            "angle45":  "Top view. A tractor-trailer starts angled at 45 degrees to the lower right of an empty loading-dock bay between two parked trailers. A gold arrow shows the rear of the trailer sweeping up and to the left, straightening as it enters the bay.",
            "offset90": "Top view. A tractor-trailer starts in the alley, parallel to the dock and at 90 degrees to the empty bay between two parked trailers. A gold arrow shows the rear of the trailer swinging left then up into the bay, driver-side."}[key]
    A(f'<desc id="{pfx}d">{desc}</desc>')
    A(f'''<defs>
<linearGradient id="{pfx}road" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#171c25"/><stop offset="1" stop-color="#0d1015"/></linearGradient>
<linearGradient id="{pfx}wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a414d"/><stop offset="1" stop-color="#232933"/></linearGradient>
<linearGradient id="{pfx}trl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#cfd6e1"/><stop offset=".5" stop-color="#f6f8fb"/><stop offset="1" stop-color="#bcc4d1"/></linearGradient>
<linearGradient id="{pfx}park" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7d8796"/><stop offset=".5" stop-color="#a6afbd"/><stop offset="1" stop-color="#6b7482"/></linearGradient>
<linearGradient id="{pfx}cab" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7d3c79"/><stop offset=".5" stop-color="#3a1236"/><stop offset="1" stop-color="#14061a"/></linearGradient>
<linearGradient id="{pfx}hood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6b2d67"/><stop offset=".5" stop-color="#3a1236"/><stop offset="1" stop-color="#14061a"/></linearGradient>
<filter id="{pfx}sh" x="-20%" y="-20%" width="140%" height="140%"><feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0"/><feGaussianBlur stdDeviation="2"/></filter>
</defs>''')
    A(f'<rect width="{VBW}" height="{VBH}" fill="url(#{pfx}road)"/>')
    # dock wall + doors + bumpers
    A(f'<rect x="0" y="0" width="{VBW}" height="{PY(0):.1f}" fill="url(#{pfx}wall)"/>')
    A(f'<line x1="0" y1="{PY(0):.1f}" x2="{VBW}" y2="{PY(0):.1f}" stroke="#59616f" stroke-width="1.5"/>')
    for bx in (0,) + NEIGHBOR_X + ROW_X:
        A(f'<rect x="{PX(bx-4):.1f}" y="{PY(-8):.1f}" width="{8*SC:.1f}" height="{8*SC:.1f}" rx="1.5" fill="#0b0e13" stroke="#59616f" stroke-width="1"/>')
        for k in range(1, 5): A(f'<line x1="{PX(bx-4):.1f}" y1="{PY(-8)+k*8*SC/5:.1f}" x2="{PX(bx+4):.1f}" y2="{PY(-8)+k*8*SC/5:.1f}" stroke="#1d232d" stroke-width="1"/>')
        A(f'<rect x="{PX(bx-4.6):.1f}" y="{PY(-0.6):.1f}" width="{1.3*SC:.1f}" height="{1.1*SC:.1f}" fill="#07080b"/><rect x="{PX(bx+3.3):.1f}" y="{PY(-0.6):.1f}" width="{1.3*SC:.1f}" height="{1.1*SC:.1f}" fill="#07080b"/>')
    A(f'<text x="{PX(-24):.1f}" y="{PY(-3.2):.1f}" fill="#a6afbd" font-family="Inter,Arial,sans-serif" font-size="9.5" font-weight="700" letter-spacing="1.6">LOADING DOCK</text>')
    # stall paint lines (between door bays)
    for lx in (-BAY/2, BAY/2):
        A(f'<line x1="{PX(lx):.1f}" y1="{PY(DOCK_GAP):.1f}" x2="{PX(lx):.1f}" y2="{PY(56):.1f}" stroke="#e9edf3" stroke-opacity=".18" stroke-width="1" stroke-dasharray="5 5"/>')
    # target footprint (final trailer position)
    fin = [0.0, DOCK_GAP - TR_REAR, rad(90), rad(90)]
    A(f'<g transform="{T((fin[0], fin[1]), fin[3])}"><rect x="{TR_REAR}" y="{-W/2}" width="{TR_NOSE-TR_REAR+REEFER}" height="{W}" rx=".7" fill="#f4a81d" fill-opacity=".10" stroke="#f4a81d" stroke-width=".42" stroke-dasharray="1.6 1.2"/></g>')
    # soft shadows then parked trailers
    for nx in NEIGHBOR_X + ROW_X:
        A(f'<g transform="translate(1.5 1.5)" opacity=".5" filter="url(#{pfx}sh)">{_parked(pfx, nx).replace("url(#"+pfx+"park)", "#000").replace("#e7ebf1","#000")}</g>')
    for nx in ROW_X: A(f'<g opacity=".55">{_parked(pfx, nx)}</g>')
    for nx in NEIGHBOR_X: A(_parked(pfx, nx))
    # ghost poses along the way
    for gf in c["ghosts"]:
        gi = int(gf * (n - 1))
        A(f'<g opacity="{0.55 if key!="straight" else 0.45}">{rig_pose(pfx, states[gi], "ghost")}</g>')
    # path of the trailer's rear: underlay + gold + head
    A(f'<path d="{line_d}" fill="none" stroke="#07080b" stroke-opacity=".7" stroke-width="6.2" stroke-linecap="round" stroke-linejoin="round"/>')
    # soft shadow + the moving rig at its START pose, drawn over the path start
    s0 = states[0]
    A(f'<g transform="translate(2 2)" opacity=".45" filter="url(#{pfx}sh)">{rig_pose(pfx, s0, "main").replace("url(#"+pfx+"trl)", "#000").replace("url(#"+pfx+"cab)", "#000").replace("url(#"+pfx+"hood)", "#000")}</g>')
    A(rig_pose(pfx, s0, "main"))
    A(f'<path d="{line_d}" fill="none" stroke="#f4a81d" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')
    A(f'<polygon points="{head}" fill="#f4a81d" stroke="#07080b" stroke-width="1.2" stroke-linejoin="round"/>')
    r0 = px[0]
    A(f'<circle cx="{r0[0]:.1f}" cy="{r0[1]:.1f}" r="4.6" fill="#f4a81d" stroke="#07080b" stroke-width="1.6"/>')
    A('</svg>')

    # ---- verification data ----
    done = verify_by_integration(states, steer) if key != "straight" else (0.0, 0.0)
    a = audit(states[::5])
    final = states[-1]; fr = rear_pt(final)
    rep = dict(case=key,
               start_rear_ft=[round(v, 1) for v in rear_pt(states[0])], start_headings_deg=[round(deg(states[0][2])), round(deg(states[0][3]))],
               final_rear_xy_ft=[round(fr[0], 2), round(fr[1], 2)], final_headings_deg=[round(deg(final[2]) % 360, 1), round(deg(final[3]) % 360, 1)],
               max_steer_deg=round(max(abs(v) for v in steer), 1), max_trailer_angle_deg=round(max(abs(deg(s[2] - s[3])) for s in states), 1),
               min_clearance_ft=a["min_clearance_ft"], replay_pos_err_ft=done[0], replay_angle_err_deg=done[1],
               arrow_head_dir_screen=[round(ux, 3), round(uy, 3)], arrow_tip_world_ft=[round(apts[-1][0], 1), round(apts[-1][1], 1)],
               arrow_goes_toward_dock=bool(uy < 0), path_len_ft=round(sum(math.hypot(pts[i][0]-pts[i-1][0], pts[i][1]-pts[i-1][1]) for i in range(1, len(pts)))),
               rig_extent_ft=dict(xmax=round(max(v[0] for s in states for k in ("trailer", "tractor") for v in box(s, k)), 1),
                                  ymax=round(max(v[1] for s in states for k in ("trailer", "tractor") for v in box(s, k)), 1),
                                  xmin=round(min(v[0] for s in states for k in ("trailer", "tractor") for v in box(s, k)), 1)))
    return "\n".join(o), rep

if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    out = root / "src" / "_parts"; out.mkdir(exist_ok=True)
    reports = []
    for key, c in CASES.items():
        svg, rep = build(key, c)
        (out / f"backing_{key}.svg").write_text(svg); reports.append(rep)
        print(key, json.dumps(rep))
    (Path(__file__).parent / "backing_report.json").write_text(json.dumps(reports, indent=1))
    print("viewBox", VBW, VBH)
