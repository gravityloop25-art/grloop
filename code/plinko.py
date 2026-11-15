import sys, math, random
import numpy as np
from PIL import Image, ImageDraw
from common import *

random.seed(9); np.random.seed(9)
BR, PR = 9.0, 9.0
ROWS = 13
pegs = []; prow = []
for r in range(ROWS):
    y = 480 + r * 82
    off = 0 if r % 2 == 0 else 45
    for c in range(12 if r % 2 == 0 else 11):
        pegs.append((90 + off + c * 90, y)); prow.append(r)
PEG = np.array(pegs, float); PROW = np.array(prow)
MULT = np.isin(PROW, [3, 7, 11])
NB = 12; BIN_X0 = 0; BIN_W = W / NB
BIN_TOP, BIN_BOT = 1575, 1860
CAP = 70
GRAV, VMAX = 0.5, 17.0
MAXB = 1100
SPAWN_END = 20 * FPS
sky = Sky(31)

P = np.zeros((0, 2)); V = np.zeros((0, 2)); G = np.zeros(0, int); CD = np.zeros(0, int)
total = 0; bins = np.zeros(NB, int); pflash = np.zeros(len(PEG)); events = []
fin_fr = None; binflash = 0.0

def spawn(x, y, vx, vy, g):
    global P, V, G, CD, total
    P = np.vstack([P, [x, y]]); V = np.vstack([V, [vx, vy]]); G = np.append(G, g); CD = np.append(CD, 0); total += 1

def step(fr):
    global P, V, G, CD, bins, pflash, fin_fr, binflash
    pflash *= 0.86
    if fr < SPAWN_END and fr % 5 == 0 and total < MAXB:
        spawn(540 + random.uniform(-70, 70), 380, random.uniform(-1.5, 1.5), 2, 0)
    SUB = 2
    for _ in range(SUB):
        if len(P) == 0: break
        V[:, 1] += GRAV / SUB
        sp = np.hypot(V[:, 0], V[:, 1]); V *= np.minimum(1, VMAX / np.maximum(sp, 1e-6))[:, None]
        P = P + V / SUB
        # walls
        lw = P[:, 0] < BR; V[lw, 0] = abs(V[lw, 0]); P[lw, 0] = BR
        rw = P[:, 0] > W - BR; V[rw, 0] = -abs(V[rw, 0]); P[rw, 0] = W - BR
        # pegs (only balls in peg area)
        sel = np.where((P[:, 1] > 440) & (P[:, 1] < 1480))[0]
        if len(sel):
            D = P[sel, None, :] - PEG[None, :, :]
            dist = np.hypot(D[..., 0], D[..., 1])
            j = dist.argmin(1); dm = dist[np.arange(len(sel)), j]
            hit = dm < BR + PR
            for k in np.where(hit)[0]:
                i = sel[k]; pj = j[k]
                nvec = D[k, pj] / max(dm[k], 1e-6)
                vn = V[i, 0] * nvec[0] + V[i, 1] * nvec[1]
                if vn < 0:
                    V[i] -= 1.55 * vn * nvec
                    V[i, 0] += random.uniform(-0.6, 0.6)
                    P[i] = PEG[pj] + nvec * (BR + PR + 0.5)
                    pflash[pj] = 1.0
                    if random.random() < 0.5: events.append((fr, "click", int(PROW[pj] + (pj % 3))))
                    if MULT[pj] and CD[i] == 0 and total < MAXB:
                        CD[i] = 12
                        a = random.uniform(-0.9, 0.9)
                        spawn(P[i, 0], P[i, 1], V[i, 0] + 5 * math.cos(a + 1.57) * random.choice([-1, 1]), V[i, 1] * 0.5, G[i] + 1)
                        CD[-1] = 12
                        events.append((fr, "pop", int(PROW[pj] // 3)))
    CD = np.maximum(0, CD - 1)
    if len(P):
        done = P[:, 1] > BIN_TOP + 20
        if done.any():
            for i in np.where(done)[0]:
                b = min(NB - 1, max(0, int(P[i, 0] // BIN_W))); bins[b] += 1
                if random.random() < 0.4: events.append((fr, "click", 8))
            P, V, G, CD = P[~done], V[~done], G[~done], CD[~done]
    if fr > SPAWN_END and len(P) == 0 and fin_fr is None:
        fin_fr = fr; events.append((fr, "fin", 0))

def ballcol(g):
    return [(80, 230, 255), (120, 160, 255), (170, 110, 255), (230, 100, 240), (255, 130, 190), (255, 160, 120)][min(g, 5)]

def draw(fr):
    light = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(light)
    for i in range(len(PEG)):
        x, y = PEG[i]; f = pflash[i]
        base = (255, 70, 200) if MULT[i] else (70, 170, 255)
        c = tuple(min(255, int(v * (0.75 if MULT[i] else 0.5) + 170 * f)) for v in base)
        d.ellipse((x - PR + 2, y - PR + 2, x + PR - 2, y + PR - 2), fill=c)
        if MULT[i]: d.ellipse((x - PR - 3, y - PR - 3, x + PR + 3, y + PR + 3), outline=tuple(int(v * 0.6) for v in (255, 150, 90)), width=2)
    # bins
    pulse = 0.0 if fin_fr is None else max(0, 1 - (fr - fin_fr) / 40)
    for b in range(NB + 1):
        x = b * BIN_W
        d.line((x, BIN_TOP, x, BIN_BOT), fill=(200, 60, 190), width=3)
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
        c = ballcol(G[i]); x, y = P[i]
        d.ellipse((x - BR, y - BR, x + BR, y + BR), fill=c)
        d.ellipse((x - 4, y - 5, x, y - 1), fill=tuple(min(255, v + 110) for v in c))
    f = font(120); txt = str(total); tw = d.textlength(txt, font=f)
    d.text((540 - tw / 2, 150), txt, font=f, fill=(255, 190, 245))
    f2 = font(38); lt = "BALLS"; d.text((540 - d.textlength(lt, font=f2) / 2, 292), lt, font=f2, fill=(255, 150, 200))
    return compose(sky.frame(fr), light)

def run(mode, pv):
    wr = Writer() if mode == "render" else None
    fr = 0; log = {}
    while True:
        step(fr)
        if fr % 30 == 0: log[fr // 30] = (total, len(P))
        if wr: wr.write(draw(fr))
        elif fr in pv: Image.fromarray(draw(fr)).save(f"k_{fr}.png")
        fr += 1
        if (fin_fr is not None and fr > fin_fr + 75) or fr > 1800: break
    if wr:
        wr.close(); make_audio(fr, events); mux("video_tmp.mp4", "audio.wav", "plinko_neon.mp4")
    print(fr, log, bins)

if __name__ == "__main__":
    run(sys.argv[1], {int(x) for x in sys.argv[2:]})
