import sys, math, random
import numpy as np
from PIL import Image, ImageDraw
from common import *

CMD = sys.argv[1]; SEED = int(sys.argv[2]); HPM = float(sys.argv[3]); SPD = float(sys.argv[4]); NB0 = int(sys.argv[5])
PV = {int(x) for x in sys.argv[6:]}
rng = np.random.default_rng(SEED); random.seed(SEED)
AX1, AX2, AY1, AY2 = 140.0, 940.0, 450.0, 1450.0
NC, NR = 10, 20; BW = (AX2 - AX1) / NC; BH = 22.0; BY0 = AY1 + 20
BR = 9.0; SUB = 4; CAP = 500; GHOST = 8; TLIM = 30.0
BC = [(60, 220, 255), (255, 60, 220), (255, 160, 60), (160, 100, 255), (120, 255, 160)]
HCOL = {1: (60, 220, 255), 2: (170, 90, 255), 3: (255, 40, 220)}
sky = Sky(131)
HP = np.ones((NR, NC), int); rr_ = rng.uniform(0, 1, (NR, NC)); HP[rr_ < HPM] = 2; HP[rr_ < HPM * 0.35] = 3
FLB = np.zeros((NR, NC)); TOTAL = NR * NC
ang0 = -math.pi / 2 + rng.uniform(-0.6, 0.6, NB0)
P = np.stack([rng.uniform(AX1 + 100, AX2 - 100, NB0), np.full(NB0, AY2 - 60.0)], 1)
V = SPD * np.stack([np.cos(ang0), np.sin(ang0)], 1); GH = np.zeros(NB0); CI = np.arange(NB0) % 5
events = []

def rot(v, a):
    c, s = math.cos(a), math.sin(a)
    return np.stack([v[:, 0] * c - v[:, 1] * s, v[:, 0] * s + v[:, 1] * c], 1)

