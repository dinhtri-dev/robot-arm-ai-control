from ultralytics import YOLO

model = YOLO("runs/detect/mi_siu_kay_v1/weights/best.pt")

results = model.predict(
    source="new_images",
    conf=0.3,     # có thể chỉnh 0.25–0.4
    save=False
)

print("✅ Predict xong")
