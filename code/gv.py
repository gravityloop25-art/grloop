import sys, math, random
import numpy as np
from PIL import Image, ImageDraw
from common import *

MODE = sys.argv[1]; CMD = sys.argv[2]; SEED = int(sys.argv[3]); GRAV = float(sys.argv[4]); PER = float(sys.argv[5])
PV = {int(x) for x in sys.argv[6:]}
random.seed(SEED); rng = np.random.default_rng(SEED)
CX, CY, R = 540.0, 1010.0, 480.0
BR = 8.0; SUB = 4; MAXB = 1000; GH0 = int(__import__("os").environ.get("GH0","12")); THR = 1.2; VMAX = 13.0; REST = float(__import__("os").environ.get("REST","0.8")); DUR_MAX = 46 * FPS
sky = Sky(151 if MODE == "gear" else 152)
BC = [(60, 220, 255), (255, 60, 220), (255, 160, 60), (160, 100, 255), (120, 255, 160)]
RAMPS = [((CX - 452, CY + 120), (CX - 150, CY + 300)), ((CX + 452, CY + 120), (CX + 150, CY + 300))] if MODE == "gear" else []
import os
KICK = float(os.environ.get("KICK","7")); GYO = float(os.environ.get("GYO","120")); SPD = float(os.environ.get("SPD","8")); AMP = float(os.environ.get("AMP","1.25"))
RG = float(os.environ.get("RG","95")); TH = 14.0; NT = 10
GEARS = [dict(c=np.array([CX - RG - 8, CY + GYO]), w=0.045, off=0.0, col=CYAN), dict(c=np.array([CX + RG + 8, CY + GYO]), w=-0.045, off=math.pi / NT, col=MAG)]
PIV = np.array([CX, CY + R - 20]); AL0 = float(os.environ.get("AMP","1.25")); ARML = R * 0.97; HW = float(os.environ.get("HW","36"))
CFG = {"gear": dict(t1="Every gear touch", t2="doubles the balls", out="gravity_zahnrad.mp4"),
       "paddle": dict(t1="Every crush", t2="doubles a ball", out="schlaeger.mp4")}[MODE]

if MODE == "gear": P = np.array([[CX - 130.0, CY - 280]]); V = np.array([[1.5, 0.5]])
else: P = np.array([[CX - 150.0, CY - 100]]); V = np.array([[5.0, -6.0]])
GH = np.zeros(1); CI = np.zeros(1, int); events = []

def rot(v, a):
    c, s = math.cos(a), math.sin(a)
    return np.stack([v[:, 0] * c - v[:, 1] * s, v[:, 0] * s + v[:, 1] * c], 1)

def gear_hit(g, t):
    global P, V
    c = g["c"]; rel = P - c; d = np.hypot(rel[:, 0], rel[:, 1]) + 1e-9
    idx = np.where(d < RG + TH + BR + 2)[0]
    if len(idx) == 0: return np.zeros(0, int), np.zeros(0)
    phi = np.arctan2(rel[idx, 1], rel[idx, 0]) - (g["w"] * t + g["off"])
    rho = RG + TH * (0.5 + 0.5 * np.cos(NT * phi)); hit = (rho + BR) > d[idx]
    ii = idx[hit]
    if len(ii) == 0: return np.zeros(0, int), np.zeros(0)
    n = rel[ii] / d[ii, None]; P[ii] = c + n * (rho[hit] + BR)[:, None]
    vs = g["w"] * np.stack([-rel[ii, 1], rel[ii, 0]], 1); vn = ((V[ii] - vs) * n).sum(1); bad = vn < 0
    jj = ii[bad]; V[jj] -= (1 + REST) * vn[bad, None] * n[bad]; V[jj] += KICK * n[bad] + rng.normal(0, 0.8, (len(jj), 2))
    return jj, -vn[bad]

def seg_hit(A, B, rad):
    global P, V
    A = np.array(A); B = np.array(B); ab = B - A
    s = np.clip(((P - A) @ ab) / (ab @ ab), 0, 1); q = A + s[:, None] * ab; dv = P - q; d = np.hypot(dv[:, 0], dv[:, 1]) + 1e-9
    near = np.where(d < rad + BR)[0]
    if len(near) == 0: return
    n = dv[near] / d[near, None]; P[near] = q[near] + n * (rad + BR); vn = (V[near] * n).sum(1); bad = vn < 0
    jj = near[bad]; V[jj] -= (1 + REST * 0.7) * vn[bad, None] * n[bad]

def arm_state(t):
    a = AL0 * math.sin(2 * math.pi * t / PER); w = AL0 * 2 * math.pi / PER * math.cos(2 * math.pi * t / PER)
    return -math.pi / 2 + a, w

