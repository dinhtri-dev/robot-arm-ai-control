import os
from pathlib import Path
from ultralytics import YOLO
from pathlib import Path

# ================= CONFIG =================
MODEL_PATH = str(Path(os.environ.get("YEAR2_DATA_ROOT", str(Path(__file__).resolve().parent / "data"))) / 'Train-1/runs/detect/mi_siu_kay_v1/weights/best.pt')
NEW_IMAGES_DIR = Path(str(Path(os.environ.get("YEAR2_DATA_ROOT", str(Path(__file__).resolve().parent / "data"))) / 'Train-1/new_images'))
OUTPUT_LABEL_DIR = Path("auto_labels")

CONF_THRES = 0.4          # khuyến nghị 0.3–0.5
CLASS_ID = 0              # mi_siu_kay
# =========================================``

OUTPUT_LABEL_DIR.mkdir(exist_ok=True)

model = YOLO(MODEL_PATH)

results = model.predict(
    source=str(NEW_IMAGES_DIR),
    conf=CONF_THRES,
    save=False,
    verbose=False
)

total_boxes = 0

for r in results:
    img_path = Path(r.path)
    label_path = OUTPUT_LABEL_DIR / f"{img_path.stem}.txt"

    lines = []

    if r.boxes is not None:
        for box in r.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])

            if cls != CLASS_ID:
                continue

            # YOLO normalized xywh (0–1)
            x, y, w, h = box.xywhn[0].tolist()

            # bỏ box quá nhỏ / dị
            if w < 0.02 or h < 0.02:
                continue

            lines.append(f"{cls} {x:.6f} {y:.6f} {w:.6f} {h:.6f}")
            total_boxes += 1

    # ghi file label (kể cả rỗng)
    with open(label_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

print(f"✅ Auto-label xong | Tổng box: {total_boxes}")
