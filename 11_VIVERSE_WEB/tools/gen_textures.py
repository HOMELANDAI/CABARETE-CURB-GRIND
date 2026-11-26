"""CCG web build — procedural tileable PBR texture generator (numpy + Pillow).
Writes <name>_c.jpg (albedo, sRGB), <name>_n.jpg (OpenGL normal), <name>_orm.jpg (R=AO, G=rough, B=metal)
into 11_VIVERSE_WEB/assets/tex/. Every map tiles seamlessly (FFT-filtered noise on a torus).
Run:  python3 tools/gen_textures.py [size]
"""
import os, sys
import numpy as np
from PIL import Image

N = int(sys.argv[1]) if len(sys.argv) > 1 else 2048
OUT = os.path.join(os.path.dirname(__file__), '..', 'assets', 'tex')
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(20261126)
fy = np.fft.fftfreq(N)[:, None]; fx = np.fft.fftfreq(N)[None, :]
FR = np.sqrt(fx * fx + fy * fy); FR[0, 0] = 1.0


def fractal(beta=2.0, lo=0.0, hi=0.5, aniso=(1.0, 1.0)):
    """Tileable 1/f^beta noise normalised to 0..1. aniso stretches the spectrum."""
    w = rng.standard_normal((N, N))
    fr = np.sqrt((fx * aniso[0]) ** 2 + (fy * aniso[1]) ** 2); fr[0, 0] = 1.0
    filt = fr ** (-beta / 2.0)
    filt[(fr < lo) | (fr > hi)] = 0.0
    filt[0, 0] = 0.0
    r = np.real(np.fft.ifft2(np.fft.fft2(w) * filt))
    r -= r.min(); r /= (r.max() + 1e-9)
    return r


def band(f0, f1, beta=1.0):
    return fractal(beta, f0, f1)


def blur(a, px):
    """Periodic gaussian blur (FFT)."""
    s = px / N
    g = np.exp(-2 * (np.pi ** 2) * (s ** 2) * (fx ** 2 + fy ** 2) * N * N / N / N * (N ** 2) / (N ** 2))
    g = np.exp(-2 * (np.pi * px) ** 2 * (fx ** 2 + fy ** 2))
    return np.real(np.fft.ifft2(np.fft.fft2(a) * g))


def speckle(density, size_px, seed_scale=1.0):
    """Tileable sparse blobs (aggregate stones, grains)."""
    w = (rng.random((N, N)) < density).astype(np.float64)
    w *= rng.random((N, N)) * seed_scale + (1 - seed_scale)
    b = blur(w, size_px)
    b /= (b.max() + 1e-9)
    return b


def cells(count, jitter=1.0):
    """Tileable Worley F1/F2 (cracked stone, cobbles)."""
    pts = rng.random((count, 2))
    ys, xs = np.mgrid[0:N, 0:N] / N
    f1 = np.full((N, N), 9.0); f2 = np.full((N, N), 9.0); idx = np.zeros((N, N), np.int32)
    for i, (px, py) in enumerate(pts):
        dx = np.abs(xs - px); dx = np.minimum(dx, 1 - dx)
        dy = np.abs(ys - py); dy = np.minimum(dy, 1 - dy)
        d = np.sqrt(dx * dx + dy * dy)
        m = d < f1
        f2 = np.where(m, f1, np.minimum(f2, d)); idx = np.where(m, i, idx); f1 = np.where(m, d, f1)
    return f1, f2, idx


def normal_from_height(h, strength):
    gx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * 0.5 * strength * N / 1024
    gy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * 0.5 * strength * N / 1024
    nx, ny, nz = -gx, gy, np.ones_like(h)   # OpenGL convention (+Y up in tangent space)
    l = np.sqrt(nx * nx + ny * ny + nz * nz)
    return np.stack([nx / l, ny / l, nz / l], -1) * 0.5 + 0.5


