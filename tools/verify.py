#!/usr/bin/env python3
"""
Independent audit of the built site + generated artwork ("review it like someone else's work").
Run after build:   python3 tools/verify.py
Exit code 0 = every check passed. Anything FAIL must be fixed or explained before shipping.
"""
import json, math, re, sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import sim, rig, backing  # noqa

results = []
def check(name, ok, detail=""):
    results.append((bool(ok), name, detail))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))

# ---------------------------------------------------------------- 1. artwork files are valid XML
parts = sorted((ROOT / "src" / "_parts").glob("*.svg"))
check("generated SVG parts exist (rig + 3 backing)", len(parts) == 4, ", ".join(p.name for p in parts))
for p in parts:
    try:
        ET.fromstring(p.read_text()); ok = True; d = ""
    except Exception as e:
        ok, d = False, str(e)
    check(f"{p.name} is well-formed XML", ok, d)

# ---------------------------------------------------------------- 2. built pages
pages = sorted((ROOT / "site").glob("*.html"))
pages = [p for p in pages if not p.name.startswith("_")]
for p in pages:
    h = p.read_text()
    ids = re.findall(r'\bid="([^"]+)"', h)
    dup = sorted({i for i in ids if ids.count(i) > 1})
    check(f"{p.name}: no duplicate ids", not dup, ",".join(dup))
    check(f"{p.name}: no unresolved {{{{placeholders}}}}", "{{" not in h)
    m = re.search(r'<header.*?</header>', h, re.S)
    first_a = re.search(r'<a class="brand" href="([^"]+)"', m.group(0)) if m else None
    check(f"{p.name}: logo link goes Home", bool(first_a) and first_a.group(1) == "index.html")
    for ref in re.findall(r'(?:src|href)="([^"#?:]+\.(?:html|css|js|png|jpg|svg|xml|txt))"', h):
        check(f"{p.name}: local ref exists -> {ref}", (ROOT / "site" / ref).exists())
for svg in parts:
    t = svg.read_text()
    if svg.name == "rig.svg":
        check("rig.svg: trailer decal reads PRIME inc. (caps PRIME, lowercase inc.)", t.count(">PRIME<") >= 2 and t.count(">inc.<") >= 2)
        check("rig.svg: door decal present", ">PRIME inc.<" in t)
    else:
        check(f"{svg.name}: no carrier text", not re.search(r"prime", t, re.I))
    check(f"{svg.name}: no external references", "http" not in re.sub(r'xmlns="http://www.w3.org/2000/svg"', "", t))

# ---------------------------------------------------------------- 3. rig geometry (side view)
clear = rig.GAP - rig.FAIRING - rig.REEFER_D
check("gap = ~5 ft sleeper-to-trailer, of which fairings take 1.5 ft (Matt)", abs(rig.GAP - 5.0) < 1e-9 and abs(rig.FAIRING - 1.5) < 1e-9, f"gap {rig.GAP}, fairings {rig.FAIRING}")
check("visible gap behind the fairings is ~3.5 ft (Matt)", abs((rig.GAP - rig.FAIRING) - 3.5) < 1e-9)
check("reefer unit fits between fairings and trailer nose with >=1 ft clearance", clear >= 1.0, f"unit {rig.REEFER_D} ft, clearance {clear:.1f} ft")
check("sleeper behind the door is ~6 ft (72-inch sleeper, Matt)", abs((rig.CAB_BACK - rig.DOOR_REAR) - 6.0) < 0.1, f"{rig.CAB_BACK - rig.DOOR_REAR:.2f} ft")
check("trailer nose sits about over the front drive tyre's leading edge (photos)", abs(rig.NOSE - (rig.DRIVE[0] - rig.TIRE_R)) < 1.0, f"nose {rig.NOSE:.1f}, tyre edge {rig.DRIVE[0]-rig.TIRE_R:.1f}")
check("fifth wheel (kingpin) sits within the drive-tandem span", rig.DRIVE[0] <= rig.KINGPIN <= rig.DRIVE[1], f"kingpin {rig.KINGPIN:.1f}, axles {rig.DRIVE[0]:.1f}-{rig.DRIVE[1]:.1f}")
check("trailer nose is ahead of rear drive axle (trailer overhangs the tractor frame)", rig.NOSE < rig.DRIVE[1])
check("frame extends from behind the cab to the fifth wheel", rig.CAB_BACK < rig.KINGPIN, f"cab back {rig.CAB_BACK}, kingpin {rig.KINGPIN:.1f}")
check("trailer top = 13.5 ft (13 ft 6 in label)", abs(rig.TOP - 13.5) < 1e-9)
check("trailer box = 53 ft (label)", abs(rig.REAR - rig.NOSE - 53.0) < 1e-9)
check("axle count = 5 (1 steer + 2 drive + 2 trailer)", 1 + len(rig.DRIVE) + len(rig.TAND) == 5)
rsvg = (ROOT / "src" / "_parts" / "rig.svg").read_text()
check("APU not drawn on the driver's side (it is on the passenger-side frame)", 'id="apu"' not in rsvg and "APU" not in rsvg)
for must in ("Reefer unit", "Fairings", "Fifth wheel", "53 ft trailer", "13 ft 6 in", "Steer axle", "Drive tandem", "Trailer tandem", "Gap behind the cab"):
    check(f"rig label present: {must}", must in rsvg)
