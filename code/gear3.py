import sys, math, random
import numpy as np
from PIL import Image, ImageDraw
from common import *

random.seed(13); np.random.seed(13)
CX, CY, R = 540.0, 1060.0, 490.0
BR = 9.0
SPEED = 10.0
SUB = 3
MAXB = 1000
AR, T, HUB = 128.0, 20.0, 30.0
UNITS = [  # center, spin, omega, phase, color
    dict(g=np.array([CX - 175, CY - 130]), spin=0.012, om=math.pi / 32, ph=math.pi, col=(255, 60, 220)),
    dict(g=np.array([CX + 175, CY - 130]), spin=-0.010, om=math.pi / 36, ph=0.0, col=(60, 220, 255)),
    dict(g=np.array([CX, CY + 190]), spin=0.009, om=math.pi / 30, ph=1.6, col=(255, 160, 60)),
]
for u in UNITS: u["last"] = -100
DUR_MAX = 44 * FPS
sky = Sky(61)

def ang(u, fr):
    base = u["spin"] * fr + u["ph"]; rel = u["om"] * (fr - 28)
    return base + rel, base - rel

P = np.array([[CX - 20.0, CY - 10]]); V = np.array([[SPEED * 0.8, SPEED * 0.6]])
CI = np.array([0]); GH = np.array([0]); SC = np.array([0.0])
events = []; ripples = []

def pt_collide(P, V, pt, lim):
    rel = P - pt; d = np.hypot(rel[:, 0], rel[:, 1]) + 1e-9; hit = d < lim
    refl = np.zeros(len(P), bool)
    if not hit.any(): return refl
    n = rel[hit] / d[hit, None]; P[hit] = pt + n * lim
    vn = (V[hit] * n).sum(1); bad = vn < 0
    Vh = V[hit]; Vh[bad] -= 2 * vn[bad, None] * n[bad]; V[hit] = Vh
    hi = np.where(hit)[0]; refl[hi[bad]] = True
    return refl

def arc_collide(P, V, cen, start, sign):
    rel = P - cen; d = np.hypot(rel[:, 0], rel[:, 1]) + 1e-9
    a = np.arctan2(rel[:, 1], rel[:, 0]); off = ((a - start) * sign) % (2 * math.pi)
    inspan = off < math.pi; lim = BR + T / 2
    hit = inspan & (np.abs(d - AR) < lim); refl = np.zeros(len(P), bool)
    if hit.any():
        s = np.sign(d - AR)[hit]; s[s == 0] = 1
        n = rel[hit] / d[hit, None] * s[:, None]
        P[hit] = cen + rel[hit] / d[hit, None] * (AR + s * lim)[:, None]
        vn = (V[hit] * n).sum(1); bad = vn < 0
        Vh = V[hit]; Vh[bad] -= 2 * vn[bad, None] * n[bad]; V[hit] = Vh
        hi = np.where(hit)[0]; refl[hi[bad]] = True
    end = cen + AR * np.array([math.cos(start + sign * math.pi), math.sin(start + sign * math.pi)])
    refl |= pt_collide(P, V, end, lim)
    return refl

