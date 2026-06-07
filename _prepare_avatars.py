"""
Подготовка фото для аватаров команды.
Использование:
  1. Положи исходные фото (любой размер/формат) в frontend/assets/team/src/
  2. Запусти: python _prepare_avatars.py
  3. Готовые аватары появятся в frontend/assets/team/
"""
from pathlib import Path
from PIL import Image

SRC_DIR  = Path("frontend/assets/team/src")
OUT_DIR  = Path("frontend/assets/team")
SIZE     = 400          # px — финальный квадрат
FACE_TOP = 0.08         # отступ сверху (8% от высоты) — чтобы не срезать макушку
QUALITY  = 90

SRC_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

sources = list(SRC_DIR.glob("*"))
if not sources:
    print(f"Положи исходные фото в {SRC_DIR} и запусти снова.")
    exit()

for src_path in sources:
    if src_path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}:
        continue

    img = Image.open(src_path).convert("RGB")
    w, h = img.size

    # Берём квадрат: ширина = ширина исходника, верхняя граница — 8% от верха
    crop_size = w
    top  = int(h * FACE_TOP)
    left = 0
    # Если высота после отступа меньше ширины — берём всё что есть
    available = h - top
    if available < crop_size:
        crop_size = available

    box = (left, top, left + crop_size, top + crop_size)
    cropped = img.crop(box).resize((SIZE, SIZE), Image.LANCZOS)

    out_name = src_path.stem + ".jpg"
    out_path = OUT_DIR / out_name
    cropped.save(out_path, "JPEG", quality=QUALITY, optimize=True)
    print(f"✓ {src_path.name}  →  {out_path}  ({SIZE}×{SIZE}px, q={QUALITY})")

print("Готово!")
