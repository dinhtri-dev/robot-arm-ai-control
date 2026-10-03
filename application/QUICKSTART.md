# 🚀 QUICK START GUIDE

## Chạy ngay trong 3 bước:

### Windows:
```bash
1. Đặt file best.pt vào cùng thư mục với app.py
2. Double click file: run.bat
3. Mở browser: http://localhost:5000
```

### Linux/Mac:
```bash
1. Đặt file best.pt vào cùng thư mục với app.py
2. Chạy: ./run.sh
3. Mở browser: http://localhost:5000
```

### Manual:
```bash
1. pip install -r requirements.txt
2. python app.py
3. Mở browser: http://localhost:5000
```

## ⚠️ Quan trọng:
- Đảm bảo file **best.pt** (YOLOv8 model) nằm cùng thư mục với app.py
- Camera phải được kết nối (mặc định dùng camera index 1)
- Python 3.8+ phải được cài đặt

## 🎯 Các nút chính:

| Nút | Chức năng |
|-----|-----------|
| BẬT AI DETECT | Bật phát hiện đối tượng |
| TẮT AI DETECT | Tắt phát hiện đối tượng |
| Joystick XY | Di chuyển mặt phẳng ngang |
| Joystick Z | Di chuyển trục đứng |
| MỞ/ĐÓNG | Điều khiển gripper |
| ADD | Lưu waypoint |
| RUN | Chạy waypoints |
| BẮT ĐẦU PICKING | Bắt đầu auto picking |

## 🎥 Camera Settings:
- Mặc định dùng camera index **1**
- Nếu không hoạt động, sửa trong app.py dòng 56:
  ```python
  camera = cv2.VideoCapture(0)  # Thử 0, 2, 3...
  ```

## 📱 Truy cập từ thiết bị khác:
```
http://<IP_của_máy_chủ>:5000
```
Ví dụ: http://192.168.1.100:5000

---
Đã xong! Enjoy! 🎉
