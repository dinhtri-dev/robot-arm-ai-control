import os
import random
import shutil

IMG_DIR = "images"
LBL_DIR = "labels"

TRAIN_RATIO = 0.8

train_img_dir = "images/train"
val_img_dir   = "images/val"
train_lbl_dir = "labels/train"
val_lbl_dir   = "labels/val"

for d in [train_img_dir, val_img_dir, train_lbl_dir, val_lbl_dir]:
    os.makedirs(d, exist_ok=True)

images = [
    f for f in os.listdir(IMG_DIR)
    if f.lower().endswith((".jpg", ".jpeg", ".png"))
]

print(f"📸 Tổng ảnh tìm thấy: {len(images)}")
print("Ví dụ 5 ảnh đầu:", images[:5])

random.shuffle(images)
split_idx = int(len(images) * TRAIN_RATIO)

train_imgs = images[:split_idx]
val_imgs = images[split_idx:]

def move(img_list, img_dst, lbl_dst):
    for img in img_list:
        shutil.move(
            os.path.join(IMG_DIR, img),
            os.path.join(img_dst, img)
        )

        lbl = os.path.splitext(img)[0] + ".txt"
        lbl_path = os.path.join(LBL_DIR, lbl)

        if os.path.exists(lbl_path):
            shutil.move(lbl_path, os.path.join(lbl_dst, lbl))
        else:
            print(f"[WARN] Không có label cho ảnh: {img}")

move(train_imgs, train_img_dir, train_lbl_dir)
move(val_imgs, val_img_dir, val_lbl_dir)

print("✅ Split train/val DONE")
