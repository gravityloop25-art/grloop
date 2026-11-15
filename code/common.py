import math, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
SR = 44100
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

class Sky:
    """dark night sky with many small twinkling stars"""
    def __init__(self, seed=1, n=230):
        r = np.random.default_rng(seed)
        self.x = r.uniform(0, W, n); self.y = r.uniform(0, H, n)
        self.b = r.uniform(0.25, 1.0, n); self.ph = r.uniform(0, 6.28, n)
        self.sp = r.uniform(0.04, 0.16, n); self.sz = r.choice([1, 1, 1, 2, 2, 3], n)
        tint = r.uniform(0, 1, n)
        self.col = np.stack([255 * np.ones(n), 215 + 40 * (1 - tint) - 70 * tint, 230 - 90 * tint], 1)
        self.big = set(np.argsort(-self.b)[:14].tolist())
        yy = np.linspace(0, 1, H)[:, None]
        base = np.zeros((H, W, 3), np.float32)
        base[..., 0] = 2 + 3 * yy; base[..., 1] = 1 + 2 * yy; base[..., 2] = 6 + 8 * yy
        self.base = base

    def frame(self, fr):
        img = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(img)
        tw = 0.55 + 0.45 * np.sin(self.ph + fr * self.sp * 2.2)
        tw = tw ** 2 * self.b
        for i in range(len(self.x)):
            k = tw[i]
            if k < 0.05: continue
            c = tuple(int(v * k) for v in self.col[i]); x, y, s = self.x[i], self.y[i], self.sz[i]
            d.ellipse((x - s * .7, y - s * .7, x + s * .7, y + s * .7), fill=c)
            if i in self.big and k > 0.35:
                L = 5 + 9 * k
                d.line((x - L, y, x + L, y), fill=tuple(int(v * k * .7) for v in self.col[i]), width=1)
                d.line((x, y - L, x, y + L), fill=tuple(int(v * k * .7) for v in self.col[i]), width=1)
        return np.asarray(img, np.float32) + self.base

def compose(sky, light, g1=0.85, g2=0.75, g3=0.45):
    """sky: float32 HxWx3, light: PIL RGB layer of crisp neon. adds soft glow."""
    small = light.resize((W // 4, H // 4), Image.BOX)
    a = small.filter(ImageFilter.GaussianBlur(2)).resize((W, H), Image.BILINEAR)
    b = small.filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR)
    c = small.filter(ImageFilter.GaussianBlur(16)).resize((W, H), Image.BILINEAR)
    out = sky + np.asarray(light, np.float32) + g1 * np.asarray(a, np.float32) + g2 * np.asarray(b, np.float32) + g3 * np.asarray(c, np.float32)
    # soft clip so bright cores go white-ish
    out = 255 * (1 - np.exp(-out / 150.0)) * 1.15
    return np.clip(out, 0, 255).astype(np.uint8)

def font(sz): return ImageFont.truetype(FONT, sz)

def lerp(c1, c2, t): return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
MAG = (255, 40, 220); ORA = (255, 150, 90); CYAN = (60, 220, 255); VIO = (150, 80, 255)

class Writer:
    def __init__(self, path="video_tmp.mp4"):
        self.ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                    "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
                                    "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    def write(self, arr): self.ff.stdin.write(arr.tobytes())
    def close(self): self.ff.stdin.close(); self.ff.wait()

# ---------------- audio ----------------
PENT = [0, 2, 4, 7, 9, 12, 14, 16, 19]
rng = np.random.default_rng(7)

def tone(midi, dur, amp, dec):
    f = 440 * 2 ** ((midi - 69) / 12); t = np.arange(int(dur * SR)) / SR
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)) * np.exp(-dec * t) * amp

def click(freq, amp, dur=0.03):
    t = np.arange(int(dur * SR)) / SR
    return (0.5 * rng.normal(0, 1, len(t)) * np.exp(-t * 400) + np.sin(2 * np.pi * freq * t) * np.exp(-t * 120)) * amp

def pop(amp, zone):
    dur = 0.7; t = np.arange(int(dur * SR)) / SR
    boom = np.sin(2 * np.pi * (150 * t - 70 * t * t)) * np.exp(-t * 9)
    noise = np.convolve(rng.normal(0, 1, len(t)), np.ones(10) / 10, mode="same") * np.exp(-t * 8) * 0.7
    chime = tone(72 + PENT[min(zone, 8)], dur, 0.55, 7)
    return (boom + noise + chime) * amp

def finale(amp=0.6):
    t = np.arange(int(1.4 * SR)) / SR
    sw = np.sin(2 * np.pi * (400 * t + 500 * t * t)) * np.exp(-t * 3) * 0.5
    nz = rng.normal(0, 1, len(t)) * np.exp(-t * 4) * 0.4
    return (sw + nz + tone(79, 1.4, 0.5, 3) + tone(86, 1.4, 0.3, 3)) * amp

def make_audio(nframes, events, path="audio.wav"):
    """events: list of (frame, kind, param). kinds: click(param=pitch idx), pop(param=zone), fin"""
    out = np.zeros(int(nframes / FPS * SR) + 2 * SR, dtype=np.float32)
    def add(sig, fr, jit=0.0):
        s = max(0, int((fr / FPS + jit) * SR)); e = min(len(out), s + len(sig)); out[s:e] += sig[:e - s]
    per = {}
    for fr, k, v in events: per.setdefault(fr, []).append((k, v))
    for fr, evs in per.items():
        pops = [e for e in evs if e[0] == "pop"][:2]
        cl = [e for e in evs if e[0] == "click"][:2]
        for _, z in pops: add(pop(0.45, z), fr, random.uniform(0, 0.012))
        for _, i in cl:
            j = random.uniform(0, 0.02); add(click(1000 + 150 * (i % 9), 0.4), fr, j); add(tone(84 + PENT[i % 9], 0.12, 0.12, 30), fr, j)
        for k, v in evs:
            if k == "fin": add(finale(), fr)
    out = np.tanh(out * 1.15) * 0.85
    out = out[:int(nframes / FPS * SR)]
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((out * 32767).astype(np.int16).tobytes())

def mux(video, audio, out):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", audio, "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", out], check=True)