def ao_from_height(h, px=6, k=2.5):
    return np.clip(1.0 - k * np.maximum(0, blur(h, px) - h), 0, 1)


def save(name, color, height, rough, metal=0.0, nstrength=6.0, ao_k=2.5):
    c = np.clip(color, 0, 1)
    Image.fromarray((c * 255 + 0.5).astype(np.uint8)).save(os.path.join(OUT, name + '_c.jpg'), quality=92)
    n = normal_from_height(height, nstrength)
    Image.fromarray((n * 255 + 0.5).astype(np.uint8)).save(os.path.join(OUT, name + '_n.jpg'), quality=94)
    ao = ao_from_height(height, k=ao_k)
    m = np.full((N, N), metal) if np.isscalar(metal) else metal
    orm = np.stack([ao, np.clip(rough, 0.02, 1), np.clip(m, 0, 1)], -1)
    Image.fromarray((orm * 255 + 0.5).astype(np.uint8)).save(os.path.join(OUT, name + '_orm.jpg'), quality=92)
    print('wrote', name)


def lerp(a, b, t):
    t = t[..., None] if np.ndim(t) == 2 else t
    return np.asarray(a) * (1 - t) + np.asarray(b) * t


def srgb(hexs):
    return np.array([int(hexs[i:i + 2], 16) / 255 for i in (1, 3, 5)])


# --- Asphalt: aggregate, binder, patched cracks, oil, sun-bleached wear (1 tile = 4 m) ---------------
def asphalt():
    big = fractal(2.2, 0, 0.02); mid = fractal(1.6, 0.01, 0.2)
    agg = speckle(0.018, 1.3); agg2 = speckle(0.05, 0.7)
    f1, f2, _ = cells(26)
    crack = np.clip(1 - (f2 - f1) * 90, 0, 1) ** 3 * (fractal(2.0, 0, 0.05) > 0.55)
    oil = np.clip((fractal(2.6, 0, 0.03) - 0.68) * 6, 0, 1)
    tone = 0.20 + 0.10 * big + 0.06 * mid
    col = np.stack([tone] * 3, -1) * srgb('#d8d4cc')
    col = lerp(col, srgb('#8f8a80'), np.clip(agg * 1.3, 0, 1) * 0.55)
    col = lerp(col, srgb('#c9c3b6'), np.clip(agg2 * 1.6 - 0.5, 0, 1) * 0.5)
    col = lerp(col, srgb('#101010'), crack * 0.85)
    col = lerp(col, srgb('#15130f'), oil * 0.5)
    h = 0.5 * agg + 0.3 * agg2 + 0.15 * mid - 0.9 * crack
    rough = 0.86 - 0.18 * agg - 0.35 * oil + 0.05 * mid
    save('asphalt', col, h, rough, nstrength=9)


# --- Skatepark concrete: trowel swirls, fine pores, scuffs, joints every half tile (tile = 4 m) -----
def concrete():
    big = fractal(2.4, 0, 0.02); swirl = fractal(1.2, 0.002, 0.05, aniso=(1.0, 3.0))
    pores = speckle(0.03, 0.6); scuff = np.clip((fractal(1.8, 0.002, 0.12) - 0.62) * 4, 0, 1)
    ys, xs = np.mgrid[0:N, 0:N] / N
    jd = np.minimum(np.minimum(xs % 0.5, 0.5 - xs % 0.5), np.minimum(ys % 0.5, 0.5 - ys % 0.5))
    joint = np.clip(1 - jd * N / 3.0, 0, 1)
    tone = 0.62 + 0.10 * big + 0.05 * swirl
    col = np.stack([tone] * 3, -1) * srgb('#e9e4da')
    col = lerp(col, srgb('#7d786f'), pores * 0.6)
    col = lerp(col, srgb('#4b4741'), scuff * 0.45)
    col = lerp(col, srgb('#3a3732'), joint * 0.8)
    h = 0.25 * swirl - 0.6 * pores - 1.2 * joint + 0.1 * big
    rough = 0.62 + 0.1 * swirl - 0.18 * scuff + 0.2 * pores
    save('concrete', col, h, rough, nstrength=5)