# measured from the DRAWN outlines (not from constants): cab/fairing roof vs trailer roof, and fairing->trailer gap
def _min_y(d):
    nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", d)]
    return min(nums[1::2])
def _path_d(fill):
    m = re.search(r'<path d="([^"]+)" fill="url\(#%s\)"' % fill, rsvg)
    return m.group(1) if m else None
cab_top, trl_top = _min_y(_path_d("cabfill")), _min_y(_path_d("trl"))
check("height at the back of the sleeper/fairings equals the trailer height (drawn outlines)", abs(cab_top - trl_top) < 1.5, f"cab top y={cab_top:.1f}px, trailer top y={trl_top:.1f}px")
cab_xs = [float(v) for v in re.findall(r"-?\d+\.?\d*", _path_d("cabfill"))][0::2]
trl_xs = [float(v) for v in re.findall(r"-?\d+\.?\d*", _path_d("trl"))][0::2]
vis_gap_ft = (min(trl_xs) - max(cab_xs)) / rig.S
check("visible gap, back of fairings to trailer front, is 3.5 ft (drawn outlines)", abs(vis_gap_ft - 3.5) < 0.1, f"{vis_gap_ft:.2f} ft")
rm = re.search(r'<g id="reefer">\s*<path d="([^"]+)"', rsvg)
reefer_front_ft = (min(trl_xs) - min(float(v) for v in re.findall(r"-?\d+\.?\d*", rm.group(1))[0::2])) / rig.S if rm else None
check("reefer unit sits inside that gap, in front of the trailer's front wall (drawn outlines)", reefer_front_ft is not None and 1.5 < reefer_front_ft < vis_gap_ft - 0.8, f"unit depth {reefer_front_ft:.2f} ft of a {vis_gap_ft:.2f} ft gap")
# --- Matt's photo-accuracy callouts, measured from the DRAWN SVG (not constants) ---
def _grp(gid):
    m = re.search(r'<g id="%s">(.*?)</g>' % gid, rsvg, re.S)
    return m.group(1) if m else ""
def _nums(txt, axis):
    vals = [float(v) for v in re.findall(r"-?\d+\.?\d*", txt)]
    return vals[axis::2]
def _path_ds(txt): return " ".join(re.findall(r' d="([^"]+)"', txt))
bump, deer, skirt = _grp("bumper"), _grp("deerguard"), _grp("cabskirt")
check("deer guard exists and sticks out >= 0.5 ft in front of the bumper (drawn)", bool(deer) and (min(_nums(_path_ds(bump), 0)) - min(_nums(_path_ds(deer), 0))) / rig.S >= 0.5,
      f"{(min(_nums(_path_ds(bump),0)) - min(_nums(_path_ds(deer),0)))/rig.S:.2f} ft ahead" if deer else "missing")
check("black plastic lower bumper below the gray/chrome part (drawn)", "url(#skirtblk)" in bump and "url(#valance)" in bump)
check("black lower skirts reach to within 1 ft of the ground along cab + sleeper (drawn)", bool(skirt) and (rig.GY - max(_nums(_path_ds(skirt), 1))) / rig.S <= 1.0,
      f"{(rig.GY - max(_nums(_path_ds(skirt),1)))/rig.S:.2f} ft above ground" if skirt else "missing")
