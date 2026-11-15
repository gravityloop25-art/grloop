import sys, math, random
import numpy as np
from PIL import Image, ImageDraw
from common import *

CMD = sys.argv[1]; SEED = int(sys.argv[2]); G = float(sys.argv[3]); CAP = int(sys.argv[4]); HOLD = int(sys.argv[5])
PV = {int(x) for x in sys.argv[6:]}
rng = np.random.default_rng(SEED); random.seed(SEED)
X1, X2 = 130.0, 950.0; CW = (X2 - X1) / 3
NR = 8; Y0 = 520.0; DY = 135.0; YEND = Y0 + (NR - 1) * DY + 100
BR = 6.0; PR = 12.0; VMAX = 7.0; DUR_MAX = 50 * FPS
sky = Sky(99)
ROWS = [[2, 3, 2], [3, 2, 2], [2, 2, 3], [2, 2, 3], [2, 3, 2], [3, 2, 2], [2, 3, 2], [5, 2, 10]]
VCOL = {2: (60, 220, 255), 3: (170, 90, 255), 4: (255, 40, 220), 5: (255, 150, 60), 10: (255, 235, 150)}
BC = [(60, 220, 255), (255, 60, 220), (255, 160, 60), (160, 100, 255), (120, 255, 160)]
YG = [Y0 + k * DY for k in range(NR)]
PEGS = []
for k in range(NR):
    m = 5 if k % 2 else 6
    for x in np.linspace(X1 + 90, X2 - 90, m): PEGS.append((float(x), YG[k] + DY / 2))
P = np.array([[540.0, 450.0]]); V = np.zeros((1, 2)); CG = np.zeros(1, int)
COLL = 0; GF = np.zeros((NR, 3)); events = []; MAXTOT = 1

