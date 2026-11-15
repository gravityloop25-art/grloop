import sys, math, random
import numpy as np
from PIL import Image, ImageDraw
from common import *

CMD = sys.argv[1]; K = float(sys.argv[2]); DROP = float(sys.argv[3])
PV = {int(x) for x in sys.argv[4:]}
random.seed(3); np.random.seed(3)
NL = 120; X1, X2 = 290.0, 790.0
YTOP = 820.0; SP = 8.0
LY = YTOP + np.arange(NL) * SP
T0 = 1200.0; BRAD = 44.0; G = 0.55; DUR_MAX = 50 * FPS
sky = Sky(61)
alive = np.ones(NL, bool); brokefr = np.full(NL, -999)
bx, by, vx, vy = 540.0, 470.0, 2.6, 0.0
temp = T0; hp = 1.0; events = []
parts = []  # x,y,vx,vy,life,kind(0 shard,1 steam)

def tcol(t):
    k = max(0.0, min(1.0, t / T0))
    if k > .7: return lerp((255, 150, 40), (255, 250, 220), (k - .7) / .3)
    if k > .35: return lerp((230, 50, 20), (255, 150, 40), (k - .35) / .35)
    return lerp((70, 20, 20), (230, 50, 20), k / .35)

def step(fr):
    global bx, by, vx, vy, temp, hp
    vy += G; by += vy; bx += vx
    if bx < X1 + BRAD + 4: bx = X1 + BRAD + 4; vx = abs(vx)
    if bx > X2 - BRAD - 4: bx = X2 - BRAD - 4; vx = -abs(vx)
    idx = np.where(alive)[0]
    contact = False
    if len(idx):
        top = idx[0]; yb = LY[top]
        if by + BRAD >= yb:
            by = yb - BRAD; contact = True
            if vy > 4.0: vy = -vy * 0.3
            else: vy = 0
            hp -= K * (temp / T0) ** 0.8
            temp = max(0.0, temp - 0.05)
            if fr % 2 == 0: parts.append([bx + random.uniform(-30, 30), by + BRAD - 6, random.uniform(-.6, .6), random.uniform(-2.5, -1.2), 40, 1])
            if hp <= 0:
                alive[top] = False; brokefr[top] = fr; hp = 1.0; temp = max(0.0, temp - DROP)
                for _ in range(10):
                    parts.append([random.uniform(X1 + 10, X2 - 10), yb, random.uniform(-3, 3), random.uniform(-6, -1), 30, 0])
                n = NL - alive.sum()
                events.append((fr, "click", int(8 * temp / T0)))
                if n % 10 == 0: events.append((fr, "pop", min(8, n // 15)))
    for p in parts:
        p[0] += p[2]; p[1] += p[3]; p[4] -= 1
        if p[5] == 0: p[3] += 0.4
    parts[:] = [p for p in parts if p[4] > 0]
    return contact

def draw(fr, endfr, win):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    wc = (255, 235, 250)
    d.line((X1, 560, X1, LY[-1] + 30), fill=wc, width=5); d.line((X2, 560, X2, LY[-1] + 30), fill=wc, width=5)
    for i in range(NL):
        y = LY[i]
        if alive[i]:
            sh = 0.75 + 0.25 * math.sin(i * 0.7)
            c = (int(70 * sh), int(200 * sh), int(255 * sh))
            if i == np.argmax(alive) and hp < 1:
                c = lerp(c, tcol(temp), (1 - hp) * .8)
            d.rectangle((X1 + 4, y, X2 - 4, y + 3), fill=c)
        elif fr - brokefr[i] < 8:
            q = 1 - (fr - brokefr[i]) / 8; d.rectangle((X1 + 4, y - 2, X2 - 4, y + 5), fill=(int(255 * q), int(255 * q), int(255 * q)))
    for p in parts:
        q = p[4] / 40
        if p[5] == 0: d.rectangle((p[0] - 3, p[1] - 2, p[0] + 3, p[1] + 2), fill=(int(150 * q + 60), int(230 * q), 255))
        else:
            r = 6 + (40 - p[4]) * .5; g = int(70 * q); d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=(g, g, g))
    c = tcol(temp)
    for r, k in ((BRAD + 16, .25), (BRAD + 7, .5), (BRAD, 1.0)):
        d.ellipse((bx - r, by - r, bx + r, by + r), fill=tuple(int(v * k) for v in c))
    d.ellipse((bx - BRAD * .55, by - BRAD * .6, bx - BRAD * .05, by - BRAD * .15), fill=tuple(min(255, v + 60) for v in c))
    f = font(70); t1 = "Can it melt all"; t2 = "120 ice layers?"
    d.text((540 - d.textlength(t1, font=f) / 2, 100), t1, font=f, fill=(255, 240, 252))
    d.text((540 - d.textlength(t2, font=f) / 2, 185), t2, font=f, fill=(255, 240, 252))
    n = NL - int(alive.sum())
    f2 = font(46); tx = f"MELTED  {n} / {NL}"; d.text((540 - d.textlength(tx, font=f2) / 2, 300), tx, font=f2, fill=(140, 225, 255))
    f3 = font(84); tx = f"{temp:.0f}°C"; d.text((540 - d.textlength(tx, font=f3) / 2, 370), tx, font=f3, fill=c if temp > 150 else (230, 80, 60))
    if endfr is not None and fr >= endfr:
        q = fr - endfr; f5 = font(100); tx = "IT MADE IT!" if win else "FROZEN!"
        if q % 14 < 10 or q > 40: d.text((540 - d.textlength(tx, font=f5) / 2, 1100), tx, font=f5, fill=(255, 250, 220) if win else (140, 225, 255))
    return compose(sky.frame(fr), img, .8, .65, .4)

def run():
    global vy
    wr = Writer() if CMD == "render" else None; fr = 0; endfr = None; win = None; log = {}; stuck = 0
    while True:
        step(fr)
        if endfr is None:
            if not alive.any() and by > LY[-1] + 60: endfr = fr; win = True; events.append((fr, "fin", 0))
            if temp <= 1: endfr = fr; win = False; events.append((fr, "fin", 0))
        if fr % 90 == 0: log[fr // 30] = (NL - int(alive.sum()), round(temp))
        if wr: wr.write(draw(fr, endfr, win))
        elif CMD == "preview" and fr in PV: Image.fromarray(draw(fr, endfr, win)).save(f"p_{fr}.png")
        fr += 1
        if (endfr is not None and fr > endfr + 120) or fr >= DUR_MAX: break
    if wr:
        wr.close(); make_audio(fr, events); mux("video_tmp.mp4", "audio.wav", "gluehende_kugel.mp4")
    print(K, DROP, "end", endfr and round(endfr / 30, 1), win, log)

run()
