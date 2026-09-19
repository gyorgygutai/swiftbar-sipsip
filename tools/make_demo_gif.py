#!/usr/bin/env python3
"""Animated README demo GIF for the sipsip SwiftBar plugin.

Square 1:1 canvas, icon large and centered, cycling through the click states:
off -> 10m -> 20m -> 30m -> 40m -> off

Black glyphs (as authored) on white so it reads on GitHub's light background;
the 'off' state uses its built-in dimmed alpha. Between states a quick
press-pulse (shrink + dim) sells the click. Frames are drawn with PIL,
encoded with ffmpeg two-pass palettegen.

Usage:
    python3 tools/make_demo_gif.py [--out assets/caffeinete_demo.gif] [--size 320]
"""

import argparse
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parent.parent
ASSETS = REPO / "assets"

# --- Canvas ---------------------------------------------------------------
FPS = 12
HOLD_S = 0.6        # hold per timer state
OFF_HOLD_S = 0.75   # slightly longer on 'off' so the loop start reads clearly
FLASH_S = 0.12      # click press duration between states
PRESS_SCALE = 0.90  # icon scale during the press pulse
PRESS_ALPHA = 0.45  # icon alpha multiplier during the press pulse

ORDER = ["off", "10m", "20m", "30m", "40m"]


def load_icons() -> dict[str, Image.Image]:
    icons = {}
    for s in ORDER:
        p = ASSETS / f"sipsip_icon-{s}.png"
        img = Image.open(p).convert("RGBA")
        if img.size != (44, 44):
            img = img.resize((44, 44), Image.LANCZOS)
        icons[s] = img
    return icons


def make_frame(icon: Image.Image, canvas: int, icon_px: int, pressed: bool) -> Image.Image:
    frame = Image.new("RGB", (canvas, canvas), (255, 255, 255))

    big = icon.resize((icon_px, icon_px), Image.LANCZOS)
    if pressed:
        px = round(icon_px * PRESS_SCALE)
        big = big.resize((px, px), Image.LANCZOS)
        a = big.getchannel("A").point(lambda v: int(v * PRESS_ALPHA))
        big.putalpha(a)

    ix = (canvas - big.width) // 2
    iy = (canvas - big.height) // 2
    frame.paste(big, (ix, iy), big)
    return frame


def build_frames(icons: dict[str, Image.Image], canvas: int, icon_px: int) -> list[Image.Image]:
    frames = []
    for i, state in enumerate(ORDER):
        hold = OFF_HOLD_S if state == "off" else HOLD_S
        frames += [make_frame(icons[state], canvas, icon_px, pressed=False)] * round(hold * FPS)
        if i < len(ORDER) - 1:
            frames += [make_frame(icons[state], canvas, icon_px, pressed=True)] * round(FLASH_S * FPS)
    # loop wrap: press on the last state, then it releases into the opening 'off'
    frames += [make_frame(icons[ORDER[-1]], canvas, icon_px, pressed=True)] * round(FLASH_S * FPS)
    return frames


def encode_gif(frames_dir: Path, out: Path, fps: int) -> None:
    pal = frames_dir / "palette.png"
    pattern = str(frames_dir / "f_%04d.png")
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error",
         "-framerate", str(fps), "-i", pattern,
         "-vf", "palettegen=stats_mode=diff",
         str(pal)],
        check=True,
    )
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error",
         "-framerate", str(fps), "-i", pattern,
         "-i", str(pal),
         "-lavfi", "paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle",
         "-loop", "0",
         str(out)],
        check=True,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ASSETS / "sipsip_demo.gif"))
    ap.add_argument("--size", type=int, default=320, help="square canvas size in px")
    ap.add_argument("--icon", type=int, default=0,
                    help="icon size in px (default: 56%% of canvas, multiple of 44)")
    args = ap.parse_args()

    canvas = args.size
    icon_px = args.icon or max(1, round(canvas * 0.56 / 44) * 44)

    out = Path(args.out).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    icons = load_icons()
    frames = build_frames(icons, canvas, icon_px)

    with tempfile.TemporaryDirectory() as td:
        fd = Path(td)
        for i, fr in enumerate(frames):
            fr.save(fd / f"f_{i:04d}.png")
        encode_gif(fd, out, FPS)

    size_kb = out.stat().st_size / 1024
    n = len(frames)
    print(f"wrote {out}  ({canvas}x{canvas}, {n} frames, {n / FPS:.2f}s loop, {size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
