import sys, math, random
import numpy as np
from PIL import Image, ImageDraw
from common import *

random.seed(17); np.random.seed(17)
BR = 9.0
GR_BODY, GR_TOOTH_R, GR_RING, NT = 70.0, 14.0, 86.0, 10
GCEN = [(270, 600, 1), (810, 600, -1), (540, 790, 1), (270, 980, -1), (810, 980, 1), (540, 1170, -1), (270, 1360, 1), (810, 1360, -1)]
PINK = {2, 5, 6}                     # splitting gears
WOM = 0.045
NG = len(GCEN)
NC = NG * (NT + 1)                    # collision circles: per gear NT teeth + body
CR = np.zeros(NC); CP = np.zeros((NC, 2)); CV = np.zeros((NC, 2)); CG = np.zeros(NC, int); ISTOOTH = np.zeros(NC, bool)
for g in range(NG):
    for k in range(NT + 1):
        i = g * (NT + 1) + k; CG[i] = g
        if k == NT: CR[i] = GR_BODY
        else: CR[i] = GR_TOOTH_R; ISTOOTH[i] = True
def update_gears(fr):
    for g, (gx, gy, s) in enumerate(GCEN):
        rot = s * WOM * fr + g * 0.4
        for k in range(NT):
            i = g * (NT + 1) + k; a = rot + k * 2 * math.pi / NT
            CP[i] = (gx + GR_RING * math.cos(a), gy + GR_RING * math.sin(a))
            CV[i] = (-s * WOM * GR_RING * math.sin(a), s * WOM * GR_RING * math.cos(a))
        i = g * (NT + 1) + NT; CP[i] = (gx, gy); CV[i] = (0, 0)

NB = 6; BIN_W = W / NB; BIN_TOP, BIN_BOT = 1600, 1860; CAP = 220
GRAV, VMAX = 0.5, 17.0; MAXB = 1000; SPAWN_END = 17 * FPS
sky = Sky(71)
P = np.zeros((0, 2)); V = np.zeros((0, 2)); GEN = np.zeros(0, int); CD = np.zeros(0, int)
total = 0; bins = np.zeros(NB, int); gflash = np.zeros(NG); events = []; fin_fr = None

def spawn(x, y, vx, vy, g):
    global P, V, GEN, CD, total
    P = np.vstack([P, [x, y]]); V = np.vstack([V, [vx, vy]]); GEN = np.append(GEN, g); CD = np.append(CD, 0); total += 1

