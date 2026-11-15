import sys, math, random
import numpy as np
from PIL import Image, ImageDraw
from common import *

CMD = sys.argv[1]; SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 5
PCONV = float(sys.argv[3]) if len(sys.argv) > 3 else 0.3
PV = {int(x) for x in sys.argv[4:]}
random.seed(SEED); rng = np.random.default_rng(SEED)
CX, CY, R = 540.0, 1000.0, 470.0
BR = 13.0; SPEED = 7.0; SUB = 3; NPER = 50; DUR_MAX = 46 * FPS
COLS = [(255, 40, 220), (255, 150, 60), (60, 220, 255), (150, 90, 255)]
NAMES = ["PINK", "ORANGE", "CYAN", "PURPLE"]
sky = Sky(31)

# start: 4 quadrant clusters
P = []; C = []
for c, (sx, sy) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)]):
    k = 0
    while k < NPER:
        x = CX + sx * rng.uniform(40, 330); y = CY + sy * rng.uniform(40, 330)
        if math.hypot(x - CX, y - CY) > R - 30: continue
        if P and np.min(np.hypot(np.array(P)[:, 0] - x, np.array(P)[:, 1] - y)) < 2 * BR + 2: continue
        P.append((x, y)); C.append(c); k += 1
P = np.array(P); C = np.array(C)
a = rng.uniform(0, 2 * np.pi, len(P)); V = SPEED * np.stack([np.cos(a), np.sin(a)], 1)
FL = np.zeros(len(P))
events = []
# central spinning bar (bounce obstacle)
BL, BW = 150.0, 14.0

def bar(t):
    al = 0.012 * t; return al, 0.012

def step(fr):
    global P, V
    conv = 0; hits = 0
    n = len(P)
    for sub in range(SUB):
        P += V / SUB
        # wall
        rel = P - [CX, CY]; d = np.hypot(rel[:, 0], rel[:, 1]); out = d > R - BR
        if out.any():
            nn = rel[out] / d[out, None]; vn = (V[out] * nn).sum(1); Vo = V[out]; g = vn > 0
            Vo[g] -= 2 * vn[g, None] * nn[g]; V[out] = Vo; P[out] = np.array([CX, CY]) + nn * (R - BR)
        # bar (segment through center, both directions)
        al, w = bar(fr + (sub + 1) / SUB)
        u = np.array([math.cos(al), math.sin(al)])
        s = np.clip(rel @ u, -BL, BL); q = np.array([CX, CY]) + s[:, None] * u
        dv = P - q; dd = np.hypot(dv[:, 0], dv[:, 1]) + 1e-9; hit = dd < BR + BW / 2
        if hit.any():
            nn = dv[hit] / dd[hit, None]; P[hit] = q[hit] + nn * (BR + BW / 2)
            r = P[hit] - [CX, CY]; vo = w * np.stack([-r[:, 1], r[:, 0]], 1)
            vn = ((V[hit] - vo) * nn).sum(1); Vh = V[hit]; g = vn < 0
            Vh[g] -= 2 * vn[g, None] * nn[g]; V[hit] = Vh
        # ball-ball
        dx = P[:, None, :] - P[None, :, :]; dist = np.hypot(dx[..., 0], dx[..., 1])
        iu, ju = np.where(np.triu(dist < 2 * BR, 1))
        for i, j in zip(iu, ju):
            dvec = P[i] - P[j]; dd = math.hypot(*dvec) + 1e-9; nn = dvec / dd
            rv = (V[i] - V[j]) @ nn
            ov = 2 * BR - dd; P[i] += nn * ov / 2; P[j] -= nn * ov / 2
            if rv < 0:
                V[i] -= rv * nn; V[j] += rv * nn; hits += 1
                if C[i] != C[j] and random.random() < PCONV:
                    ni = (C == C[i]).sum(); nj = (C == C[j]).sum()
                    pa = ni ** 1.5 / (ni ** 1.5 + nj ** 1.5)
                    if random.random() < pa: C[j] = C[i]; FL[j] = 1
                    else: C[i] = C[j]; FL[i] = 1
                    conv += 1
    sp = np.hypot(V[:, 0], V[:, 1]) + 1e-9; V *= (SPEED / sp)[:, None]
    if conv: events.append((fr, "click", random.choice([0, 2, 4, 5, 7])))
    if conv >= 3: events.append((fr, "pop", 3))
    return conv