def obb(al, w):
    global P, V
    u = np.array([math.cos(al), math.sin(al)]); v = np.array([-math.sin(al), math.cos(al)])
    rel = P - PIV; s = rel @ u; l = rel @ v
    qs = np.clip(s, 0, ARML); ql = np.clip(l, -HW, HW); ds = s - qs; dl = l - ql; dist = np.hypot(ds, dl)
    near = dist < BR
    if not near.any(): return np.zeros(0, int), np.zeros(0)
    ns = np.zeros(len(P)); nl = np.zeros(len(P)); push = np.zeros(len(P))
    out = near & (dist > 1e-6); ns[out] = ds[out] / dist[out]; nl[out] = dl[out] / dist[out]; push[out] = BR - dist[out]
    ins = near & ~out
    if ins.any():
        pens = np.stack([s - 0, ARML - s, l + HW, HW - l], 1)[ins]; k = pens.argmin(1); pm = pens.min(1)
        a = np.zeros((ins.sum(), 2)); a[k == 0, 0] = -1; a[k == 1, 0] = 1; a[k == 2, 1] = -1; a[k == 3, 1] = 1
        ns[ins] = a[:, 0]; nl[ins] = a[:, 1]; push[ins] = pm + BR
    n = ns[:, None] * u + nl[:, None] * v; P[near] += (n * push[:, None])[near]
    r = P - PIV; vo = w * np.stack([-r[:, 1], r[:, 0]], 1); vn = ((V - vo) * n).sum(1); bad = near & (vn < 0)
    V[bad] -= (1 + 0.5) * vn[bad, None] * n[bad]
    return np.where(bad)[0], -vn[bad]

