---
name: life-fridge-magnet
description: "Create a clean 生活冰箱贴 photo poster with adaptive orientation, a vivid source-derived enamel fridge-magnet illustration, EXIF date and exposure metadata, an optional address, and badge-derived color swatches. Landscape photos produce a portrait 3:4 upper/lower layout; portrait photos produce a landscape 4:3 left/right layout."
---

# 生活冰箱贴

Create one finished raster poster that combines truthful photography with a compact souvenir-pin abstraction. Read [references/visual-system.md](references/visual-system.md) before composing.

## Input roles

- Lock the current user upload as `USER_PHOTO`.
- Use `assets/reference.png` only to understand layout and visual hierarchy.
- Never substitute the reference for the user's photograph.
- Use the photograph as the sole semantic source for the badge.

## Required result

- Match the poster canvas to the split direction: landscape input produces a portrait 3:4 poster, normally `1200 × 1600`; portrait or square input produces a landscape 4:3 poster, normally `1600 × 1200`.
- Detect the source orientation before composition:
  - Landscape (`width > height`): place the original photograph in the upper half and the information field in the lower half.
  - Portrait or square (`width <= height`): place the information field on the left and the original photograph on the right.
- Use a flush 50/50 split with no gutter, border, or divider.
- Fill the information field with one flat, relatively high-lightness color sampled or harmonized from the photo. Keep it bright enough to feel lively while preserving text and badge contrast.
- Use `safe-cover` by default: allow only a subtle crop needed to make the photograph span its panel, and automatically fall back to `contain` when more than 12% of the source would be removed. Apply no generative editing, filters, grading, frames, or added text.
- Keep the primary subject fully visible, including distinctive extremities such as ears, horns, limbs, tail, head, and held objects. If a centered safe crop would touch the subject, use `contain` instead.
- Center one small, vivid enamel-pin illustration in the information field, slightly above its midpoint.
- Place two quiet uppercase metadata lines below the pin: date and address first, then aperture, ISO, and shutter speed.
- Place 2–6 small solid color swatches below the metadata. Derive them from the enamel badge unless the user supplies a palette.
- When address, aperture, ISO, or shutter data is unavailable, retain the field label and leave its value empty. Never invent metadata.
- Add no logo, watermark, title, caption, coordinate, border, or unrelated decorative icon.

## Workflow

1. Inspect `USER_PHOTO`. Identify one primary subject, one background landmark or habitat cue, a bright harmonious information-field color, and EXIF date, aperture, ISO, shutter speed, and GPS/address when present. If EXIF date is absent, use the artwork date and state this choice. Leave all other unavailable metadata values empty rather than asking or guessing unless the user explicitly wants to supply an address.
2. Treat `assets/reference.png` as style evidence only. Do not copy its moose, mountains, wording, or colors.
3. Generate only the badge artwork with the built-in image-generation tool:
   - Use `USER_PHOTO` as semantic reference.
   - Depict the primary subject in front of one simplified setting contour.
   - Use antique-gold metal outlines, vivid source-derived enamel fills, and 2–4 internal color regions.
   - Keep the silhouette compact, horizontally stable, and readable at small size.
   - Generate on a perfectly flat `#FF00FF` chroma-key background, with no shadow, text, letters, border, or photographic pixels.
4. Remove the chroma key with the installed imagegen helper. Prefer:

   `python <imagegen-skill>/scripts/remove_chroma_key.py --input BADGE_SOURCE --out BADGE_ALPHA.png --auto-key border --soft-matte --transparent-threshold 12 --opaque-threshold 220 --despill`

   Validate transparent corners, crisp gold edges, no magenta fringe, and no photographic region. Retry once with `--edge-contract 1` if needed.
5. Run `scripts/compose_poster.py` with the locked photo, transparent badge, factual metadata, and sampled high-lightness background color. Keep `--layout auto --photo-fit safe-cover`. Use `contain` whenever the subject approaches a crop edge; never use `cover` when it cuts into the primary subject. Omit `--palette` to extract swatches automatically from the badge, or pass 2–6 comma-separated hex colors.
6. Inspect the final poster. Confirm the photo field contains the user's unchanged photo, the detected orientation produced the correct structure, the badge is small and centered above the metadata, missing values remain empty, the information background is uniform and bright, and the swatches match the badge.
7. Save one non-overwriting PNG and return its path with a one-sentence description.

## Badge prompt requirements

Always state:

- `Image 1 is the user photograph and is semantic evidence only.`
- `Create a new enamel souvenir pin; do not reproduce, embed, crop, trace, or retain photographic pixels.`
- `Use one compact antique-gold outline, a simplified primary subject, and one setting contour.`
- `Background must be perfectly flat solid #FF00FF with no texture, lighting, gradient, floor, or shadow.`
- `Do not use magenta anywhere in the pin.`
- `No text, letters, numbers, logo, watermark, frame, cast shadow, or mockup.`

## Composition command

```powershell
python scripts/compose_poster.py `
  --photo USER_PHOTO `
  --badge BADGE_ALPHA.png `
  --output FINAL.png `
  --date "SEP 27TH 2024" `
  --address "GRAND TETON" `
  --aperture "F/2.8" `
  --iso "1000" `
  --shutter "1/125S" `
  --background "#AFC9B5" `
  --palette "#E83224,#FFF0C4,#121212,#19C3DE" `
  --layout auto `
  --photo-fit safe-cover
```

## Rejection rules

Reject and revise when:

- the photographic panel is generated, filtered, or replaced;
- the primary subject is clipped or the default composition crops any part of the source photograph;
- a landscape source does not use an upper/lower structure;
- a portrait source does not use a left/right structure;
- the badge resembles a photo cutout, sticker, logo, cartoon, or realistic miniature scene;
- the pin is larger than 45% of the left-panel width;
- the background contains texture, gradient, shadow, or a second color field;
- metadata differs from EXIF, a missing value is fabricated, or field labels are missing;
- swatches are missing, unrelated to the badge, or rendered as gradients;
- extra metadata or decoration appears;
- the source relationship is lost: subject in front, setting cue behind.