def draw(fr, cnt, endfr, winner):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    d.ellipse((CX - R - 4, CY - R - 4, CX + R + 4, CY + R + 4), outline=(255, 235, 250), width=5)
    al, _ = bar(fr); u = np.array([math.cos(al), math.sin(al)]); v = np.array([-u[1], u[0]])
    cs = [tuple(np.array([CX, CY]) + a * BL * u + b * BW / 2 * v) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    d.polygon(cs, fill=(60, 50, 70), outline=(255, 230, 250)); d.ellipse((CX - 12, CY - 12, CX + 12, CY + 12), fill=(255, 255, 255))
    for (x, y), c, fl in zip(P, C, FL):
        col = COLS[c]
        if fl > 0.05: d.ellipse((x - BR - 6 * fl, y - BR - 6 * fl, x + BR + 6 * fl, y + BR + 6 * fl), fill=(255, 255, 255))
        d.ellipse((x - BR, y - BR, x + BR, y + BR), fill=col)
        d.ellipse((x - 5, y - 7, x, y - 2), fill=tuple(min(255, k + 120) for k in col))
    f = font(76); t1 = "Which color"; t2 = "takes over?"
    d.text((540 - d.textlength(t1, font=f) / 2, 105), t1, font=f, fill=(255, 240, 252))
    d.text((540 - d.textlength(t2, font=f) / 2, 195), t2, font=f, fill=(255, 240, 252))
    f2 = font(36); s = "every crash can flip a color"
    d.text((540 - d.textlength(s, font=f2) / 2, 300), s, font=f2, fill=(220, 200, 230))
    by = CY + R + 70; bw = 210; gx = 30; f3 = font(54); f4 = font(24); tot = len(P)
    for c in range(4):
        x = 75 + c * (bw + gx); p = cnt[c] / tot
        d.rectangle((x, by, x + bw, by + 18), outline=tuple(int(k * .6) for k in COLS[c]), width=2)
        d.rectangle((x, by, x + bw * p, by + 18), fill=COLS[c])
        tx = str(cnt[c]) if cnt[c] else "OUT"
        d.text((x + bw / 2 - d.textlength(tx, font=f3) / 2, by + 30), tx, font=f3, fill=COLS[c] if cnt[c] else (120, 110, 120))
        d.text((x + bw / 2 - d.textlength(NAMES[c], font=f4) / 2, by + 95), NAMES[c], font=f4, fill=tuple(int(k * .8) for k in COLS[c]))
    if endfr is not None and fr >= endfr:
        k = fr - endfr; f5 = font(100); tx = f"{NAMES[winner]} WINS!"; tw = d.textlength(tx, font=f5)
        if k % 14 < 10 or k > 40: d.text((540 - tw / 2, 400), tx, font=f5, fill=COLS[winner])
    return compose(sky.frame(fr), img, .6, .5, .3)

def run():
    wr = Writer() if CMD == "render" else None; fr = 0; endfr = None; winner = None; log = {}
    while True:
        step(fr); FL[:] *= 0.85
        cnt = [int((C == c).sum()) for c in range(4)]
        if endfr is None and max(cnt) == len(P):
            winner = int(np.argmax(cnt)); endfr = fr; events.append((fr, "fin", 0))
        if fr % 90 == 0: log[fr // 30] = cnt
        if wr: wr.write(draw(fr, cnt, endfr, winner))
        elif CMD == "preview" and fr in PV: Image.fromarray(draw(fr, cnt, endfr, winner)).save(f"p_{fr}.png")
        fr += 1
        if (endfr is not None and fr > endfr + 120) or fr >= DUR_MAX: break
    if wr:
        wr.close(); make_audio(fr, events); mux("video_tmp.mp4", "audio.wav", "farbkrieg.mp4")
    print("seed", SEED, PCONV, "frames", fr, round(fr / 30, 1), "end", endfr and round(endfr / 30, 1), winner, log)

run()