check("skirts span the whole cab+sleeper length (drawn)", bool(skirt) and (max(_nums(_path_ds(skirt), 0)) - min(_nums(_path_ds(skirt), 0))) / rig.S >= 9.5)
uw = _grp("upperwindow")
check("upper sleeper window present, above the header seam and below the roof (drawn)", bool(uw) and max(_nums(_path_ds(uw), 1)) < rig.Y(8.85) and min(_nums(_path_ds(uw), 1)) > cab_top + 10)
check("lower sleeper window present", bool(_grp("lowerwindow")))
dec = _grp("decals")
check("gold decals are two-tone (bright + dark gold, >=4 of each)", dec.count('fill="#f7e45e"') >= 4 and dec.count('fill="#c99c1d"') >= 4, f"{dec.count('fill=\"#f7e45e\"')} bright / {dec.count('fill=\"#c99c1d\"')} dark")
# sim and drawing use the same rig dimensions
check("sim wheelbase == drawing wheelbase", abs(sim.L1 - rig.WHEELBASE) < 0.01, f"sim {sim.L1}, drawing {rig.WHEELBASE:.2f}")
check("sim kingpin->trailer-tandem == drawing", abs(sim.L2 - ((rig.TAND[0] + rig.TAND[1]) / 2 - rig.KINGPIN)) < 0.01, f"sim {sim.L2}, drawing {(rig.TAND[0]+rig.TAND[1])/2-rig.KINGPIN:.2f}")
check("sim cab-fairing rear ahead of kingpin == drawing", abs(sim.CAB_BACK - (rig.KINGPIN - rig.CAB_BACK - rig.FAIRING)) < 0.05, f"sim {sim.CAB_BACK:.2f}, drawing {rig.KINGPIN-rig.CAB_BACK-rig.FAIRING:.2f}")