def step(fr):
    global P, V, CI, GH, SC
    arms = []
    for u in UNITS:
        ta, tb = ang(u, fr)
        ca = u["g"] + AR * np.array([math.cos(ta), math.sin(ta)]); cb = u["g"] + AR * np.array([math.cos(tb), math.sin(tb)])
        arms.append((ta, tb, ca, cb))
    wall = armh = 0
    for _ in range(SUB):
        P += V / SUB
        rel = P - [CX, CY]; d = np.hypot(rel[:, 0], rel[:, 1]); out = d > R - BR
        if out.any():
            n = rel[out] / d[out, None]; vn = (V[out] * n).sum(1); Vo = V[out]; go = vn > 0
            Vo[go] -= 2 * vn[go, None] * n[go]; V[out] = Vo; P[out] = np.array([CX, CY]) + n * (R - BR); wall += int(go.sum())
        idx = np.where(GH <= 0)[0]
        if len(idx):
            Pa, Va = P[idx], V[idx]; rr = np.zeros(len(idx), bool)
            for u, (ta, tb, ca, cb) in zip(UNITS, arms):
                rr |= arc_collide(Pa, Va, ca, ta + math.pi, +1)
                rr |= arc_collide(Pa, Va, cb, tb + math.pi, -1)
                rr |= pt_collide(Pa, Va, u["g"], HUB + BR)
            P[idx], V[idx] = Pa, Va; armh += int(rr.sum()); SC[idx[rr]] += 1
    GH -= 1; SC *= 0.9; stuck = SC > 3; GH[stuck] = 12; SC[stuck] = 0
    sp = np.hypot(V[:, 0], V[:, 1]) + 1e-9; V *= (SPEED / sp)[:, None]
    if wall and random.random() < .5: events.append((fr, "click", 7))
    if armh: events.append((fr, "click", random.choice([2, 4, 5])))
    for u, (ta, tb, ca, cb) in zip(UNITS, arms):
        diff = abs(((ta - tb) + math.pi) % (2 * math.pi) - math.pi)
        if diff < 0.07 and fr - u["last"] > 20:
            u["last"] = fr
            rel = P - ca; inside = np.hypot(rel[:, 0], rel[:, 1]) < AR - T / 2
            if inside.any():
                ids = np.where(inside)[0]; room = MAXB - len(P); nP, nV, nC = [], [], []
                for i in ids:
                    nc = (CI[i] + 1) % 12; CI[i] = nc; GH[i] = 22
                    a = random.uniform(0, 6.283); V[i] = [SPEED * math.cos(a), SPEED * math.sin(a)]
                    if room > 0:
                        room -= 1; a = random.uniform(0, 6.283)
                        nP.append(P[i] + np.random.normal(0, 4, 2)); nV.append([SPEED * math.cos(a), SPEED * math.sin(a)]); nC.append(nc)
                if nP:
                    P = np.vstack([P, nP]); V = np.vstack([V, nV]); CI = np.concatenate([CI, nC])
                    GH = np.concatenate([GH, np.full(len(nP), 22)]); SC = np.concatenate([SC, np.zeros(len(nP))])
                ripples.append([ca[0], ca[1], 0, u["col"]])
                events.append((fr, "pop", min(8, len(P) // 110)))
    for r in ripples: r[2] += 1
    ripples[:] = [r for r in ripples if r[2] < 26]
    return arms

def ballcol(c):
    t = (c % 12) / 11.0
    return lerp(CYAN, VIO, t * 2) if t < .5 else lerp(VIO, (255, 120, 240), (t - .5) * 2)

def draw_arm(d, cen, start, sign, col):
    x, y = cen; a0 = math.degrees(start); a1 = math.degrees(start + sign * math.pi)
    lo, hi = (a0, a1) if sign > 0 else (a1, a0)
    d.arc([x - AR - T / 2, y - AR - T / 2, x + AR + T / 2, y + AR + T / 2], lo, hi, fill=tuple(int(v * .8) for v in col), width=int(T))
    d.arc([x - AR - T / 8, y - AR - T / 8, x + AR + T / 8, y + AR + T / 8], lo, hi, fill=tuple(min(255, v + 100) for v in col), width=4)
    for a in (start, start + sign * math.pi):
        ex, ey = x + AR * math.cos(a), y + AR * math.sin(a)
        d.ellipse((ex - T / 2, ey - T / 2, ex + T / 2, ey + T / 2), fill=tuple(int(v * .8) for v in col))

def draw(fr, arms):
    light = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(light)
    d.ellipse((CX - R - 3, CY - R - 3, CX + R + 3, CY + R + 3), outline=(255, 120, 235), width=6)
    for u, (ta, tb, ca, cb) in zip(UNITS, arms):
        draw_arm(d, ca, ta + math.pi, +1, u["col"]); draw_arm(d, cb, tb + math.pi, -1, u["col"])
        gx, gy = u["g"]; rot = fr * 0.06 * (1 if u["spin"] > 0 else -1)
        pts = [(gx + (HUB + (8 if i % 2 == 0 else -4)) * math.cos(rot + i * math.pi / 8), gy + (HUB + (8 if i % 2 == 0 else -4)) * math.sin(rot + i * math.pi / 8)) for i in range(16)]
        d.polygon(pts, fill=tuple(min(255, v + 60) for v in u["col"])); d.ellipse((gx - 9, gy - 9, gx + 9, gy + 9), fill=(255, 255, 255))
    for x, y, age, col in ripples:
        rad = AR * (0.2 + age / 22); fade = max(0, 1 - age / 26)
        d.ellipse((x - rad, y - rad, x + rad, y + rad), outline=tuple(int(v * fade) for v in col), width=5)
    for (x, y), ci in zip(P, CI):
        c = ballcol(ci); d.ellipse((x - BR, y - BR, x + BR, y + BR), fill=c)
        d.ellipse((x - 4, y - 5, x, y - 1), fill=tuple(min(255, v + 110) for v in c))
    f = font(120); txt = str(len(P)); tw = d.textlength(txt, font=f)
    d.text((540 - tw / 2, 120), txt, font=f, fill=(255, 190, 245))
    f2 = font(38); lt = "BALLS"; d.text((540 - d.textlength(lt, font=f2) / 2, 262), lt, font=f2, fill=(255, 150, 200))
    return compose(sky.frame(fr), light)

def run(mode, pv):
    wr = Writer() if mode == "render" else None; log = {}; fr = 0; full = None
    while True:
        st = step(fr)
        if fr % 90 == 0: log[fr // 30] = len(P)
        if len(P) >= MAXB and full is None: full = fr
        if wr: wr.write(draw(fr, st))
        elif fr in pv: Image.fromarray(draw(fr, st)).save(f"t_{fr}.png")
        fr += 1
        if (full is not None and fr > full + 150) or fr >= DUR_MAX: break
    if wr:
        wr.close(); make_audio(fr, events); mux("video_tmp.mp4", "audio.wav", "dreifach_zahnrad.mp4")
    print(fr, log, len(P))

if __name__ == "__main__":
    run(sys.argv[1], {int(x) for x in sys.argv[2:]})