def step(fr):
    global P, V, GH, CI
    ns = 0
    for sub in range(SUB):
        t = fr + (sub + 1) / SUB
        V[:, 1] += GRAV / SUB; sp = np.hypot(V[:, 0], V[:, 1])
        if MODE == 'paddle': V *= (SPD / (sp + 1e-9))[:, None]
        else:
            big = sp > VMAX; V[big] *= (VMAX / sp[big])[:, None]
        P += V / SUB
        rel = P - [CX, CY]; d = np.hypot(rel[:, 0], rel[:, 1]) + 1e-9; out = d > R - BR
        if out.any():
            n = rel[out] / d[out, None]; vn = (V[out] * n).sum(1); Vo = V[out]; g = vn > 0
            Vo[g] -= (1 + REST) * vn[g, None] * n[g]; V[out] = Vo; P[out] = np.array([CX, CY]) + n * (R - BR)
        cands = []
        if MODE == "gear":
            for A, B in RAMPS: seg_hit(A, B, 14.0)
            for g in GEARS:
                jj, spd = gear_hit(g, t)
                if len(jj): cands.append(jj[spd > THR])
        else:
            al, w = arm_state(t); jj, spd = obb(al, w)
            if len(jj):
                dd = np.hypot(P[jj, 0] - CX, P[jj, 1] - CY); cands.append(jj[spd > 0.0])
        if cands:
            cand = np.unique(np.concatenate(cands)); cand = cand[GH[cand] <= 0][:max(0, MAXB - len(P))]
            if len(cand):
                if MODE == 'paddle':
                    aa = rng.uniform(0.5, 1.6, len(cand)) * rng.choice([-1, 1], len(cand)); c_, s_ = np.cos(aa), np.sin(aa); v0 = V[cand].copy()
                    nv = np.stack([v0[:, 0] * c_ - v0[:, 1] * s_, v0[:, 0] * s_ + v0[:, 1] * c_], 1); V[cand] = np.stack([v0[:, 0] * c_ + v0[:, 1] * s_, -v0[:, 0] * s_ + v0[:, 1] * c_], 1)
                else:
                    nv = rot(V[cand], -0.5) + rng.normal(0, 0.8, (len(cand), 2)); V[cand] = rot(V[cand], 0.5)
                GH[cand] = GH0
                P = np.vstack([P, P[cand] + rng.normal(0, 1.5, (len(cand), 2))]); V = np.vstack([V, nv])
                GH = np.concatenate([GH, np.full(len(cand), GH0)]); CI = np.concatenate([CI, (CI[cand] + 1) % 5]); ns += len(cand)
    GH -= 1
    if ns:
        events.append((fr, "click", random.choice([2, 4, 5, 6])))
        if ns >= 4: events.append((fr, "pop", min(8, len(P) // 120)))
    return ns

def tooth_poly(g, t):
    pts = []
    for i in range(160):
        phi = i * 2 * math.pi / 160; rho = RG + TH * (0.5 + 0.5 * math.cos(NT * (phi - g["w"] * t - g["off"]) + 0)) if False else None
    for i in range(160):
        ang = i * 2 * math.pi / 160; ph = ang - (g["w"] * t + g["off"])
        rho = RG + TH * (0.5 + 0.5 * math.cos(NT * ph)); pts.append((g["c"][0] + rho * math.cos(ang), g["c"][1] + rho * math.sin(ang)))
    return pts

def draw(fr, endfr):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    rc = (255, 235, 250)
    if endfr is not None and 0 <= fr - endfr < 90 and (fr - endfr) % 16 < 8: rc = (255, 255, 255)
    d.ellipse((CX - R - 4, CY - R - 4, CX + R + 4, CY + R + 4), outline=rc, width=6)
    if MODE == "gear":
        for A, B in RAMPS:
            d.line([A, B], fill=(70, 50, 110), width=34); d.line([A, B], fill=(190, 150, 255), width=5)
        pass
        for g in GEARS:
            pts = tooth_poly(g, fr); d.polygon(pts, fill=tuple(int(c * .22) for c in g["col"]), outline=g["col"])
            d.line(pts + [pts[0]], fill=g["col"], width=4)
            cx, cy = g["c"]; d.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), fill=(255, 240, 255))
    else:
        al, w = arm_state(fr); u = np.array([math.cos(al), math.sin(al)]); v = np.array([-math.sin(al), math.cos(al)])
        cs = [tuple(PIV + s * u + l * v) for s, l in ((0, -HW), (ARML, -HW), (ARML, HW), (0, HW))]
        d.polygon(cs, fill=(70, 40, 60)); d.line(cs + [cs[0]], fill=(255, 150, 90), width=5)
        d.line([cs[0], cs[3]], fill=(255, 220, 190), width=8)
        for q in (80, 160, 240, 320, 400):
            p1 = PIV + q * u - HW * .5 * v; p2 = PIV + q * u + HW * .5 * v; d.line([tuple(p1), tuple(p2)], fill=(200, 110, 70), width=3)
        d.ellipse((PIV[0] - 26, PIV[1] - 26, PIV[0] + 26, PIV[1] + 26), fill=(255, 240, 255))
    for (x, y), c in zip(P, CI):
        col = BC[c % 5]; d.ellipse((x - BR, y - BR, x + BR, y + BR), fill=col)
        d.ellipse((x - 4, y - 5, x, y - 1), fill=tuple(min(255, q + 110) for q in col))
    f = font(66)
    d.text((540 - d.textlength(CFG["t1"], font=f) / 2, 95), CFG["t1"], font=f, fill=(255, 240, 252))
    d.text((540 - d.textlength(CFG["t2"], font=f) / 2, 175), CFG["t2"], font=f, fill=(255, 240, 252))
    f3 = font(130); tx = f"{len(P):,}"; d.text((540 - d.textlength(tx, font=f3) / 2, 260), tx, font=f3, fill=(255, 200, 245))
    f4 = font(34); tx = "BALLS  -  will it overflow?"; d.text((540 - d.textlength(tx, font=f4) / 2, 405), tx, font=f4, fill=(220, 180, 230))
    bw = 700; by = CY + R + 55
    d.rectangle((540 - bw / 2, by, 540 + bw / 2, by + 16), outline=(140, 70, 130), width=2)
    d.rectangle((540 - bw / 2, by, 540 - bw / 2 + bw * min(1, len(P) / MAXB), by + 16), fill=(255, 60, 200))
    f5 = font(36); tx = f"OVERFLOW AT {MAXB:,}"; d.text((540 - d.textlength(tx, font=f5) / 2, by + 35), tx, font=f5, fill=(210, 190, 225))
    if endfr is not None and fr >= endfr:
        k = fr - endfr; rad = R * min(1.12, k / 36)
        if k < 40: d.ellipse((CX - rad, CY - rad, CX + rad, CY + rad), outline=(255, 230, 250), width=8)
        f6 = font(100); tx = "OVERFLOW!"
        d.rectangle((0, CY - 160, W, CY - 30), fill=(0, 0, 0))
        if k % 14 < 10 or k > 40: d.text((540 - d.textlength(tx, font=f6) / 2, CY - 150), tx, font=f6, fill=(255, 250, 210))
    return compose(sky.frame(fr), img, .7, .55, .3)

def run():
    wr = Writer() if CMD == "render" else None; fr = 0; endfr = None; log = {}
    while True:
        if endfr is None: step(fr)
        if endfr is None and len(P) >= MAXB: endfr = fr; events.append((fr, "fin", 0))
        if fr % 90 == 0: log[fr // 30] = len(P)
        if wr: wr.write(draw(fr, endfr))
        elif CMD == "preview" and fr in PV: Image.fromarray(draw(fr, endfr)).save(f"p_{MODE}_{fr}.png")
        fr += 1
        if (endfr is not None and fr > endfr + 110) or fr >= DUR_MAX: break
    if wr:
        wr.close(); make_audio(fr, events); mux("video_tmp.mp4", "audio.wav", CFG["out"])
    print(MODE, SEED, GRAV, PER, "end", endfr and round(endfr / 30, 1), log)

run()
