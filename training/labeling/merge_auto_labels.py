import os
from pathlib import Path
from pathlib import Path
import shutil

AUTO_LABELS = Path(str(Path(os.environ.get("YEAR2_DATA_ROOT", str(Path(__file__).resolve().parent / "data"))) / 'Train-1/auto_labels'))
AUTO_IMAGES = Path(str(Path(os.environ.get("YEAR2_DATA_ROOT", str(Path(__file__).resolve().parent / "data"))) / 'Train-1/new_images'))

DST_LABELS = Path(str(Path(os.environ.get("YEAR2_DATA_ROOT", str(Path(__file__).resolve().parent / "data"))) / 'Data_done/Thùng mì SiuKay/images/train'))
DST_IMAGES = Path(str(Path(os.environ.get("YEAR2_DATA_ROOT", str(Path(__file__).resolve().parent / "data"))) / 'Data_done/Thùng mì SiuKay/labels/train'))

DST_LABELS.mkdir(parents=True, exist_ok=True)
DST_IMAGES.mkdir(parents=True, exist_ok=True)

added = 0
skipped = 0

for txt in AUTO_LABELS.glob("*.txt"):
    name = txt.stem
    dst_txt = DST_LABELS / txt.name
    dst_img = DST_IMAGES / f"{name}.jpg"

    # nếu đã có label tay → bỏ
    if dst_txt.exists():
        skipped += 1
        continue

    src_img = AUTO_IMAGES / f"{name}.jpg"
    if not src_img.exists():
        continue

    shutil.copy(txt, dst_txt)
    shutil.copy(src_img, dst_img)
    added += 1

print(f"✅ Gộp xong | Thêm: {added} | Bỏ qua (đã label tay): {skipped}")