def step(fr):
    global P, V, GH, CI
    nb = 0; broke = 0
    for _ in range(SUB):
        P += V / SUB
        l = P[:, 0] < AX1 + BR; V[l, 0] = np.abs(V[l, 0]); P[l, 0] = AX1 + BR
        r_ = P[:, 0] > AX2 - BR; V[r_, 0] = -np.abs(V[r_, 0]); P[r_, 0] = AX2 - BR
        t = P[:, 1] < AY1 + BR; V[t, 1] = np.abs(V[t, 1]); P[t, 1] = AY1 + BR
        b = P[:, 1] > AY2 - BR; V[b, 1] = -np.abs(V[b, 1]); P[b, 1] = AY2 - BR
        hitany = np.zeros(len(P), bool)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            px = P[:, 0] + dx * BR; py = P[:, 1] + dy * BR
            ci = np.floor((px - AX1) / BW).astype(int); ri = np.floor((py - BY0) / BH).astype(int)
            ok = (ci >= 0) & (ci < NC) & (ri >= 0) & (ri < NR)
            ci2 = np.clip(ci, 0, NC - 1); ri2 = np.clip(ri, 0, NR - 1)
            ok &= HP[ri2, ci2] > 0
            ok &= (dx * V[:, 0] > 0) if dx else (dy * V[:, 1] > 0)
            idx = np.where(ok)[0]
            if len(idx) == 0: continue
            if dx: V[idx, 0] = -V[idx, 0]
            else: V[idx, 1] = -V[idx, 1]
            for (a_, b_) in set(zip(ri2[idx].tolist(), ci2[idx].tolist())):
                if HP[a_, b_] > 0:
                    HP[a_, b_] -= 1; FLB[a_, b_] = 1.0
                    if HP[a_, b_] == 0: broke += 1
            hitany[idx] = True
        cand = np.where(hitany & (GH <= 0))[0]; cand = cand[:max(0, CAP - len(P))]
        if len(cand):
            a = 0.4; nv = rot(V[cand], -a); V[cand] = rot(V[cand], a); CI[cand] += 1; GH[cand] = GHOST
            P = np.vstack([P, P[cand] + rng.normal(0, 1.2, (len(cand), 2))]); V = np.vstack([V, nv])
            GH = np.concatenate([GH, np.full(len(cand), GHOST)]); CI = np.concatenate([CI, CI[cand]]); nb += len(cand)
    GH -= 1
    if nb: events.append((fr, "click", random.choice([1, 3, 4, 6])))
    if broke: events.append((fr, "pop", min(8, (TOTAL - int((HP > 0).sum())) * 9 // TOTAL)))

def draw(fr, endfr, win):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    d.rectangle((AX1 - 5, AY1 - 5, AX2 + 5, AY2 + 5), outline=(255, 235, 250), width=5)
    for r in range(NR):
        for c in range(NC):
            x0 = AX1 + c * BW; y0 = BY0 + r * BH; fl = FLB[r, c]
            if HP[r, c] > 0:
                col = HCOL[int(HP[r, c])]
                fill = tuple(int(v * (.2 + .6 * fl)) for v in col)
                d.rectangle((x0 + 2, y0 + 2, x0 + BW - 2, y0 + BH - 2), fill=fill, outline=col if fl < .3 else (255, 255, 255), width=2)
            elif fl > .05:
                k = int(255 * fl); d.rectangle((x0 + 2, y0 + 2, x0 + BW - 2, y0 + BH - 2), fill=(k, k, k))
    for (x, y), c in zip(P, CI):
        col = BC[c % 5]; d.ellipse((x - BR, y - BR, x + BR, y + BR), fill=col)
        d.ellipse((x - 5, y - 7, x, y - 2), fill=tuple(min(255, v + 110) for v in col))
    f = font(66); t1 = "Can they break"; t2 = "200 bricks in 30s?"
    d.text((540 - d.textlength(t1, font=f) / 2, 95), t1, font=f, fill=(255, 240, 252))
    d.text((540 - d.textlength(t2, font=f) / 2, 175), t2, font=f, fill=(255, 240, 252))
    left = max(0.0, TLIM - fr / FPS); k = left / TLIM
    tc = lerp((255, 60, 60), (120, 255, 170), k) if k > .3 else (255, 60, 60)
    if left < 5 and (fr // 8) % 2: tc = (255, 255, 255)
    f2 = font(110); tx = f"{left:.1f}s"; d.text((540 - d.textlength(tx, font=f2) / 2, 262), tx, font=f2, fill=tc)
    broken = TOTAL - int((HP > 0).sum())
    f3 = font(66); tx = f"BRICKS {broken} / {TOTAL}"; d.text((540 - d.textlength(tx, font=f3) / 2, AY2 + 45), tx, font=f3, fill=(255, 200, 245))
    bw = 760; by = AY2 + 135
    d.rectangle((540 - bw / 2, by, 540 + bw / 2, by + 18), outline=(140, 70, 130), width=2)
    d.rectangle((540 - bw / 2, by, 540 - bw / 2 + bw * broken / TOTAL, by + 18), fill=(255, 60, 200))
    f4 = font(34); tx = f"{len(P)} balls  -  every hit splits a ball"; d.text((540 - d.textlength(tx, font=f4) / 2, by + 40), tx, font=f4, fill=(210, 190, 225))
    if endfr is not None and fr >= endfr:
        q = fr - endfr; f6 = font(100); tx = ("JUST IN TIME!" if left < 3 else "WALL BROKEN!") if win else "TIME'S UP!"
        d.rectangle((0, 1000 - 85, W, 1000 + 85), fill=(0, 0, 0))
        if q % 14 < 10 or q > 40: d.text((540 - d.textlength(tx, font=f6) / 2, 1000 - 60), tx, font=f6, fill=(255, 250, 210) if win else (255, 90, 90))
    return compose(sky.frame(fr), img, .7, .55, .3)

def run():
    wr = Writer() if CMD == "render" else None; fr = 0; endfr = None; win = None; log = {}
    while True:
        FLB[:] *= 0.84
        if endfr is None: step(fr)
        if endfr is None:
            if (HP > 0).sum() == 0: endfr = fr; win = True; events.append((fr, "fin", 0))
            elif fr / FPS >= TLIM: endfr = fr; win = False
        if fr % 90 == 0: log[fr // 30] = (len(P), TOTAL - int((HP > 0).sum()))
        if wr: wr.write(draw(fr, endfr, win))
        elif CMD == "preview" and fr in PV: Image.fromarray(draw(fr, endfr, win)).save(f"p_{fr}.png")
        fr += 1
        if (endfr is not None and fr > endfr + 105) or fr >= 40 * FPS: break
    if wr:
        wr.close(); make_audio(fr, events); mux("video_tmp.mp4", "audio.wav", "ziegelmauer.mp4")
    print(SEED, HPM, SPD, NB0, "end", endfr and round(endfr / 30, 1), win, log)

run()
