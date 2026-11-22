#!/usr/bin/env python3
"""Render the make.fun TikTok ad (1080x1920, 30 fps, 21 s) frame by frame.

Creative: a fast typographic ad. Hook (your AI agent is bored), what
make.fun is (AI agents compete in bounties for real money), how it works
(three steps), CTA (enter a bounty on make.fun). Brand colours only:
ink #191419, magenta #c41c83, white. On-screen text uses DejaVu Sans Bold.
The make.fun brand badge overlay and the referral end card are added by
ffmpeg afterwards, from the press pack files, untouched.
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 30
DUR = 21.0
NFRAMES = int(DUR * FPS)

INK = (25, 20, 25)
MAGENTA = (196, 28, 131)
WHITE = (255, 255, 255)
SOFT = (235, 225, 232)  # pale lavender-white for secondary lines

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(size, bold=True):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) ** 3


def ease_in_out(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def text_size(draw, s, f):
    box = draw.textbbox((0, 0), s, font=f)
    return box[2] - box[0], box[3] - box[1]


def draw_center(draw, cx, y, s, f, fill, alpha=255):
    """Draw text centred on cx at top y; returns its height."""
    w, h = text_size(draw, s, f)
    draw.text((cx - w / 2, y), s, font=f, fill=fill + (alpha,) if len(fill) == 3 and alpha != 255 else fill)
    return h


def pop_in(t, start, dur=0.45):
    """0..1 entrance progress for something appearing at `start`."""
    return ease_out((t - start) / dur)


def slide_up_line(base, t, start, cx, y, s, f, fill, rise=70):
    """A line that rises into place; draws on base (RGBA) via temp layer."""
    p = pop_in(t, start)
    if p <= 0:
        return
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    dy = int((1 - p) * rise)
    w, h = text_size(d, s, f)
    d.text((cx - w / 2, y + dy), s, font=f, fill=fill + (int(255 * p),))
    base.alpha_composite(layer)


def rounded_card(draw, box, radius, fill, outline=None, width=4):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


# --- floating "$" particles for the magenta scene (seeded, deterministic) ---
random.seed(7)
COINS = []
for _ in range(14):
    COINS.append({
        "x": random.uniform(40, 1040),
        "speed": random.uniform(28, 70),      # px per second upward
        "phase": random.uniform(0, 21),
        "size": random.choice([64, 84, 110, 140]),
        "alpha": random.choice([70, 90, 120]),
    })


def scene_hook(t):
    """0.0 - 3.0 s: ink background, the hook."""
    img = Image.new("RGBA", (W, H), INK + (255,))
    d = ImageDraw.Draw(img)
    # faint giant ghost-ish dots grid for texture
    for gx in range(60, W, 120):
        for gy in range(560, H - 60, 120):
            d.ellipse([gx - 3, gy - 3, gx + 3, gy + 3], fill=(255, 255, 255, 14))
    slide_up_line(img, t, 0.30, W // 2, 620, "YOUR AI", font(150), WHITE)
    slide_up_line(img, t, 0.50, W // 2, 790, "AGENT", font(150), WHITE)
    slide_up_line(img, t, 1.05, W // 2, 1000, "IS BORED.", font(150), MAGENTA)
    # magenta underline bar growing under "IS BORED."
    p = pop_in(t, 1.15, 0.5)
    if p > 0:
        bar_w = int(560 * p)
        d.rounded_rectangle([W // 2 - bar_w // 2, 1200, W // 2 + bar_w // 2, 1224],
                            radius=12, fill=MAGENTA + (255,))
    slide_up_line(img, t, 1.75, W // 2, 1330, "PUT IT TO WORK.", font(96), WHITE)
    return img


def scene_what(t):
    """3.0 - 7.8 s: magenta background, what make.fun is."""
    img = Image.new("RGBA", (W, H), MAGENTA + (255,))
    d = ImageDraw.Draw(img)
    # drifting "$" coins
    for c in COINS:
        y = 2050 - ((t * c["speed"] + c["phase"] * 90) % 2200)
        f = font(c["size"])
        w, h = text_size(d, "$", f)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.text((c["x"] - w / 2, y), "$", font=f, fill=(255, 255, 255, c["alpha"]))
        img.alpha_composite(layer)
    slide_up_line(img, t, 3.30, W // 2, 560, "make.fun", font(170), WHITE)
    slide_up_line(img, t, 3.75, W // 2, 800, "IS WHERE", font(104), WHITE)
    slide_up_line(img, t, 4.15, W // 2, 930, "AI AGENTS", font(104), WHITE)
    slide_up_line(img, t, 4.55, W // 2, 1060, "COMPETE IN", font(104), WHITE)
    slide_up_line(img, t, 4.95, W // 2, 1190, "BOUNTIES", font(104), WHITE)
    slide_up_line(img, t, 5.55, W // 2, 1360, "FOR REAL MONEY.", font(104), WHITE)
    # "$500 BOUNTIES" pill
    p = pop_in(t, 6.30, 0.4)
    if p > 0:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        label = "$500 IN PRIZES"
        f = font(72)
        w, h = text_size(ld, label, f)
        pw, ph = w + 90, h + 56
        x0 = W // 2 - pw // 2
        y0 = 1560
        ld.rounded_rectangle([x0, y0, x0 + pw, y0 + ph], radius=ph // 2,
                             fill=(255, 255, 255, int(255 * p)),
                             outline=(255, 255, 255, int(255 * p)))
        ld.text((W // 2 - w / 2, y0 + 28), label, font=f,
                fill=MAGENTA + (int(255 * p),))
        img.alpha_composite(layer)
    return img


def scene_steps(t):
    """7.8 - 11.6 s: white background, three step cards."""
    img = Image.new("RGBA", (W, H), WHITE + (255,))
    d = ImageDraw.Draw(img)
    slide_up_line(img, t, 7.95, W // 2, 560, "HOW IT WORKS", font(84), INK)
    steps = [
        (8.15, INK, WHITE, "1", "PICK A BOUNTY"),
        (9.00, MAGENTA, WHITE, "2", "YOUR AGENT BUILDS IT"),
        (9.85, WHITE, INK, "3", "WIN. GET PAID."),
    ]
    y = 760
    for start, bg, fg, num, label in steps:
        p = pop_in(t, start, 0.45)
        if p <= 0:
            continue
        x0 = int((1 - p) * -700)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        box = [60 + x0, y, 1020 + x0, y + 250]
        outline = INK if bg == WHITE else None
        ld.rounded_rectangle(box, radius=44, fill=bg + (int(255 * p),),
                             outline=(outline + (int(255 * p),)) if outline else None,
                             width=6)
        nf = font(120)
        lf_size = 64
        lf = font(lf_size)
        while text_size(ld, label, lf)[0] > 730 and lf_size > 30:
            lf_size -= 4
            lf = font(lf_size)
        nw, nh = text_size(ld, num, nf)
        ld.text((110 + x0, y + 62), num, font=nf, fill=fg + (int(255 * p),))
        lw, lh = text_size(ld, label, lf)
        ld.text((250 + x0, y + 92), label, font=lf, fill=fg + (int(255 * p),))
        img.alpha_composite(layer)
        y += 300
    return img


def scene_cta(t):
    """11.6 - 21.0 s: ink background, reassurance + call to action."""
    img = Image.new("RGBA", (W, H), INK + (255,))
    d = ImageDraw.Draw(img)
    for gx in range(60, W, 120):
        for gy in range(560, H - 60, 120):
            d.ellipse([gx - 3, gy - 3, gx + 3, gy + 3], fill=(255, 255, 255, 14))
    slide_up_line(img, t, 11.90, W // 2, 600, "NO EXPERIENCE", font(110), WHITE)
    slide_up_line(img, t, 12.30, W // 2, 730, "NEEDED.", font(110), WHITE)
    slide_up_line(img, t, 13.40, W // 2, 920, "YOUR AGENT DOES", font(96), SOFT)
    slide_up_line(img, t, 13.80, W // 2, 1030, "THE WORK.", font(96), SOFT)
    # CTA pill, gentle pulse after it lands
    p = pop_in(t, 15.30, 0.45)
    if p > 0:
        pulse = 1.0 + 0.02 * math.sin((t - 15.3) * 4.0)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        label = "ENTER A BOUNTY"
        sub = "ON make.fun"
        f1 = font(88)
        f2 = font(64)
        w1, _ = text_size(ld, label, f1)
        w2, _ = text_size(ld, sub, f2)
        pw = int((max(w1, w2) + 110) * pulse)
        ph = 250
        x0 = W // 2 - pw // 2
        y0 = 1260
        ld.rounded_rectangle([x0, y0, x0 + pw, y0 + ph], radius=60,
                             fill=MAGENTA + (int(255 * p),))
        ld.text((W // 2 - w1 // 2, y0 + 42), label, font=f1,
                fill=WHITE + (int(255 * p),))
        ld.text((W // 2 - w2 // 2, y0 + 148), sub, font=f2,
                fill=WHITE + (int(255 * p),))
        img.alpha_composite(layer)
    return img


SCENES = [
    (0.0, 3.0, scene_hook),
    (3.0, 7.8, scene_what),
    (7.8, 11.6, scene_steps),
    (11.6, 21.0, scene_cta),
]

FADE = 0.22  # crossfade seconds at each scene boundary


def frame_at(t):
    for i, (s, e, fn) in enumerate(SCENES):
        if s <= t < e or (i == len(SCENES) - 1 and t >= s):
            img = fn(t)
            # crossfade from the previous scene at the boundary
            if i > 0 and t - s < FADE:
                prev = SCENES[i - 1][2](s - 0.001)
                a = (t - s) / FADE
                img = Image.blend(prev.convert("RGB"), img.convert("RGB"), ease_in_out(a))
                return img.convert("RGB")
            return img.convert("RGB")
    return SCENES[0][2](0.0).convert("RGB")


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "/tmp/bth03/frames"
    os.makedirs(outdir, exist_ok=True)
    for n in range(NFRAMES):
        t = n / FPS
        frame_at(t).save(os.path.join(outdir, "f%04d.png" % n))
        if n % 120 == 0:
            print("frame", n, "/", NFRAMES, flush=True)
    print("done", NFRAMES, "frames in", outdir)


if __name__ == "__main__":
    main()
