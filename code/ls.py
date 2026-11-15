import sys, math, random
import numpy as np
from PIL import Image, ImageDraw
from common import *

CMD = sys.argv[1]; SEED = int(sys.argv[2]); N0 = int(sys.argv[3]); SP = float(sys.argv[4]); HUNT = float(sys.argv[5])
PV = {int(x) for x in sys.argv[6:]}
rng = np.random.default_rng(SEED); random.seed(SEED)
CX, CY, R = 540.0, 1010.0, 470.0
K = 4.5; DUR_MAX = 48 * FPS
sky = Sky(88)
pts = []
while len(pts) < N0:
    a = rng.uniform(0, 2 * np.pi); r = math.sqrt(rng.uniform(0, 1)) * (R - 30)
    x, y = CX + r * math.cos(a), CY + r * math.sin(a)
    if pts and np.min(np.hypot(np.array(pts)[:, 0] - x, np.array(pts)[:, 1] - y)) < 2 * K + 1: continue
    pts.append((x, y))
P = np.array(pts); b = rng.uniform(0, 2 * np.pi, N0); V = SP * np.stack([np.cos(b), np.sin(b)], 1)
M = np.ones(N0); FL = np.zeros(N0); events = []; MTOT = float(N0)
STOPS = [(60, 220, 255), (150, 90, 255), (255, 40, 220), (255, 150, 60), (255, 245, 200)]

def rad(m): return K * np.sqrt(m)

def mcol(m):
    t = math.log(m) / math.log(MTOT) if m > 1 else 0.0
    x = t * (len(STOPS) - 1); k = min(int(x), len(STOPS) - 2)
    return lerp(STOPS[k], STOPS[k + 1], x - k)

def step(fr):
    global P, V, M, FL
    P += V
    rel = P - [CX, CY]; d = np.hypot(rel[:, 0], rel[:, 1]) + 1e-9; r = rad(M); out = d > R - r - 3
    if out.any():
        nn = rel[out] / d[out, None]; vn = (V[out] * nn).sum(1); Vo = V[out]; g = vn > 0
        Vo[g] -= 2 * vn[g, None] * nn[g]; V[out] = Vo
        P[out] = np.array([CX, CY]) + nn * (R - r[out] - 3)[:, None]
    n = len(P)
    if n < 2: return 0
    D = P[None, :, :] - P[:, None, :]; dist = np.hypot(D[..., 0], D[..., 1]) + 1e-9
    cont = np.triu(dist < (r[:, None] + r[None, :]), 1)
    ii, jj = np.where(cont)
    dead = np.zeros(n, bool); eaten = 0; big = 0
    for i, j in zip(ii, jj):
        if dead[i] or dead[j]: continue
        if M[i] > M[j] or (M[i] == M[j] and i < j): a, bb = i, j
        else: a, bb = j, i
        M[a] += M[bb]; dead[bb] = True; FL[a] = 1.0; eaten += 1; big = max(big, M[a])
    if HUNT > 0:
        sm = (M[None, :] < M[:, None]) & ~dead[None, :]
        dd = np.where(sm, dist, 1e9); jn = dd.argmin(1); ar = np.arange(n); has = dd[ar, jn] < 1e8
        dirv = D[ar, jn] / dist[ar, jn][:, None]
        V[has] += HUNT * min(1.0, 40.0 / max(n, 6)) * 10 * SP * dirv[has]
        sp = np.hypot(V[:, 0], V[:, 1]) + 1e-9; V *= (SP / sp)[:, None]
    keep = ~dead
    P, V, M, FL = P[keep], V[keep], M[keep], FL[keep]
    if eaten:
        events.append((fr, "click", random.choice([0, 2, 4, 5, 7])))
        if big >= 25: events.append((fr, "pop", min(8, int(math.log2(big)) - 3)))
    return eaten

def draw(fr, endfr):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    rc = (255, 235, 250)
    if endfr is not None and 0 <= fr - endfr < 90 and (fr - endfr) % 16 < 8: rc = (255, 255, 255)
    d.ellipse((CX - R - 4, CY - R - 4, CX + R + 4, CY + R + 4), outline=rc, width=5)
    order = np.argsort(M)
    for i in order:
        x, y = P[i]; m = M[i]; r = rad(m); c = mcol(m)
        if FL[i] > 0.05: d.ellipse((x - r - 7 * FL[i], y - r - 7 * FL[i], x + r + 7 * FL[i], y + r + 7 * FL[i]), fill=(255, 255, 255))
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)
        d.ellipse((x - r * .55, y - r * .65, x - r * .1, y - r * .2), fill=tuple(min(255, v + 110) for v in c))
    f = font(76); t1 = "Who is the last"; t2 = "ball standing?"
    d.text((540 - d.textlength(t1, font=f) / 2, 105), t1, font=f, fill=(255, 240, 252))
    d.text((540 - d.textlength(t2, font=f) / 2, 195), t2, font=f, fill=(255, 240, 252))
    f2 = font(36); s = "the bigger ball eats the smaller"
    d.text((540 - d.textlength(s, font=f2) / 2, 300), s, font=f2, fill=(220, 200, 230))
    mx = int(M.max())
    f3 = font(130); tx = f"x{mx}"; d.text((540 - d.textlength(tx, font=f3) / 2, CY + R + 35), tx, font=f3, fill=mcol(M.max()))
    f4 = font(34); tx = "BIGGEST BALL"; d.text((540 - d.textlength(tx, font=f4) / 2, CY + R + 180), tx, font=f4, fill=(220, 180, 230))
    f5 = font(46); tx = f"{len(P)} ALIVE"; d.text((540 - d.textlength(tx, font=f5) / 2, CY + R + 235), tx, font=f5, fill=(255, 200, 245))
    if endfr is not None and fr >= endfr:
        q = fr - endfr; f6 = font(96); tx = "LAST BALL!"
        if q % 14 < 10 or q > 40: d.text((540 - d.textlength(tx, font=f6) / 2, 385), tx, font=f6, fill=(255, 250, 210))
    return compose(sky.frame(fr), img, .7, .55, .3)

def run():
    wr = Writer() if CMD == "render" else None; fr = 0; endfr = None; log = {}
    while True:
        FL[:] *= 0.85
        if endfr is None: step(fr)
        if endfr is None and len(P) == 1: endfr = fr; events.append((fr, "fin", 0))
        if fr % 90 == 0: log[fr // 30] = (len(P), int(M.max()))
        if wr: wr.write(draw(fr, endfr))
        elif CMD == "preview" and fr in PV: Image.fromarray(draw(fr, endfr)).save(f"p_{fr}.png")
        fr += 1
        if (endfr is not None and fr > endfr + 105) or fr >= DUR_MAX: break
    if wr:
        wr.close(); make_audio(fr, events); mux("video_tmp.mp4", "audio.wav", "last_ball.mp4")
    print(SEED, N0, SP, HUNT, "end", endfr and round(endfr / 30, 1), log)

run()
