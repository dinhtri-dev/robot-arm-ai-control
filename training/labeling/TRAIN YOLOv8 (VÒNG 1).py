import os
from pathlib import Path
from ultralytics import YOLO

if __name__ == "__main__":
    model = YOLO("yolov8n.pt")

    model.train(
        data=str(Path(os.environ.get("YEAR2_DATA_ROOT", str(Path(__file__).resolve().parent / "data"))) / 'Year2/kĩ thuật robot/DATA/ky thuat robot.v1i.yolov8/data.yaml'),
        epochs=50,
        imgsz=640,
        batch=16,
        name="Thung_pho_tron_de_nhat",
        workers=0      # 👈 thêm dòng này cho chắc
    )
 