# --- Pavers: running-bond clay pavers with sand joints (tile = 2 m) --------------------------------
def pavers():
    ys, xs = np.mgrid[0:N, 0:N] / N
    rows = 10; cols = 5
    r = np.floor(ys * rows); off = (r % 2) * 0.5
    u = (xs * cols + off) % 1.0; v = (ys * rows) % 1.0
    bid = (np.floor(xs * cols + off) * 31 + r * 17) % 97
    edge = np.minimum(np.minimum(u, 1 - u) * 3.2, np.minimum(v, 1 - v) * 1.0)
    bevel = np.clip(edge * 14, 0, 1)
    var = (bid / 97.0)
    noise = fractal(1.5, 0.01, 0.3)
    base = lerp(srgb('#a8553a'), srgb('#c98a5e'), var)
    base = lerp(base, srgb('#6e3a28'), noise * 0.35)
    col = lerp(srgb('#bfb39a') * np.ones((N, N, 3)), base, bevel)
    h = bevel * 0.8 + noise * 0.15
    rough = 0.75 + 0.15 * (1 - bevel)
    save('pavers', col, h, rough, nstrength=7)


# --- Beach sand: wind ripples + grains + shell bits (tile = 6 m) ---------------------------------
def sand():
    ys, xs = np.mgrid[0:N, 0:N] / N
    warp = fractal(2.2, 0, 0.03)
    rip = 0.5 + 0.5 * np.sin((ys * 14 + warp * 3.0 + 0.2 * np.sin(xs * 2 * np.pi * 2)) * 2 * np.pi)
    grains = speckle(0.25, 0.5); shells = speckle(0.002, 1.0)
    big = fractal(2.4, 0, 0.02)
    col = lerp(srgb('#d9c29a'), srgb('#f0e2c4'), big * 0.7 + rip * 0.2)
    col = lerp(col, srgb('#a8916b'), np.clip(grains - 0.4, 0, 1) * 0.6)
    col = lerp(col, srgb('#fffaf0'), np.clip(shells * 2, 0, 1) * 0.6)
    h = rip * 0.6 + grains * 0.25 + big * 0.2
    rough = 0.92 - 0.05 * rip
    save('sand', col, h, rough, nstrength=4)


# --- Stucco / painted plaster (white base; buildings tint per instance), with drips & dirt at bottom ---
def stucco():
    knock = np.clip(fractal(1.1, 0.03, 0.4) - 0.45, 0, 1) * 2
    fine = speckle(0.2, 0.6); big = fractal(2.4, 0, 0.02)
    ys = np.mgrid[0:N, 0:N][0] / N
    drip = np.clip((fractal(1.0, 0.0, 0.5, aniso=(1.0, 0.04)) - 0.6) * 3, 0, 1)
    tone = 0.86 + 0.08 * big - 0.05 * fine
    col = np.stack([tone] * 3, -1) * srgb('#fbf7ef')
    col = lerp(col, srgb('#8c8170'), drip * 0.35)
    h = knock * 0.7 + fine * 0.2
    rough = 0.88 - 0.1 * knock
    save('stucco', col, h, rough, nstrength=6)


# --- Corrugated zinc roof with rust streaks (tile = 2 m) ------------------------------------------
def roof():
    xs = np.mgrid[0:N, 0:N][1] / N
    corr = 0.5 + 0.5 * np.sin(xs * 2 * np.pi * 26)
    rust = np.clip((fractal(1.8, 0, 0.1, aniso=(1.0, 0.25)) - 0.5) * 3, 0, 1)
    dirt = fractal(2.0, 0, 0.05)
    col = lerp(srgb('#9aa3a6'), srgb('#c5cccd'), dirt * 0.6 + corr * 0.15)
    col = lerp(col, srgb('#8a4a25'), rust * 0.75)
    h = corr
    rough = 0.45 + 0.4 * rust + 0.1 * dirt
    metal = 0.85 * (1 - rust)
    save('roof', col, h, rough, metal, nstrength=10)