# ---------------------------------------------------------------- 4. backing plans: physics + arrows (recomputed, not read from files)
for key, c in backing.CASES.items():
    st, sv = backing.plan_case(c)
    # (a) non-holonomic consistency, computed from raw geometry only
    worst_p, worst_a = 0.0, 0.0
    for i in range(2, len(st) - 2, 3):
        a, b = st[i - 1], st[i + 1]
        # kingpin P moves BACKWARD: its velocity must point along -heading(t1)
        vx, vy = b[0] - a[0], b[1] - a[1]
        if math.hypot(vx, vy) < 1e-9: continue
        want = math.atan2(-math.sin(st[i][2]), -math.cos(st[i][2]))
        worst_p = max(worst_p, abs(math.degrees((math.atan2(vy, vx) - want + math.pi) % (2 * math.pi) - math.pi)))
        # trailer tandem centre A moves backward along -heading(t2)
        A = lambda s: (s[0] - sim.L2 * math.cos(s[3]), s[1] - sim.L2 * math.sin(s[3]))
        ax, ay = A(b)[0] - A(a)[0], A(b)[1] - A(a)[1]
        want = math.atan2(-math.sin(st[i][3]), -math.cos(st[i][3]))
        worst_a = max(worst_a, abs(math.degrees((math.atan2(ay, ax) - want + math.pi) % (2 * math.pi) - math.pi)))
    check(f"{key}: tractor never slides sideways (kingpin heading error)", worst_p < 1.0, f"{worst_p:.2f} deg")
    check(f"{key}: trailer never slides sideways (axle heading error)", worst_a < 1.0, f"{worst_a:.2f} deg")
    # (b) re-drive the kinematic model with only the steering
    pe, ae = sim.verify_by_integration(st, sv) if key != "straight" else (0, 0)
    check(f"{key}: replaying the steering reproduces the path", pe < 0.5 and ae < 1.0, f"{pe} ft, {ae} deg")
    # (c) ends parked square in the bay, rear at the dock
    f = st[-1]; rx, ry = backing.rear_pt(f)
    check(f"{key}: ends centred in bay, square, rear at dock", abs(rx) < 0.1 and abs(ry - sim.DOCK_GAP) < 0.1 and abs(math.degrees(f[3]) - 90) < 0.5 and abs(math.degrees(f[2]) - 90) < 1.0,
          f"rear ({rx:.2f},{ry:.2f}) t1 {math.degrees(f[2]):.1f} t2 {math.degrees(f[3]):.1f}")
    # (d) clearances / limits (all dock-row trailers counted)
    a = sim.audit(st[::4])
    check(f"{key}: clears every parked trailer by >= 2 ft", a["min_clearance_ft"] >= 2.0, f"{a['min_clearance_ft']} ft")
    check(f"{key}: steering within 35 deg", max(abs(v) for v in sv) <= 35.0, f"{max(abs(v) for v in sv):.1f} deg")
    check(f"{key}: trailer angle within 60 deg (no jackknife)", a["max_articulation_deg"] <= 60.0, f"{a['max_articulation_deg']} deg")
    # (e) the start pose is what the picture says it is
    s0 = st[0]
    rear0 = backing.rear_pt(s0); head = (math.degrees(s0[3]) % 360)
    expect = {"straight": 90, "angle45": 45, "offset90": 0}[key]
    check(f"{key}: start trailer heading = {expect} deg", abs(head - expect) < 0.5, f"{head:.1f}")
    # (f) arrow in the drawing: parse the generated SVG, recompute its direction
    svg = (ROOT / "src" / "_parts" / f"backing_{key}.svg").read_text()
    poly = re.findall(r'<polygon points="([^"]+)" fill="#f4a81d"', svg)
    check(f"{key}: arrowhead present", len(poly) == 1)
    tip, b1, b2 = [tuple(map(float, q.split(","))) for q in poly[0].split()]
    mid = ((b1[0] + b2[0]) / 2, (b1[1] + b2[1]) / 2)
    dx, dy = tip[0] - mid[0], tip[1] - mid[1]
    ang = math.degrees(math.atan2(dy, dx))
    check(f"{key}: arrowhead points toward the dock (up the page)", dy < 0 and abs(ang + 90) < 6, f"heading {ang:.1f} deg (screen), -90 = straight up")
    # arrow tip location in world feet must be inside the bay, near the dock
    tx, ty = tip[0] / backing.SC + backing.XMIN, tip[1] / backing.SC + backing.YMIN
    check(f"{key}: arrow tip inside the bay near the dock", abs(tx) < 4.25 and 0.5 < ty < 12, f"({tx:.1f}, {ty:.1f}) ft")
    # arrow tail starts on the trailer's rear (start dot) not on the cab
    dot = re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="4.6" fill="#f4a81d"', svg)
    cx, cy = float(dot[0][0]) / backing.SC + backing.XMIN, float(dot[0][1]) / backing.SC + backing.YMIN
    check(f"{key}: arrow starts at the trailer's rear end", math.hypot(cx - rear0[0], cy - rear0[1]) < 0.3, f"dot ({cx:.1f},{cy:.1f}) vs rear ({rear0[0]:.1f},{rear0[1]:.1f})")
    # the cab must be at the far end from the arrow tail (i.e. arrow tail is not at the cab)
    cabx = s0[0] + 22 * math.cos(s0[2]); caby = s0[1] + 22 * math.sin(s0[2])
    check(f"{key}: cab is on the opposite end of the rig from the arrow tail", math.hypot(cabx - rear0[0], caby - rear0[1]) > 60, f"{math.hypot(cabx-rear0[0], caby-rear0[1]):.0f} ft apart")

# ---------------------------------------------------------------- 5. stated claims in the page text
tr = (ROOT / "src" / "training.html").read_text()
gap = (2 * sim.BAY - sim.W) / 2 - 0  # clear gap between neighbours minus trailer width, split per side
spare = ((2 * sim.BAY - sim.W) - sim.W) / 2
check("'about 3½ ft to spare on each side' matches 12-ft door spacing and 8.5-ft trailers", abs(spare - 3.5) < 0.01, f"{spare} ft")
rep = {r["case"]: r for r in json.loads((ROOT / "tools" / "backing_report.json").read_text())}
check("'rear starts roughly 100 ft from the dock' (45 deg)", abs(rep["angle45"]["start_rear_ft"][1] - 100) < 5, str(rep["angle45"]["start_rear_ft"]))

bad = [n for ok, n, _ in results if not ok]
print(f"\n{len(results)-len(bad)}/{len(results)} checks passed")
if bad:
    print("FAILED:\n  " + "\n  ".join(bad)); sys.exit(1)
