import os
from pathlib import Path
import json
import os

# ===== CONFIG =====
LS_JSON = str(Path(os.environ.get("YEAR2_DATA_ROOT", str(Path(__file__).resolve().parent / "data"))) / 'Year2/kĩ thuật robot/DATA/ky thuat robot.v1i.coco/train/_annotations.coco.json')
IMAGE_BASE_PATH = str(Path(os.environ.get("YEAR2_DATA_ROOT", str(Path(__file__).resolve().parent / "data"))) / 'Year2/kĩ thuật robot/DATA/IMAGES')
LABEL_BASE_PATH = str(Path(os.environ.get("YEAR2_DATA_ROOT", str(Path(__file__).resolve().parent / "data"))) / 'Year2/kĩ thuật robot/DATA/LABEL')


CLASS_MAP = {
    "mi_siu_kay": 0
}

# ==================

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

with open(LS_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

for task in data:
    image_path = task["data"]["image"]

    # lấy tên ảnh
    image_name = os.path.basename(image_path)
    image_id, _ = os.path.splitext(image_name)

    # xác định train / val
    if os.path.exists(os.path.join(IMAGE_BASE_PATH, "train", image_name)):
        split = "train"
    elif os.path.exists(os.path.join(IMAGE_BASE_PATH, "val", image_name)):
        split = "val"
    else:
        print(f"[SKIP] Không tìm thấy ảnh: {image_name}")
        continue

    label_dir = os.path.join(LABEL_BASE_PATH, split)
    ensure_dir(label_dir)

    label_file = os.path.join(label_dir, image_id + ".txt")

    yolo_lines = []

    annotations = task.get("annotations", [])
    if not annotations:
        continue

    for ann in annotations:
        for result in ann["result"]:
            if result["type"] != "rectanglelabels":
                continue

            label_name = result["value"]["rectanglelabels"][0]
            class_id = CLASS_MAP.get(label_name)

            if class_id is None:
                continue

            # Label Studio dùng %
            x = result["value"]["x"] / 100
            y = result["value"]["y"] / 100
            w = result["value"]["width"] / 100
            h = result["value"]["height"] / 100

            # YOLO cần center
            x_center = x + w / 2
            y_center = y + h / 2

            yolo_lines.append(
                f"{class_id} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}"
            )

    if yolo_lines:
        with open(label_file, "w", encoding="utf-8") as f:
            f.write("\n".join(yolo_lines))

print("✅ Convert Label Studio → YOLO DONE")
