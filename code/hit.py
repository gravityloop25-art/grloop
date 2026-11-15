import sys, math, random
import numpy as np
from PIL import Image, ImageDraw
from common import *

MODE = sys.argv[1]            # press2 | pend | press4
CMD = sys.argv[2]             # sim | render | preview
PV = {int(x) for x in sys.argv[3:]}
random.seed(21); np.random.seed(21)
CX, CY, R = 540.0, 1010.0, 490.0
BR = 9.0
SPEED = 9.5
SUB = 4
MAXB = 1000
THR = 2.0
SPLITGH = 10
DUR_MAX = 46 * FPS
CFG = {
    "press2": dict(out="pressen_neon.mp4", title="Squeeze = Split", sub="every squeeze splits a ball", seed=71),
    "pend": dict(out="pendel_neon.mp4", title="Hit = Split", sub="every hit splits a ball", seed=72),
    "press4": dict(out="vier_pressen_neon.mp4", title="4 Presses, 1 Ball", sub="every squeeze doubles it", seed=73),
}[MODE]
sky = Sky(CFG["seed"])
PCOL = [(255, 50, 220), (255, 150, 70), (60, 220, 255), (170, 90, 255)]

def rot(v, a):
    c, s = math.cos(a), math.sin(a)
    return np.stack([v[..., 0] * c - v[..., 1] * s, v[..., 0] * s + v[..., 1] * c], -1)

def obstacles(t):
    """returns list of dict(O, al, lo, hi, vt, w, C0, split, col)"""
    C = np.array([CX, CY]); obs = []
    if MODE in ("press2", "press4"):
        n = 2 if MODE == "press2" else 4
        wa = 0.0035 if MODE == "press2" else 0.0028
        th = -math.pi / 2 + wa * t
        per = 78 if MODE == "press2" else 150
        hw = 92 if MODE == "press2" else 58
        for k in range(n):
            al = th + k * 2 * math.pi / n
            if MODE == "press2":
                ph = 2 * math.pi * t / per; e = 215 + 175 * math.cos(ph); de = -175 * math.sin(ph) * 2 * math.pi / per
            else:
                ph = 2 * math.pi * t / per - k * math.pi / 2; e = 235 + 165 * math.cos(ph); de = -165 * math.sin(ph) * 2 * math.pi / per
            u = np.array([math.cos(al), math.sin(al)])
            obs.append(dict(O=C, al=al, lo=(e, -hw), hi=(R + 90, hw), vt=u * de, w=wa, C0=C, split=True, col=PCOL[k], e=e, hw=hw))
            if MODE == "press2":
                obs.append(dict(O=C, al=al, lo=(0, -6), hi=(e, 6), vt=np.zeros(2), w=wa, C0=C, split=False, col=None, e=e, hw=6))
    else:
        piv = np.array([CX, CY - R + 6]); th = 0.62 * math.sin(2 * math.pi * t / 112)
        w = 0.62 * 2 * math.pi / 112 * math.cos(2 * math.pi * t / 112)
        al = math.pi / 2 + th
        obs.append(dict(O=piv, al=al, lo=(520, -105), hi=(760, 105), vt=np.zeros(2), w=w, C0=piv, split=True, col=PCOL[1], e=520, hw=105))
        obs.append(dict(O=piv, al=al, lo=(0, -7), hi=(520, 7), vt=np.zeros(2), w=w, C0=piv, split=False, col=None, e=520, hw=7))
    return obs

