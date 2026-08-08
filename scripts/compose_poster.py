#!/usr/bin/env python3
"""Compose a split-photo enamel zine poster deterministically."""

from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def parse_size(value: str) -> tuple[int, int]:
    try:
        width, height = (int(part) for part in value.lower().split("x", 1))
    except Exception as exc:
        raise argparse.ArgumentTypeError("size must be WIDTHxHEIGHT") from exc
    if width < 800 or height < 600:
        raise argparse.ArgumentTypeError("size must be at least 800x600")
    return width, height


def parse_color(value: str) -> tuple[int, int, int]:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise argparse.ArgumentTypeError("background must be a six-digit hex color")
    try:
        return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("invalid hex background color") from exc


def cover_crop(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    target_w, target_h = size
    scale = max(target_w / image.width, target_h / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = max(0, (resized.width - target_w) // 2)
    top = max(0, (resized.height - target_h) // 2)
    return resized.crop((left, top, left + target_w, top + target_h))


def contain_fit(image: Image.Image, size: tuple[int, int], background: tuple[int, int, int]) -> Image.Image:
    """Fit the entire source inside the field without cropping any photographic content."""
    target_w, target_h = size
    scale = min(target_w / image.width, target_h / image.height)
    resized = image.resize(
        (max(1, round(image.width * scale)), max(1, round(image.height * scale))),
        Image.Resampling.LANCZOS,
    )
    field = Image.new("RGB", size, background)
    left = (target_w - resized.width) // 2
    top = (target_h - resized.height) // 2
    field.paste(resized, (left, top))
    return field


def safe_cover_fit(image: Image.Image, size: tuple[int, int], background: tuple[int, int, int]) -> Image.Image:
    """Use a subtle centered crop, but contain when the crop would be substantial."""
    target_w, target_h = size
    source_ratio = image.width / image.height
    target_ratio = target_w / target_h
    retained = target_ratio / source_ratio if source_ratio > target_ratio else source_ratio / target_ratio
    if retained < 0.88:
        return contain_fit(image, size, background)
    return cover_crop(image, size)


def choose_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/cour.ttf"),
        Path("C:/Windows/Fonts/consola.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def tracked_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str,
                 font: ImageFont.ImageFont, fill: tuple[int, int, int], tracking: int) -> None:
    x, y = xy
    for char in text:
        draw.text((x, y), char, font=font, fill=fill)
        box = draw.textbbox((x, y), char, font=font)
        x += box[2] - box[0] + tracking


def tracked_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, tracking: int) -> int:
    widths = [draw.textbbox((0, 0), char, font=font)[2] for char in text]
    return sum(widths) + max(0, len(text) - 1) * tracking


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--photo", required=True)
    parser.add_argument("--badge", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--place", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--background", type=parse_color, required=True)
    parser.add_argument("--size", type=parse_size, default=None)
    parser.add_argument(
        "--layout",
        choices=("auto", "left-right", "upper-lower"),
        default="auto",
        help="auto uses upper-lower for landscape photos and left-right otherwise",
    )
    parser.add_argument(
        "--photo-fit",
        choices=("safe-cover", "contain", "cover"),
        default="safe-cover",
        help="safe-cover permits only a subtle crop and otherwise contains the source",
    )
    args = parser.parse_args()

    photo = Image.open(args.photo).convert("RGB")
    layout = args.layout
    if layout == "auto":
        layout = "upper-lower" if photo.width > photo.height else "left-right"

    width, height = args.size or ((1200, 1600) if layout == "upper-lower" else (1600, 1200))
    canvas = Image.new("RGB", (width, height), args.background)

    if layout == "upper-lower":
        split_y = height // 2
        photo_field = (0, 0, width, split_y)
        info_field = (0, split_y, width, height - split_y)
    else:
        split_x = width // 2
        info_field = (0, 0, split_x, height)
        photo_field = (split_x, 0, width - split_x, height)

    photo_x, photo_y, photo_w, photo_h = photo_field
    if args.photo_fit == "contain":
        photo_crop = contain_fit(photo, (photo_w, photo_h), args.background)
    elif args.photo_fit == "safe-cover":
        photo_crop = safe_cover_fit(photo, (photo_w, photo_h), args.background)
    else:
        photo_crop = cover_crop(photo, (photo_w, photo_h))
    canvas.paste(photo_crop, (photo_x, photo_y))

    info_x, info_y, info_w, info_h = info_field

    badge = Image.open(args.badge).convert("RGBA")
    alpha_box = badge.getchannel("A").getbbox()
    if alpha_box is None:
        raise SystemExit("badge has no visible alpha content")
    badge = badge.crop(alpha_box)
    target_w = round(info_w * 0.36)
    target_h = round(info_h * 0.38)
    scale = min(target_w / badge.width, target_h / badge.height)
    badge = badge.resize((max(1, round(badge.width * scale)), max(1, round(badge.height * scale))), Image.Resampling.LANCZOS)

    badge_x = info_x + (info_w - badge.width) // 2
    badge_y = info_y + round(info_h * 0.34) - badge.height // 2
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow_mask = badge.getchannel("A").filter(ImageFilter.GaussianBlur(max(2, width // 500)))
    shadow_layer = Image.new("RGBA", badge.size, (24, 30, 34, 72))
    shadow_layer.putalpha(shadow_mask.point(lambda a: round(a * 0.28)))
    shadow.alpha_composite(shadow_layer, (badge_x + max(3, width // 320), badge_y + max(4, height // 240)))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), shadow)
    canvas.alpha_composite(badge, (badge_x, badge_y))

    line = f"{args.place} | {args.subject} | {args.date}".upper()
    draw = ImageDraw.Draw(canvas)
    font = choose_font(max(15, round(height * 0.018)))
    tracking = max(1, round(width * 0.0013))
    text_w = tracked_width(draw, line, font, tracking)
    max_w = round(info_w * 0.82)
    while text_w > max_w and getattr(font, "size", 12) > 11:
        font = choose_font(font.size - 1)
        text_w = tracked_width(draw, line, font, tracking)
    text_x = max(info_x + round(info_w * 0.06), info_x + (info_w - text_w) // 2)
    text_y = info_y + round(info_h * 0.72)
    tracked_text(draw, (text_x, text_y), line, font, (245, 243, 234), tracking)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output, format="PNG")
    print(f"PASS {output.resolve()} {width}x{height} layout={layout} photo-fit={args.photo_fit}")


if __name__ == "__main__":
    main()