def step(fr):
    global P, V, GEN, CD, bins, fin_fr
    update_gears(fr); gflash[:] *= 0.88
    if fr < SPAWN_END and fr % 5 == 0 and total < MAXB:
        spawn(random.choice([540, 270, 810]) + random.uniform(-90, 90), 330, random.uniform(-1.5, 1.5), 2, 0)
    SUB = 2
    for _ in range(SUB):
        if len(P) == 0: break
        V[:, 1] += GRAV / SUB
        sp = np.hypot(V[:, 0], V[:, 1]); V *= np.minimum(1, VMAX / np.maximum(sp, 1e-6))[:, None]
        P = P + V / SUB
        lw = P[:, 0] < BR; V[lw, 0] = abs(V[lw, 0]); P[lw, 0] = BR
        rw = P[:, 0] > W - BR; V[rw, 0] = -abs(V[rw, 0]); P[rw, 0] = W - BR
        sel = np.where((P[:, 1] > 440) & (P[:, 1] < 1500))[0]
        if len(sel):
            D = P[sel, None, :] - CP[None, :, :]
            dist = np.hypot(D[..., 0], D[..., 1]); pen = dist - (BR + CR[None, :])
            j = pen.argmin(1); pm = pen[np.arange(len(sel)), j]
            for k in np.where(pm < 0)[0]:
                i = sel[k]; c = j[k]
                nvec = D[k, c] / max(dist[k, c], 1e-6)
                vrel = V[i] - CV[c]; vn = vrel @ nvec
                if vn < 0:
                    V[i] = CV[c] + vrel - 1.65 * vn * nvec
                    V[i, 0] += random.uniform(-0.5, 0.5)
                    P[i] = CP[c] + nvec * (BR + CR[c] + 0.5)
                    g = CG[c]; gflash[g] = 1.0
                    if random.random() < 0.5: events.append((fr, "click", int(g * 2 + (c % 3))))
                    if g in PINK and ISTOOTH[c] and CD[i] == 0 and total < MAXB:
                        CD[i] = 14; a = random.choice([-1, 1])
                        spawn(P[i, 0], P[i, 1], V[i, 0] + a * 5, V[i, 1] * 0.5, GEN[i] + 1); CD[-1] = 14
                        events.append((fr, "pop", int(g)))
    CD = np.maximum(0, CD - 1)
    if len(P):
        done = P[:, 1] > BIN_TOP + 20
        if done.any():
            for i in np.where(done)[0]:
                b = min(NB - 1, max(0, int(P[i, 0] // BIN_W))); bins[b] += 1
                if random.random() < 0.4: events.append((fr, "click", 8))
            P, V, GEN, CD = P[~done], V[~done], GEN[~done], CD[~done]
    if fr > SPAWN_END and len(P) == 0 and fin_fr is None:
        fin_fr = fr; events.append((fr, "fin", 0))

def ballcol(g): return [(80, 230, 255), (120, 160, 255), (170, 110, 255), (230, 100, 240), (255, 130, 190), (255, 160, 120)][min(g, 5)]

def draw(fr):
    light = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(light)
    for g, (gx, gy, s) in enumerate(GCEN):
        base = (255, 60, 210) if g in PINK else (60, 200, 255); f = gflash[g]
        c = tuple(min(255, int(v * 0.8 + 140 * f)) for v in base)
        d.ellipse((gx - GR_BODY, gy - GR_BODY, gx + GR_BODY, gy + GR_BODY), outline=c, width=5)
        rot = s * WOM * fr + g * 0.4
        for k in range(NT):
            a = rot + k * 2 * math.pi / NT; x, y = gx + GR_RING * math.cos(a), gy + GR_RING * math.sin(a)
            d.ellipse((x - GR_TOOTH_R, y - GR_TOOTH_R, x + GR_TOOTH_R, y + GR_TOOTH_R), fill=c)
        d.ellipse((gx - 8, gy - 8, gx + 8, gy + 8), fill=tuple(min(255, v + 90) for v in c))
        d.line((gx, gy, gx + (GR_BODY - 6) * math.cos(rot), gy + (GR_BODY - 6) * math.sin(rot)), fill=c, width=3)
    pulse = 0.0 if fin_fr is None else max(0, 1 - (fr - fin_fr) / 40)
    for b in range(NB + 1): d.line((b * BIN_W, BIN_TOP, b * BIN_W, BIN_BOT), fill=(200, 60, 190), width=3)
    d.line((0, BIN_BOT, W, BIN_BOT), fill=(255, 120, 150), width=4)
    for b in range(NB):
        h = min(1.0, bins[b] / CAP) * (BIN_BOT - BIN_TOP - 10)
        if h > 2:
            x0 = b * BIN_W + 8; x1 = (b + 1) * BIN_W - 8
            for k in range(int(h // 6)):
                y = BIN_BOT - 8 - k * 6; t = k * 6 / (BIN_BOT - BIN_TOP)
                c = lerp(MAG, ORA, t); c = tuple(min(255, int(v * (0.9 + 0.4 * pulse))) for v in c)
                d.line((x0, y, x1, y), fill=c, width=3)
    for i in range(len(P)):
        c = ballcol(GEN[i]); x, y = P[i]
        d.ellipse((x - BR, y - BR, x + BR, y + BR), fill=c)
        d.ellipse((x - 4, y - 5, x, y - 1), fill=tuple(min(255, v + 110) for v in c))
    f = font(120); txt = str(total); tw = d.textlength(txt, font=f)
    d.text((540 - tw / 2, 150), txt, font=f, fill=(255, 190, 245))
    f2 = font(38); lt = "BALLS"; d.text((540 - d.textlength(lt, font=f2) / 2, 292), lt, font=f2, fill=(255, 150, 200))
    return compose(sky.frame(fr), light)

def run(mode, pv):
    wr = Writer() if mode == "render" else None; fr = 0; log = {}
    while True:
        step(fr)
        if fr % 30 == 0: log[fr // 30] = (total, len(P))
        if wr: wr.write(draw(fr))
        elif fr in pv: Image.fromarray(draw(fr)).save(f"q_{fr}.png")
        fr += 1
        if (fin_fr is not None and fr > fin_fr + 75) or fr > 2000: break
    if wr:
        wr.close(); make_audio(fr, events); mux("video_tmp.mp4", "audio.wav", "zahnrad_plinko.mp4")
    print(fr, {k: v for k, v in log.items() if k % 3 == 0}, bins)

if __name__ == "__main__":
    run(sys.argv[1], {int(x) for x in sys.argv[2:]})