def obb(P, V, ob):
    al = ob["al"]; u = np.array([math.cos(al), math.sin(al)]); v = np.array([-math.sin(al), math.cos(al)])
    rel = P - ob["O"]; s = rel @ u; l = rel @ v
    lo, hi = ob["lo"], ob["hi"]
    qs = np.clip(s, lo[0], hi[0]); ql = np.clip(l, lo[1], hi[1]); ds = s - qs; dl = l - ql
    dist = np.hypot(ds, dl)
    near = dist < BR
    if not near.any(): return np.zeros(len(P), bool), np.zeros(len(P))
    ns = np.zeros(len(P)); nl = np.zeros(len(P)); push = np.zeros(len(P))
    out = near & (dist > 1e-6)
    ns[out] = ds[out] / dist[out]; nl[out] = dl[out] / dist[out]; push[out] = BR - dist[out]
    ins = near & ~out
    if ins.any():
        pens = np.stack([s - lo[0], hi[0] - s, l - lo[1], hi[1] - l], 1)[ins]
        k = pens.argmin(1); pm = pens.min(1)
        a = np.zeros((ins.sum(), 2)); a[k == 0, 0] = -1; a[k == 1, 0] = 1; a[k == 2, 1] = -1; a[k == 3, 1] = 1
        ns[ins] = a[:, 0]; nl[ins] = a[:, 1]; push[ins] = pm + BR
    n = ns[:, None] * u + nl[:, None] * v
    P[near] += (n * push[:, None])[near]
    r = P - ob["C0"]; vo = ob["vt"] + ob["w"] * np.stack([-r[:, 1], r[:, 0]], 1)
    vn = ((V - vo) * n).sum(1)
    bad = near & (vn < 0)
    V[bad] -= 2 * vn[bad, None] * n[bad]
    return bad, np.where(bad, -vn, 0.0)

P = np.array([[CX + 120.0, CY + 40]]); V = np.array([[SPEED * 0.6, SPEED * 0.8]])
CI = np.array([0]); GH = np.array([0])
events = []; ripples = []

