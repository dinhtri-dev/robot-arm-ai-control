# 🤖 Robot Control System với AI Detection

Hệ thống điều khiển robot tích hợp YOLOv8 để phát hiện đối tượng real-time từ camera.

## 🎯 Tính năng

### 1. **AI Detection (YOLOv8)**
- ✅ Phát hiện đối tượng real-time từ camera số 1
- ✅ Hiển thị bounding boxes và confidence scores
- ✅ Đếm số lượng đối tượng phát hiện được
- ✅ Bật/tắt detection theo nhu cầu

### 2. **Robot Control**
- ✅ Điều khiển 3 trục X, Y, Z bằng joystick
- ✅ Điều khiển gripper (mở/đóng)
- ✅ Điều chỉnh step size (5-50mm)
- ✅ Hiển thị vị trí real-time

### 3. **Preset Levels**
- ✅ Lưu 3 vị trí preset
- ✅ Di chuyển nhanh đến preset đã lưu

### 4. **Teach Points**
- ✅ Lưu nhiều waypoints
- ✅ Chạy theo waypoints đã lưu
- ✅ Xóa tất cả waypoints

### 5. **Order Picking**
- ✅ Danh sách 10+ sản phẩm
- ✅ Tọa độ cho từng sản phẩm
- ✅ Auto picking nhiều sản phẩm

### 6. **System Log**
- ✅ Log tất cả hoạt động
- ✅ Timestamp cho mỗi event
- ✅ Color-coded messages

## 📦 Cài đặt

### Bước 1: Cài đặt Python Dependencies
```bash
pip install -r requirements.txt
```

### Bước 2: Chuẩn bị Model
Đặt file **best.pt** (YOLOv8 model) vào cùng thư mục với `app.py`:
```
project/
├── app.py
├── best.pt          <-- Model file ở đây
├── templates/
│   └── index.html
└── requirements.txt
```

### Bước 3: Kiểm tra Camera
Đảm bảo camera được kết nối (mặc định sử dụng camera index 1):
```bash
# Kiểm tra camera có sẵn
python -c "import cv2; print(cv2.VideoCapture(1).isOpened())"
```

## 🚀 Chạy ứng dụng

### Chạy server:
```bash
python app.py
```

### Truy cập web interface:
Mở browser và truy cập:
```
http://localhost:5000
```

Hoặc từ máy khác trong cùng mạng:
```
http://<IP_ADDRESS>:5000
```

## 🎮 Hướng dẫn sử dụng

### 1. Bật AI Detection
1. Click nút **"BẬT AI DETECT"** màu xanh
2. Camera sẽ bắt đầu phát hiện đối tượng
3. Kết quả hiển thị ở góc dưới video feed
4. Click **"TẮT AI DETECT"** để dừng

### 2. Điều khiển Robot
- **XY Joystick**: Di chuyển trên mặt phẳng ngang
- **Z Joystick**: Di chuyển trục đứng
- **Step Size**: Điều chỉnh khoảng cách mỗi bước
- **Gripper**: Nút MỞ/ĐÓNG để điều khiển kẹp

### 3. Sử dụng Preset Levels
1. Nhập tọa độ X, Y, Z cho từng level
2. Click nút **"GO"** để di chuyển đến vị trí đó
3. Ba preset levels có thể dùng cho các tầng khác nhau

### 4. Teach Points
1. Di chuyển robot đến vị trí mong muốn
2. Click **"ADD"** để lưu điểm hiện tại
3. Lặp lại để lưu nhiều điểm
4. Click **"RUN"** để chạy theo các điểm đã lưu
5. Click **"CLEAR"** để xóa tất cả

### 5. Order Picking
1. Tick chọn các sản phẩm cần lấy
2. Điều chỉnh tọa độ X, Y, Z nếu cần
3. Click **"BẮT ĐẦU PICKING"**
4. Hệ thống sẽ tự động picking theo thứ tự

## 🔧 Cấu hình

### Thay đổi camera index
Trong file `app.py`, dòng 56:
```python
camera = cv2.VideoCapture(1)  # Đổi 1 thành 0, 2, 3... tùy camera
```

### Thay đổi model
Thay thế file `best.pt` bằng model YOLOv8 khác hoặc thay đổi dòng 42:
```python
model = YOLO('best.pt')  # Đổi thành tên model khác
```

### Điều chỉnh confidence threshold
Trong file `app.py`, dòng 75:
```python
results = model(frame, conf=0.5, iou=0.45)  # conf=0.5 là 50% confidence
```

### Thay đổi FPS
Trong file `app.py`, dòng 68:
```python
camera.set(cv2.CAP_PROP_FPS, 30)  # Đổi 30 thành FPS mong muốn
```

## 🐛 Xử lý lỗi thường gặp

### 1. Camera không hoạt động
```python
# Thử các camera index khác nhau
camera = cv2.VideoCapture(0)  # hoặc 1, 2, 3...
```

### 2. Model không load được
- Kiểm tra file `best.pt` có tồn tại không
- Kiểm tra định dạng file có đúng không
- Thử train lại model hoặc download model mẫu

### 3. FPS thấp
- Giảm resolution camera
- Tăng confidence threshold
- Sử dụng model nhẹ hơn (YOLOv8n thay vì YOLOv8x)

### 4. Socket disconnection
- Kiểm tra firewall
- Thử chuyển sang port khác
- Kiểm tra kết nối mạng

## 📊 Thông số hệ thống

| Component | Specification |
|-----------|--------------|
| Backend | Flask + SocketIO |
| AI Model | YOLOv8 (best.pt) |
| Camera | OpenCV VideoCapture |
| Resolution | 640x480 (default) |
| FPS | 30 (default) |
| Detection | Real-time object detection |
| Confidence | 50% (adjustable) |

## 🎨 Giao diện

- **Dark theme** với accent màu cyan/green
- **Responsive design** cho mobile/tablet
- **Real-time updates** qua WebSocket
- **Smooth animations** và transitions
- **Professional UI** với gradients và shadows

## 📝 License

MIT License - Tự do sử dụng và chỉnh sửa

## 👨‍💻 Hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra log trong terminal
2. Kiểm tra console trong browser (F12)
3. Đọc phần "Xử lý lỗi thường gặp" ở trên

---

🤖 **Made with ❤️ by Robot Control Team**
