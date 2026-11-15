import sys, math, random
import numpy as np
from PIL import Image, ImageDraw
from common import *

CMD = sys.argv[1]; SEED = int(sys.argv[2]); INC = float(sys.argv[3]); RPMMAX = float(sys.argv[4])
PV = {int(x) for x in sys.argv[5:]}
random.seed(SEED); np.random.seed(SEED)
CX, CY, R = 540.0, 1040.0, 470.0
BR = 12.0; SPEED = 9.0; SUB = 8; MAXB = 900; GHOST = 8; DUR_MAX = 46 * FPS
HW = 16.0; RPM0 = 6.0; ARM = R - 45
sky = Sky(52)
BC = [(60, 220, 255), (255, 60, 220), (255, 160, 60), (160, 100, 255)]
a0 = random.uniform(0, 6.28)
NB = int(sys.argv[5]); PV = {int(x) for x in sys.argv[6:]}
rr = np.sqrt(np.random.uniform(0.08, 0.85, NB)) * R; aa = np.random.uniform(0, 6.28, NB)
P = np.stack([CX + rr * np.cos(aa), CY + rr * np.sin(aa)], 1); bb = np.random.uniform(0, 6.28, NB)
V = 7.0 * np.stack([np.cos(bb), np.sin(bb)], 1)
GH = np.zeros(NB); CI = np.arange(NB) % 4; HITS = [0]
rpm = RPM0; th = -math.pi / 2; events = []; hitfl = 0.0

def rot(v, a):
    c, s = math.cos(a), math.sin(a)
    return np.stack([v[:, 0] * c - v[:, 1] * s, v[:, 0] * s + v[:, 1] * c], 1)

def arm_hit(al, w):
    """arm = segment from center out to R in direction al (both directions: two arms)"""
    global P, V
    u = np.array([math.cos(al), math.sin(al)]); v = np.array([-u[1], u[0]])
    rel = P - [CX, CY]; s = rel @ u; l = rel @ v
    near = (np.abs(s) > 26) & (np.abs(s) < ARM) & (np.abs(l) < HW + BR)
    if not near.any(): return np.zeros(len(P), bool)
    sg = np.sign(l[near]); sg[sg == 0] = 1
    n = sg[:, None] * v
    P[near] += n * (HW + BR - np.abs(l[near]))[:, None]
    vo = w * np.stack([-rel[near, 1], rel[near, 0]], 1)
    vn = ((V[near] - vo) * n).sum(1); Vn = V[near]; bad = vn < 0
    Vn[bad] -= 2 * vn[bad, None] * n[bad]; V[near] = Vn
    hit = np.zeros(len(P), bool); idx = np.where(near)[0]; hit[idx[bad]] = True
    return hit

def step(fr):
    global P, V, GH, CI, rpm, th, hitfl
    ns = 0
    for _ in range(SUB):
        w = rpm * 2 * math.pi / 60 / FPS / SUB; th += w
        P += V / SUB
        rel = P - [CX, CY]; d = np.hypot(rel[:, 0], rel[:, 1]); out = d > R - BR
        if out.any():
            n = rel[out] / d[out, None]; vn = (V[out] * n).sum(1); Vo = V[out]; g = vn > 0
            Vo[g] -= 2 * vn[g, None] * n[g]; Vo[g] = rot(Vo[g], 0) if False else Vo[g]
            # scatter inward
            Vo[g] = Vo[g] - 0.6 * np.linalg.norm(Vo[g], axis=1)[:, None] * n[g]
            V[out] = Vo; P[out] = np.array([CX, CY]) + n * (R - BR)
        # hub
        rel = P - [CX, CY]; d = np.hypot(rel[:, 0], rel[:, 1]) + 1e-9; hb = d < 30 + BR
        if hb.any():
            n = rel[hb] / d[hb, None]; P[hb] = np.array([CX, CY]) + n * (30 + BR)
            vn = (V[hb] * n).sum(1); Vh = V[hb]; g = vn < 0; Vh[g] -= 2 * vn[g, None] * n[g]; V[hb] = Vh
        hit = arm_hit(th, w * SUB) | arm_hit(th + math.pi, w * SUB)
        cand = np.where(hit & (GH <= 0))[0]
        if len(cand):
            rpm = min(RPMMAX, rpm + INC * len(cand)); hitfl = 1.0
            HITS[0] += len(cand); GH[cand] = GHOST; CI[cand] += 1; cand = cand[:0]
            if len(cand):
                a = 0.4; nv = rot(V[cand], -a); V[cand] = rot(V[cand], a); CI[cand] += 1; GH[cand] = GHOST
                P = np.vstack([P, P[cand] + np.random.normal(0, 1, (len(cand), 2))]); V = np.vstack([V, nv])
                GH = np.concatenate([GH, np.full(len(cand), GHOST)]); CI = np.concatenate([CI, CI[cand]]); ns += len(cand)
            GH[np.where(hit)[0]] = np.maximum(GH[np.where(hit)[0]], GHOST)
    GH -= 1
    sp = np.hypot(V[:, 0], V[:, 1]) + 1e-9; V *= ((7 + rpm * 0.09) / sp)[:, None]
    ns = HITS[0] - HITS[1] if len(HITS) > 1 else HITS[0]
    if len(HITS) > 1: HITS[1] = HITS[0]
    else: HITS.append(HITS[0])
    if ns: events.append((fr, "click", min(8, int(rpm / RPMMAX * 9))))
    if ns >= 4: events.append((fr, "pop", min(8, int(rpm / RPMMAX * 9))))