def step(fr):
    global P, V, CG, COLL, MAXTOT
    if fr < HOLD or len(P) == 0: return
    V[:, 1] = np.minimum(V[:, 1] + G, VMAX); old = P[:, 1].copy(); P += V
    l = P[:, 0] < X1 + BR; V[l, 0] = np.abs(V[l, 0]); P[l, 0] = X1 + BR
    r_ = P[:, 0] > X2 - BR; V[r_, 0] = -np.abs(V[r_, 0]); P[r_, 0] = X2 - BR
    for (px, py) in PEGS:
        m = np.abs(P[:, 1] - py) < PR + BR + 12
        if not m.any(): continue
        idx = np.where(m)[0]; dx = P[idx, 0] - px; dy = P[idx, 1] - py; dd = np.hypot(dx, dy) + 1e-9; hit = dd < PR + BR
        if hit.any():
            ii = idx[hit]; nx = dx[hit] / dd[hit]; ny = dy[hit] / dd[hit]
            P[ii, 0] = px + nx * (PR + BR); P[ii, 1] = py + ny * (PR + BR)
            vn = V[ii, 0] * nx + V[ii, 1] * ny; g = vn < 0
            V[ii[g], 0] -= 1.5 * vn[g] * nx[g]; V[ii[g], 1] -= 1.5 * vn[g] * ny[g]
            V[ii, 0] += rng.normal(0, 0.3, len(ii))
    ncross = 0; newP = []; newV = []; newC = []
    for k, yg in enumerate(YG):
        cross = (old < yg) & (P[:, 1] >= yg)
        if not cross.any(): continue
        idx = np.where(cross)[0]; cell = np.clip(((P[idx, 0] - X1) // CW).astype(int), 0, 2)
        for c in range(3):
            sel = idx[cell == c]
            if len(sel) == 0: continue
            val = ROWS[k][c]; GF[k, c] = 1.0; ncross += len(sel)
            room = CAP - len(P) - sum(len(x) for x in newP) - COLL
            for _ in range(val - 1):
                if room <= 0: break
                s2 = sel[:max(0, room)]
                newP.append(P[s2] + np.stack([rng.normal(0, 4, len(s2)), np.zeros(len(s2))], 1))
                newV.append(V[s2] + np.stack([rng.normal(0, 1.1, len(s2)), np.zeros(len(s2))], 1)); newC.append(CG[s2] + 1)
                room -= len(s2)
            CG[sel] += 1
    if newP:
        P = np.vstack([P] + newP); V = np.vstack([V] + newV); CG = np.concatenate([CG] + newC)
    done = P[:, 1] > YEND
    if done.any():
        COLL += int(done.sum()); P, V, CG = P[~done], V[~done], CG[~done]
    tot = len(P) + COLL; MAXTOT = max(MAXTOT, tot)
    if ncross: events.append((fr, "click", random.choice([0, 2, 4, 5, 7])))
    if ncross >= 10: events.append((fr, "pop", min(8, int(math.log10(max(tot, 1)) * 2))))

def draw(fr, endfr):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    wc = (255, 235, 250)
    d.line((X1 - 6, Y0 - 90, X1 - 6, YEND + 10), fill=wc, width=4); d.line((X2 + 6, Y0 - 90, X2 + 6, YEND + 10), fill=wc, width=4)
    for (px, py) in PEGS: d.ellipse((px - PR, py - PR, px + PR, py + PR), fill=(255, 235, 250))
    f = font(46)
    for k in range(NR):
        for c in range(3):
            val = ROWS[k][c]; col = VCOL[val]; fl = GF[k, c]
            x0 = X1 + c * CW + 6; x1 = X1 + (c + 1) * CW - 6
            fill = tuple(int(v * (.16 + .5 * fl)) for v in col)
            d.rectangle((x0, YG[k] - 26, x1, YG[k] + 26), fill=fill, outline=col, width=3)
            tx = f"x{val}"; d.text(((x0 + x1) / 2 - d.textlength(tx, font=f) / 2, YG[k] - 28), tx, font=f, fill=col if fl < .3 else (255, 255, 255))
    for (x, y), cg in zip(P, CG):
        col = BC[cg % 5]; d.ellipse((x - BR, y - BR, x + BR, y + BR), fill=col)
    f1 = font(66); t1 = "1 ball turns into"; t2 = "how many?"
    d.text((540 - d.textlength(t1, font=f1) / 2, 95), t1, font=f1, fill=(255, 240, 252))
    d.text((540 - d.textlength(t2, font=f1) / 2, 175), t2, font=f1, fill=(255, 240, 252))
    tot = len(P) + COLL
    f3 = font(130); tx = f"{tot:,}"; d.text((540 - d.textlength(tx, font=f3) / 2, 255), tx, font=f3, fill=(255, 200, 245))
    f4 = font(34); tx = "BALLS"; d.text((540 - d.textlength(tx, font=f4) / 2, 395), tx, font=f4, fill=(220, 180, 230))
    f5 = font(40); tx = f"{COLL:,} landed"; d.text((540 - d.textlength(tx, font=f5) / 2, YEND + 45), tx, font=f5, fill=(220, 200, 235))
    if endfr is not None and fr >= endfr:
        q = fr - endfr; f6 = font(96); tx = f"{tot:,} BALLS!"
        d.rectangle((0, 640, W, 790), fill=(0, 0, 0))
        if q % 14 < 10 or q > 40: d.text((540 - d.textlength(tx, font=f6) / 2, 665), tx, font=f6, fill=(255, 250, 210))
    return compose(sky.frame(fr), img, .6, .5, .28)

def run():
    wr = Writer() if CMD == "render" else None; fr = 0; endfr = None; log = {}
    while True:
        step(fr); GF[:] *= 0.86
        if endfr is None and fr > HOLD + 5 and len(P) == 0: endfr = fr; events.append((fr, "fin", 0))
        if fr % 90 == 0: log[fr // 30] = (len(P) + COLL, len(P))
        if wr: wr.write(draw(fr, endfr))
        elif CMD == "preview" and fr in PV: Image.fromarray(draw(fr, endfr)).save(f"p_{fr}.png")
        fr += 1
        if (endfr is not None and fr > endfr + 105) or fr >= DUR_MAX: break
    if wr:
        wr.close(); make_audio(fr, events); mux("video_tmp.mp4", "audio.wav", "tore.mp4")
    print(SEED, G, CAP, "end", endfr and round(endfr / 30, 1), "total", len(P) + COLL, log)

run()
