import sys, math, random
import numpy as np
from PIL import Image, ImageDraw
from common import *

CMD = sys.argv[1]; SEED = int(sys.argv[2]); NSEG = int(sys.argv[3]); HP0 = int(sys.argv[4])
PV = {int(x) for x in sys.argv[5:]}
random.seed(SEED); np.random.seed(SEED)
CX, CY, R = 540.0, 1010.0, 470.0
RW = 26  # ring thickness
BR = 9.0; SPEED = 9.5; SUB = 4; MAXB = 700; GHOST = 10; DUR_MAX = 46 * FPS
HPCOL = {5: (60, 220, 255), 4: (150, 90, 255), 3: (255, 40, 220), 2: (255, 150, 70), 1: (255, 70, 60)}
sky = Sky(44)
HP = np.random.randint(max(1, HP0 // 4), HP0 * 2, NSEG); HPM = HP.copy(); FL = np.zeros(NSEG); BROKE = np.full(NSEG, -999)
a0 = random.uniform(0, 6.28)
NB0 = int(sys.argv[5]); PV = {int(x) for x in sys.argv[6:]}
aa = a0 + np.arange(NB0) * 2 * np.pi / NB0
P = np.stack([CX + 0 * aa, CY - 0 * aa], 1) + np.random.normal(0, 2, (NB0, 2)); V = SPEED * np.stack([np.cos(aa), np.sin(aa)], 1); GH = np.zeros(NB0)
CI = np.zeros(NB0, int)
EP = np.zeros((0, 2)); EV = np.zeros((0, 2)); EC = np.zeros(0, int); EA = np.zeros(0)
events = []; escaped = 0

def rot(v, a):
    c, s = math.cos(a), math.sin(a)
    return np.stack([v[:, 0] * c - v[:, 1] * s, v[:, 0] * s + v[:, 1] * c], 1)

def step(fr):
    global P, V, GH, CI, EP, EV, EC, EA, escaped
    nh = 0; nb = 0
    for _ in range(SUB):
        P += V / SUB
        rel = P - [CX, CY]; d = np.hypot(rel[:, 0], rel[:, 1]); out = np.where(d > R - RW - BR)[0]
        if len(out):
            ang = np.arctan2(rel[out, 1], rel[out, 0]) % (2 * np.pi); sg = (ang / (2 * np.pi) * NSEG).astype(int) % NSEG
            n = rel[out] / d[out, None]; vn = (V[out] * n).sum(1)
            alive = HP[sg] > 0
            # escape
            esc = out[~alive & (d[out] > R - RW + 2)]
            # bounce
            bi = out[alive & (vn > 0)]; bs = sg[alive & (vn > 0)]; bn = n[alive & (vn > 0)]; bv = vn[alive & (vn > 0)]
            if len(bi):
                V[bi] -= 2 * bv[:, None] * bn; P[bi] = np.array([CX, CY]) + bn * (R - RW - BR)
                for i, s in zip(bi, bs):
                    if GH[i] <= 0 and HP[s] > 0:
                        HP[s] -= 1; FL[s] = 1; nh += 1
                        if HP[s] == 0: BROKE[s] = fr; nb += 1
                cand = bi[GH[bi] <= 0]
                cand = cand[:max(0, MAXB - len(P))]
                if len(cand):
                    a = 0.45; nv = rot(V[cand], -a); V[cand] = rot(V[cand], a)
                    np_ = P[cand] + np.random.normal(0, 1.2, (len(cand), 2)); CI[cand] += 1
                    GH[cand] = GHOST
                    P = np.vstack([P, np_]); V = np.vstack([V, nv]); GH = np.concatenate([GH, np.full(len(cand), GHOST)])
                    CI = np.concatenate([CI, CI[cand]])
            if len(esc):
                keep = np.ones(len(P), bool); keep[esc] = False
                EP = np.vstack([EP, P[esc]]); EV = np.vstack([EV, V[esc] * 1.1]); EC = np.concatenate([EC, CI[esc]]); EA = np.concatenate([EA, np.zeros(len(esc))])
                escaped += len(esc)
                P, V, GH, CI = P[keep], V[keep], GH[keep], CI[keep]
    GH -= 1
    if len(EP):
        EP += EV; EA += 1; on = EA < 22
        EP, EV, EC, EA = EP[on], EV[on], EC[on], EA[on]
    if nh: events.append((fr, "click", random.choice([1, 3, 4, 6])))
    if nb: events.append((fr, "pop", min(8, int((HP == 0).sum() * 9 / NSEG))))

BC = [(60, 220, 255), (255, 60, 220), (255, 160, 60), (160, 100, 255), (120, 255, 160)]
def bcol(c): return BC[c % 5]

def draw(fr, endfr, win):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    rr = R - RW / 2
    for s in range(NSEG):
        a1 = 360 * s / NSEG + 0.8; a2 = 360 * (s + 1) / NSEG - 0.8
        if HP[s] > 0:
            c = HPCOL[min(5, max(1, math.ceil(HP[s] * 5 / HPM[s])))]
            if FL[s] > .05: c = lerp(c, (255, 255, 255), FL[s])
            d.arc((CX - rr - RW / 2, CY - rr - RW / 2, CX + rr + RW / 2, CY + rr + RW / 2), a1, a2, fill=tuple(int(k * .35) for k in c), width=RW)
            d.arc((CX - R, CY - R, CX + R, CY + R), a1, a2, fill=c, width=5)
            d.arc((CX - R + RW, CY - R + RW, CX + R - RW, CY + R - RW), a1, a2, fill=c, width=3)
        elif fr - BROKE[s] < 12:
            k = 1 - (fr - BROKE[s]) / 12; c = (int(255 * k), int(200 * k), int(255 * k))
            d.arc((CX - R - 6, CY - R - 6, CX + R + 6, CY + R + 6), a1, a2, fill=c, width=RW + 10)
    for (x, y), c, ag in zip(EP, EC, EA):
        k2 = (1 - ag / 22) * .8
        d.ellipse((x - BR, y - BR, x + BR, y + BR), fill=tuple(int(k * k2) for k in bcol(c)))
    for (x, y), c in zip(P, CI):
        col = bcol(c); d.ellipse((x - BR, y - BR, x + BR, y + BR), fill=col)
        d.ellipse((x - 4, y - 5, x, y - 1), fill=tuple(min(255, k + 110) for k in col))
    left = np.where(HP > 0)[0]
    if 0 < len(left) <= 3:
        f6 = font(40)
        for s_ in left:
            am = (s_ + .5) * 2 * math.pi / NSEG; lx = CX + (R + 70) * math.cos(am); ly = CY + (R + 70) * math.sin(am)
            if (fr // 8) % 2: d.ellipse((CX + R * math.cos(am) - 30, CY + R * math.sin(am) - 30, CX + R * math.cos(am) + 30, CY + R * math.sin(am) + 30), outline=(255, 255, 255), width=4)
            tx = "LAST ONE" if len(left) == 1 else f"{len(left)} LEFT"
            lx = min(max(lx, 120), W - 120); d.text((lx - d.textlength(tx, font=f6) / 2, ly - 22), tx, font=f6, fill=(255, 230, 120))
    f = font(70); t1 = "How long until"; t2 = "the ring breaks?"
    d.text((540 - d.textlength(t1, font=f) / 2, 110), t1, font=f, fill=(255, 240, 252))
    d.text((540 - d.textlength(t2, font=f) / 2, 195), t2, font=f, fill=(255, 240, 252))
    f2 = font(36); s = "every hit splits the ball"
    d.text((540 - d.textlength(s, font=f2) / 2, 295), s, font=f2, fill=(220, 200, 230))
    nb = int((HP == 0).sum())
    f3 = font(54); tx = f"BROKEN  {nb} / {NSEG}"; d.text((540 - d.textlength(tx, font=f3) / 2, CY + R + 60), tx, font=f3, fill=(255, 190, 245))
    bw = 700; by = CY + R + 140
    d.rectangle((540 - bw / 2, by, 540 + bw / 2, by + 16), outline=(140, 70, 130), width=2)
    d.rectangle((540 - bw / 2, by, 540 - bw / 2 + bw * nb / NSEG, by + 16), fill=(255, 60, 200))
    f4 = font(34); tx = f"{len(P)} balls inside    {escaped} escaped"
    d.text((540 - d.textlength(tx, font=f4) / 2, by + 40), tx, font=f4, fill=(210, 190, 225))
    if endfr is not None and fr >= endfr:
        k = fr - endfr; f5 = font(104); tx = "RING BROKEN!" if win else ("SO CLOSE!" if (HP == 0).sum() >= NSEG - 2 else "RING WINS!")
        if k % 14 < 10 or k > 40: d.text((540 - d.textlength(tx, font=f5) / 2, CY - 60), tx, font=f5, fill=(255, 245, 255))
    return compose(sky.frame(fr), img, .75, .6, .35)

def run():
    wr = Writer() if CMD == "render" else None; fr = 0; endfr = None; win = None; log = {}
    while True:
        if endfr is None: step(fr)
        else:
            if len(EP) or len(P):
                P[:] += V; EP[:] += EV
        FL[:] *= 0.85
        if endfr is None and ((HP == 0).all() or len(P) == 0):
            endfr = fr; win = bool((HP == 0).all()); events.append((fr, "fin", 0))
            if win:  # free all balls
                EP2 = P.copy()
        if fr % 90 == 0: log[fr // 30] = (len(P), int((HP == 0).sum()), escaped)
        if wr: wr.write(draw(fr, endfr, win))
        elif CMD == "preview" and fr in PV: Image.fromarray(draw(fr, endfr, win)).save(f"p_{fr}.png")
        fr += 1
        if (endfr is not None and fr > endfr + 120) or fr >= DUR_MAX: break
    if wr:
        wr.close(); make_audio(fr, events); mux("video_tmp.mp4", "audio.wav", "ring_bruch.mp4")
    print(SEED, NSEG, HP0, "end", endfr and round(endfr / 30, 1), win, log)

run()