# --- Weathered wood planks (tile = 2 m, planks along X) ---------------------------------------------
def wood():
    ys, xs = np.mgrid[0:N, 0:N] / N
    planks = 8; p = np.floor(ys * planks); v = (ys * planks) % 1
    grain = fractal(1.0, 0.0, 0.5, aniso=(0.03, 1.0))
    gap = np.clip(1 - np.minimum(v, 1 - v) * 40, 0, 1)
    shade = ((p * 37) % 11) / 11
    col = lerp(srgb('#7a5534'), srgb('#b8875a'), grain * 0.7 + shade * 0.3)
    col = lerp(col, srgb('#2b1d12'), gap)
    h = grain * 0.3 - gap
    rough = 0.7 + 0.2 * grain
    save('wood', col, h, rough, nstrength=6)


# --- Steel: brushed + grind-polished, chipped paint (tile = 1 m) ------------------------------------
def steel():
    brush = fractal(1.0, 0.0, 0.5, aniso=(0.02, 1.0))
    chips = np.clip((fractal(1.6, 0.01, 0.3) - 0.66) * 6, 0, 1)
    wear = fractal(2.2, 0, 0.03)
    col = lerp(srgb('#8d9399'), srgb('#c9ced2'), brush * 0.5 + wear * 0.3)
    col = lerp(col, srgb('#3d4245'), chips * 0.5)
    h = brush * 0.2 - chips * 0.3
    rough = 0.22 + 0.25 * brush + 0.35 * chips
    metal = 1.0 - 0.6 * chips
    save('steel', col, h, rough, metal, nstrength=2)


# --- Painted wall (mural backs, curbs) --------------------------------------------------------------
def wallpaint():
    big = fractal(2.3, 0, 0.03); fine = speckle(0.15, 0.6)
    peel = np.clip((fractal(1.7, 0.01, 0.2) - 0.7) * 5, 0, 1)
    col = lerp(srgb('#e9e1d2'), srgb('#d1c6b2'), big)
    col = lerp(col, srgb('#9a9286'), peel * 0.7)
    h = fine * 0.2 - peel * 0.4
    rough = 0.85
    save('wallpaint', col, h, rough, nstrength=4)


# --- Tropical grass + dirt ---------------------------------------------------------------------------
def grass():
    blades = fractal(0.6, 0.05, 0.5); big = fractal(2.4, 0, 0.02); dry = fractal(2.0, 0, 0.04)
    col = lerp(srgb('#3f6b26'), srgb('#7fa046'), blades * 0.6 + big * 0.4)
    col = lerp(col, srgb('#a99a5c'), np.clip((dry - 0.55) * 3, 0, 1) * 0.7)
    save('grass', col, blades, 0.9, nstrength=5)


def dirt():
    big = fractal(2.3, 0, 0.03); peb = speckle(0.02, 1.2); fine = speckle(0.2, 0.5)
    col = lerp(srgb('#7b5a3c'), srgb('#a98260'), big)
    col = lerp(col, srgb('#cbb79a'), peb * 0.6)
    h = peb * 0.7 + fine * 0.2 + big * 0.2
    save('dirt', col, h, 0.93, nstrength=7)


# --- Ocean detail normal (two-octave wave field, tileable) -----------------------------------------
def water_normal():
    h = fractal(3.0, 0.002, 0.12) * 0.7 + fractal(2.0, 0.02, 0.4) * 0.3
    n = normal_from_height(h, 14)
    Image.fromarray((n * 255 + 0.5).astype(np.uint8)).save(os.path.join(OUT, 'water_n.jpg'), quality=94)
    print('wrote water_n')


for fn in (asphalt, concrete, pavers, sand, stucco, roof, wood, steel, wallpaint, grass, dirt, water_normal):
    fn()
