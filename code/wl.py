import sys, math, random
import numpy as np
from PIL import Image, ImageDraw
from common import *

CMD = sys.argv[1]; PV = {int(x) for x in sys.argv[2:]}
random.seed(8); np.random.seed(8)
N = 32; A = 16.5; B = A * 0.577
GX, GY = 540.0, 1180.0          # screen center of floor
Y0 = GY - (N - 1) * B
BASE = 55.0; AMP = 70.0
C2 = 0.28; DAMP = 0.992
DUR = 31 * FPS; MEGA = 24 * FPS
sky = Sky(77)
u = np.zeros((N, N)); uo = np.zeros((N, N))
ii, jj = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")
order = np.argsort((ii + jj).ravel(), kind="stable")
events = []

# drop schedule
drops = []  # (land_frame, i, j, amp, mega)
t = 15; gap = 75
while t < MEGA - 40:
    drops.append((t, random.randint(6, N - 7), random.randint(6, N - 7), 1.3, False)); t += gap; gap = max(22, int(gap * 0.9))
drops.append((MEGA, N // 2, N // 2, 3.2, True))
FALL = 26

def wave_step():
    global u, uo
    p = np.pad(u, 1, mode="edge")
    lap = p[2:, 1:-1] + p[:-2, 1:-1] + p[1:-1, 2:] + p[1:-1, :-2] - 4 * u
    un = (2 * u - uo + C2 * lap) * DAMP
    uo = u; u = un

def splash(i, j, amp, sig):
    global u
    g = np.exp(-((ii - i) ** 2 + (jj - j) ** 2) / (2 * sig ** 2))
    u -= amp * g

def colr(v):
    t = max(0.0, min(1.0, (v + 1.0) / 2.0))
    st = [(40, 120, 255), (60, 220, 255), (170, 80, 255), (255, 40, 220), (255, 150, 60), (255, 230, 120)]
    x = t * (len(st) - 1); k = min(int(x), len(st) - 2)
    return lerp(st[k], st[k + 1], x - k)

def scr(i, j): return GX + (i - j) * A, Y0 + (i + j) * B

def draw(fr, ndrops, falling, flash):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    # floor
    corners = [scr(-0.5, -0.5), scr(N - .5, -0.5), scr(N - .5, N - .5), scr(-0.5, N - .5)]
    corners = [(x, y + B) for x, y in corners]
    d.polygon(corners, fill=(18, 6, 26), outline=(170, 70, 200))
    hs = np.clip(BASE + AMP * u, 4, 320)
    for k in order:
        i, j = divmod(int(k), N); x, y = scr(i, j); y += B; h = hs[i, j]
        c = colr(u[i, j])
        if flash > 0: c = lerp(c, (255, 255, 255), flash * .5)
        top = [(x, y - h - B), (x + A, y - h), (x, y - h + B), (x - A, y - h)]
        left = [(x - A, y - h), (x, y - h + B), (x, y + B), (x - A, y)]
        right = [(x + A, y - h), (x, y - h + B), (x, y + B), (x + A, y)]
        d.polygon(left, fill=tuple(int(v * .42) for v in c))
        d.polygon(right, fill=tuple(int(v * .26) for v in c))
        d.polygon(top, fill=tuple(int(v * .8) for v in c), outline=tuple(int(v * .35) for v in c))
    for (bx, by, br) in falling:
        d.ellipse((bx - br - 6, by - br - 6, bx + br + 6, by + br + 6), fill=(120, 60, 110))
        d.ellipse((bx - br, by - br, bx + br, by + br), fill=(255, 235, 250))
    f = font(66); t1 = "What does 1 drop"; t2 = "do to 1024 cubes?"
    d.text((540 - d.textlength(t1, font=f) / 2, 110), t1, font=f, fill=(255, 240, 252))
    d.text((540 - d.textlength(t2, font=f) / 2, 190), t2, font=f, fill=(255, 240, 252))
    f3 = font(96); tx = str(ndrops); d.text((540 - d.textlength(tx, font=f3) / 2, 1500), tx, font=f3, fill=(255, 200, 245))
    f4 = font(34); tx = "DROPS"; d.text((540 - d.textlength(tx, font=f4) / 2, 1610), tx, font=f4, fill=(220, 180, 230))
    if fr >= MEGA - FALL - 20:
        f5 = font(92); tx = "MEGA DROP"
        if fr < MEGA or (fr - MEGA) % 14 < 10: d.text((540 - d.textlength(tx, font=f5) / 2, 330), tx, font=f5, fill=(255, 220, 120))
    return compose(sky.frame(fr), img, .45, .38, .22)

def run():
    wr = Writer() if CMD == "render" else None; nd = 0; flash = 0.0
    for fr in range(DUR):
        falling = []
        for (lf, i, j, amp, mega) in drops:
            if lf - FALL <= fr < lf:
                k = (fr - (lf - FALL)) / FALL
                x, y = scr(i, j); y += B - (BASE + AMP * u[i, j]) - B
                br = 30 if mega else 13
                falling.append((x, y - 1100 * (1 - k) ** 2, br))
            if fr == lf:
                splash(i, j, amp, 3.0 if mega else 1.8); nd += 1
                if mega: events.append((fr, "fin", 0)); flash = 1.0
                else: events.append((fr, "pop", min(8, nd // 3))); events.append((fr, "click", random.choice([2, 4, 5, 7])))
        wave_step(); wave_step()
        flash *= 0.9
        if wr: wr.write(draw(fr, nd, falling, flash))
        elif CMD == "preview" and fr in PV: Image.fromarray(draw(fr, nd, falling, flash)).save(f"p_{fr}.png")
    if wr:
        wr.close(); make_audio(DUR, events); mux("video_tmp.mp4", "audio.wav", "neon_welle_3d.mp4")
    print("drops", len(drops), "maxu", float(np.abs(u).max()))

run()