def step(fr):
    global P, V, CI, GH
    wall = 0; nsplit = 0
    for sub in range(SUB):
        t = fr + (sub + 1) / SUB
        P += V / SUB
        rel = P - [CX, CY]; d = np.hypot(rel[:, 0], rel[:, 1]); out = d > R - BR
        if out.any():
            n = rel[out] / d[out, None]; vn = (V[out] * n).sum(1); Vo = V[out]; go = vn > 0
            Vo[go] -= 2 * vn[go, None] * n[go]; V[out] = Vo; P[out] = np.array([CX, CY]) + n * (R - BR); wall += int(go.sum())
        for ob in obstacles(t):
            bad, spd = obb(P, V, ob)
            if ob["split"]:
                cand = np.where(bad & (spd > THR) & (GH <= 0))[0]
                if len(cand):
                    room = MAXB - len(P)
                    cand = cand[:max(0, room)]
                    if len(cand):
                        a = 0.45
                        newV = rot(V[cand], -a); V[cand] = rot(V[cand], a)
                        newP = P[cand] + np.random.normal(0, 1.5, (len(cand), 2))
                        nc = (CI[cand] + 1) % 12; CI[cand] = nc
                        GH[cand] = SPLITGH
                        P = np.vstack([P, newP]); V = np.vstack([V, newV]); CI = np.concatenate([CI, nc])
                        GH = np.concatenate([GH, np.full(len(cand), SPLITGH)])
                        nsplit += len(cand)
    GH -= 1
    sp = np.hypot(V[:, 0], V[:, 1]) + 1e-9; V *= (SPEED / sp)[:, None]
    if wall and random.random() < .35: events.append((fr, "click", 7))
    if nsplit:
        events.append((fr, "click", random.choice([2, 4, 5, 6])))
        if nsplit >= 4: events.append((fr, "pop", min(8, len(P) // 110)))
    return nsplit

def ballcol(c):
    t = (c % 12) / 11.0
    return lerp(CYAN, VIO, t * 2) if t < .5 else lerp(VIO, (255, 120, 240), (t - .5) * 2)

MASK = Image.new("L", (W, H), 0); ImageDraw.Draw(MASK).ellipse((CX - R + 3, CY - R + 3, CX + R - 3, CY + R - 3), fill=255)

def corners(ob, e0=None):
    al = ob["al"]; u = np.array([math.cos(al), math.sin(al)]); v = np.array([-math.sin(al), math.cos(al)])
    lo, hi = ob["lo"], ob["hi"]
    return [tuple(ob["O"] + s * u + l * v) for s, l in ((lo[0], lo[1]), (hi[0], lo[1]), (hi[0], hi[1]), (lo[0], hi[1]))], u, v

def draw(fr, full):
    light = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(light)
    ringc = (255, 120, 235)
    if full is not None and 0 <= fr - full < 90 and (fr - full) % 16 < 8: ringc = (255, 255, 255)
    d.ellipse((CX - R - 3, CY - R - 3, CX + R + 3, CY + R + 3), outline=ringc, width=6)
    for i in range(48):
        a = i * 2 * math.pi / 48
        d.line((CX + (R + 10) * math.cos(a), CY + (R + 10) * math.sin(a), CX + (R + 24) * math.cos(a), CY + (R + 24) * math.sin(a)), fill=(150, 50, 140), width=3)
    obs_layer = Image.new("RGB", (W, H), (0, 0, 0)); od = ImageDraw.Draw(obs_layer)
    for ob in obstacles(fr):
        if ob["col"] is None:
            cs, u, v = corners(ob)
            od.polygon(cs, fill=(110, 70, 110), outline=(255, 190, 240))
            continue
        col = ob["col"]; cs, u, v = corners(ob)
        od.polygon(cs, fill=tuple(int(c * .16) for c in col))
        od.line([cs[0], cs[1], cs[2], cs[3], cs[0]], fill=col, width=5)
        od.line([cs[0], cs[3]], fill=tuple(min(255, c + 110) for c in col), width=8)
        e = ob["lo"][0]; hw = ob["hi"][1]
        for q in (45, 95, 145, 195):
            p1 = ob["O"] + (e + q) * u - hw * .55 * v; p2 = ob["O"] + (e + q) * u + hw * .55 * v
            od.line([tuple(p1), tuple(p2)], fill=tuple(int(c * .55) for c in col), width=3)
    if MODE != "pend":
        pass
    else:
        piv = (CX, CY - R + 6); od.ellipse((piv[0] - 22, piv[1] - 22, piv[0] + 22, piv[1] + 22), fill=(255, 220, 255))
    if MODE == "press2":
        od.ellipse((CX - 14, CY - 14, CX + 14, CY + 14), fill=(255, 255, 255))
    obs_layer = Image.composite(obs_layer, Image.new("RGB", (W, H), (0, 0, 0)), MASK)
    light = Image.fromarray(np.maximum(np.asarray(light), np.asarray(obs_layer)))
    d = ImageDraw.Draw(light)
    for (x, y), ci in zip(P, CI):
        c = ballcol(ci); d.ellipse((x - BR, y - BR, x + BR, y + BR), fill=c)
        d.ellipse((x - 4, y - 5, x, y - 1), fill=tuple(min(255, v + 110) for v in c))
    if full is not None and fr >= full:
        k = fr - full; rad = R * min(1.15, k / 36)
        if k < 40: d.ellipse((CX - rad, CY - rad, CX + rad, CY + rad), outline=(255, 230, 250), width=8)
        f = font(96); tx = "OVERFLOW!"; tw = d.textlength(tx, font=f)
        d.text((540 - tw / 2, CY - 50), tx, font=f, fill=(255, 240, 255))
    f = font(84); tw = d.textlength(CFG["title"], font=f)
    d.text((540 - tw / 2, 120), CFG["title"], font=f, fill=(255, 190, 245))
    f2 = font(40); tw = d.textlength(CFG["sub"], font=f2)
    d.text((540 - tw / 2, 232), CFG["sub"], font=f2, fill=(255, 160, 200))
    f3 = font(110); txt = str(len(P)); tw = d.textlength(txt, font=f3)
    d.text((540 - tw / 2, CY + R + 55), txt, font=f3, fill=(255, 190, 245))
    f4 = font(36); lt = "BALLS"; d.text((540 - d.textlength(lt, font=f4) / 2, CY + R + 180), lt, font=f4, fill=(255, 150, 200))
    return compose(sky.frame(fr), light)

def run():
    wr = Writer() if CMD == "render" else None; log = {}; fr = 0; full = None
    while True:
        step(fr)
        if fr % 90 == 0: log[fr // 30] = len(P)
        if len(P) >= MAXB and full is None:
            full = fr; events.append((fr, "fin", 0))
        if wr: wr.write(draw(fr, full))
        elif CMD == "preview" and fr in PV: Image.fromarray(draw(fr, full)).save(f"h_{MODE}_{fr}.png")
        fr += 1
        if (full is not None and fr > full + 150) or fr >= DUR_MAX: break
    if wr:
        wr.close(); make_audio(fr, events); mux("video_tmp.mp4", "audio.wav", CFG["out"])
    print(MODE, fr, fr / 30, log, len(P))

run()