def draw(fr, endfr):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    d.ellipse((CX - R - 4, CY - R - 4, CX + R + 4, CY + R + 4), outline=(255, 235, 250), width=5)
    k = min(1, (rpm - RPM0) / (RPMMAX - RPM0))
    acol = (lerp((60, 220, 255), (255, 160, 50), k * 2) if k < .5 else lerp((255, 160, 50), (255, 40, 60), k * 2 - 1)) if k < 1 else (255, 255, 255)
    # motion blur ghosts of arm
    w = rpm * 2 * math.pi / 60 / FPS
    for g in range(4, -1, -1):
        al = th - g * w * 0.3; fade = 1 - g / 5
        for aa in (al, al + math.pi):
            u = np.array([math.cos(aa), math.sin(aa)]); v = np.array([-u[1], u[0]])
            cs = [tuple(np.array([CX, CY]) + a * u + b * v) for a, b in ((26, -HW), (ARM, -HW), (ARM, HW), (26, HW))]
            if g == 0:
                d.polygon(cs, fill=tuple(int(c * .25) for c in acol)); d.line(cs + [cs[0]], fill=acol, width=5)
            else:
                d.polygon(cs, fill=tuple(int(c * .12 * fade) for c in acol))
    d.ellipse((CX - 30, CY - 30, CX + 30, CY + 30), fill=(40, 30, 50), outline=(255, 240, 255), width=5)
    d.ellipse((CX - 9, CY - 9, CX + 9, CY + 9), fill=(255, 255, 255))
    for (x, y), c in zip(P, CI):
        col = BC[c % 4]; d.ellipse((x - BR, y - BR, x + BR, y + BR), fill=col)
        d.ellipse((x - 5, y - 7, x, y - 2), fill=tuple(min(255, q + 110) for q in col))
    f = font(64); t1 = "Every hit makes"; t2 = "the arm faster"
    d.text((540 - d.textlength(t1, font=f) / 2, 100), t1, font=f, fill=(255, 240, 252))
    d.text((540 - d.textlength(t2, font=f) / 2, 178), t2, font=f, fill=(255, 240, 252))
    f2 = font(120); tx = f"{rpm:.0f} RPM"; sc = 1 + 0.06 * hitfl
    d.text((540 - d.textlength(tx, font=f2) / 2, 290), tx, font=f2, fill=acol)
    f3 = font(96); tx = str(HITS[0]); d.text((540 - d.textlength(tx, font=f3) / 2, CY + R + 45), tx, font=f3, fill=(255, 200, 245))
    f4 = font(34); tx = "HITS"; d.text((540 - d.textlength(tx, font=f4) / 2, CY + R + 155), tx, font=f4, fill=(220, 180, 230))
    if endfr is not None and fr >= endfr:
        q = fr - endfr; f5 = font(100); tx = "MAX SPEED!"
        if q % 14 < 10 or q > 40: d.text((540 - d.textlength(tx, font=f5) / 2, 440), tx, font=f5, fill=(255, 250, 200))
    return compose(sky.frame(fr), img, .75, .6, .35)

def run():
    global hitfl
    wr = Writer() if CMD == "render" else None; fr = 0; endfr = None; log = {}
    while True:
        step(fr); hitfl *= .8
        if endfr is None and rpm >= RPMMAX: endfr = fr; events.append((fr, "fin", 0))
        if fr % 90 == 0: log[fr // 30] = (round(rpm), HITS[0])
        if wr: wr.write(draw(fr, endfr))
        elif CMD == "preview" and fr in PV: Image.fromarray(draw(fr, endfr)).save(f"p_{fr}.png")
        fr += 1
        if (endfr is not None and fr > endfr + 135) or fr >= DUR_MAX: break
    if wr:
        wr.close(); make_audio(fr, events); mux("video_tmp.mp4", "audio.wav", "turbo_arm.mp4")
    print(SEED, INC, RPMMAX, "end", endfr and round(endfr / 30, 1), log)

run()
