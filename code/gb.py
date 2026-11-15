import sys, math, random
import numpy as np
from PIL import Image, ImageDraw
from common import *

CMD = sys.argv[1]; SEED = int(sys.argv[2]); GR = float(sys.argv[3]); SP = float(sys.argv[4])
PV = {int(x) for x in sys.argv[5:]}
rng = np.random.default_rng(SEED); random.seed(SEED)
CX, CY, R = 540.0, 1040.0, 450.0
R0 = 8.0; SUB = 4; RFULL = R * 0.9
sky = Sky(141)
a0 = rng.uniform(0, 2 * np.pi)
pos = np.array([CX + 120.0, CY - 80.0]); vel = SP * np.array([math.cos(a0), math.sin(a0)])
r = R0; rt = R0; bounces = 0; events = []; ripples = []; trail = []
STOPS = [(60, 220, 255), (150, 90, 255), (255, 40, 220), (255, 150, 60), (255, 245, 200)]

def scol(s):
    t = math.log(max(s, 1.0)) / math.log(RFULL / R0)
    t = min(1.0, t); x = t * (len(STOPS) - 1); k = min(int(x), len(STOPS) - 2)
    return lerp(STOPS[k], STOPS[k + 1], x - k)

def step(fr):
    global pos, vel, r, rt, bounces
    r += (rt - r) * 0.22
    for _ in range(SUB):
        pos = pos + vel / SUB
        rel = pos - [CX, CY]; d = math.hypot(rel[0], rel[1]) + 1e-9
        if d > R - r - 3:
            n = rel / d; vn = vel @ n
            if vn > 0:
                vel = vel - 2 * vn * n; pos = np.array([CX, CY]) + n * (R - r - 4)
                bounces += 1; rt = min(RFULL, rt * GR)
                ripples.append((pos[0] + n[0] * r, pos[1] + n[1] * r, fr, scol(r / R0)))
                events.append((fr, "bloop", bounces))
                if bounces % 5 == 0: events.append((fr, "chime", bounces))
    trail.append((pos[0], pos[1], r)); del trail[:-5]

def draw(fr, endfr):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    rc = (255, 235, 250)
    if endfr is not None and 0 <= fr - endfr < 90 and (fr - endfr) % 16 < 8: rc = (255, 255, 255)
    d.ellipse((CX - R - 4, CY - R - 4, CX + R + 4, CY + R + 4), outline=rc, width=5)
    for (x, y, f0, c) in ripples:
        q = (fr - f0) / 22
        if 0 <= q < 1:
            rr = 14 + q * 90; k = 1 - q
            d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=tuple(int(v * k) for v in c), width=4)
    for i, (x, y, rr) in enumerate(trail[:-1]):
        k = (i + 1) / (len(trail) + 1) * .35; c = scol(rr / R0)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=tuple(int(v * k) for v in c))
    c = scol(r / R0)
    d.ellipse((pos[0] - r, pos[1] - r, pos[0] + r, pos[1] + r), fill=c)
    d.ellipse((pos[0] - r * .55, pos[1] - r * .65, pos[0] - r * .1, pos[1] - r * .2), fill=tuple(min(255, v + 110) for v in c))
    f = font(70); t1 = "Every bounce makes"; t2 = "the ball bigger"
    d.text((540 - d.textlength(t1, font=f) / 2, 95), t1, font=f, fill=(255, 240, 252))
    d.text((540 - d.textlength(t2, font=f) / 2, 178), t2, font=f, fill=(255, 240, 252))
    f3 = font(130); tx = f"x{r / R0:.1f}" if r / R0 < 10 else f"x{r / R0:.0f}"
    d.text((540 - d.textlength(tx, font=f3) / 2, CY + R + 35), tx, font=f3, fill=c)
    f4 = font(34); tx = "SIZE"; d.text((540 - d.textlength(tx, font=f4) / 2, CY + R + 180), tx, font=f4, fill=(220, 180, 230))
    f5 = font(46); tx = f"{bounces} BOUNCES"; d.text((540 - d.textlength(tx, font=f5) / 2, CY + R + 235), tx, font=f5, fill=(255, 200, 245))
    f2 = font(110); tx = f"x{r / R0:.0f}"
    if endfr is not None and fr >= endfr:
        q = fr - endfr; f6 = font(100); tx = "FULL!"
        if q % 14 < 10 or q > 40: d.text((540 - d.textlength(tx, font=f6) / 2, 300), tx, font=f6, fill=(255, 250, 210))
    return compose(sky.frame(fr), img, .6, .5, .3)

# ---------- new sound: rising bubble "bloop" scale + glass shimmer ----------
PS = [0, 2, 4, 7, 9]
def bloop(f0, amp=0.5):
    dur = 0.30; t = np.arange(int(dur * SR)) / SR
    f = f0 * (1 + 1.7 * (1 - np.exp(-t * 38)))
    ph = 2 * np.pi * np.cumsum(f) / SR
    env = np.exp(-t * 11) * (1 - np.exp(-t * 600))
    s = (np.sin(ph) + 0.25 * np.sin(2 * ph)) * env
    s += 0.25 * np.sin(2 * np.pi * (f0 * 0.5) * t) * np.exp(-t * 18)
    return s * amp

def shimmer(f0, amp=0.25):
    dur = 0.9; t = np.arange(int(dur * SR)) / SR; s = np.zeros_like(t)
    for k, m in enumerate((1, 1.5, 2, 3, 4.02)):
        s += np.sin(2 * np.pi * f0 * m * t + k) * np.exp(-t * (4 + 2 * k)) / (1 + k * .4)
    return s * amp

def make_audio_gb(nframes, evs, path="audio.wav"):
    out = np.zeros(int(nframes / FPS * SR) + 2 * SR, dtype=np.float32)
    def add(sig, fr):
        s = max(0, int(fr / FPS * SR)); e = min(len(out), s + len(sig)); out[s:e] += sig[:e - s]
    for fr, k, v in evs:
        if k == "bloop":
            idx = v - 1; f0 = 220 * 2 ** ((PS[idx % 5] + 12 * (idx // 5)) / 12); f0 = min(f0, 1760)
            add(bloop(f0), fr)
        elif k == "chime":
            idx = v // 5 - 1; f0 = 523 * 2 ** (PS[idx % 5] / 12) * (2 if idx >= 5 else 1); add(shimmer(f0), fr)
        elif k == "fin":
            add(finale(0.7), fr)
    out = np.tanh(out * 1.2) * 0.85; out = out[:int(nframes / FPS * SR)]
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes())

def run():
    wr = Writer() if CMD == "render" else None; fr = 0; endfr = None; log = {}
    while True:
        if endfr is None: step(fr)
        if endfr is None and r >= RFULL - 2: endfr = fr; events.append((fr, "fin", 0))
        if fr % 90 == 0: log[fr // 30] = (bounces, round(r / R0, 1))
        if wr: wr.write(draw(fr, endfr))
        elif CMD == "preview" and fr in PV: Image.fromarray(draw(fr, endfr)).save(f"p_{fr}.png")
        fr += 1
        if (endfr is not None and fr > endfr + 105) or fr >= 46 * FPS: break
    if wr:
        wr.close(); make_audio_gb(fr, events); mux("video_tmp.mp4", "audio.wav", "wachsende_kugel.mp4")
    print(SEED, GR, SP, "end", endfr and round(endfr / 30, 1), log)

run()
