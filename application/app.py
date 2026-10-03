from pathlib import Path
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Robot Control System with AI Detection - FIXED VERSION
Version 2.0 - Stable & Production Ready
"""

from flask import Flask, Response, render_template_string
from flask_socketio import SocketIO, emit
import cv2
from ultralytics import YOLO
import numpy as np
import threading
import time
from datetime import datetime

# ============================================
# 🔧 FLASK APP CONFIGURATION
# ============================================
from archive_guard import install, guarded, secure_connect, ORIGINS
app = Flask(__name__)
install(app)
socketio = SocketIO(app, cors_allowed_origins=ORIGINS, max_http_buffer_size=1024*1024, async_mode='threading')

# ============================================
# 🤖 ROBOT STATE VARIABLES
# ============================================
robot_position = {'x': 0, 'y': 0, 'z': 0}
waypoints = []
is_picking = False

# ============================================
# 📹 AI DETECTION VARIABLES
# ============================================
camera = None
model = None
latest_frame = None
detection_results = []
is_detecting = False
frame_lock = threading.Lock()
camera_ready = False

# ============================================
# 🚀 INITIALIZE YOLO MODEL
# ============================================
def init_model():
    """Khởi tạo YOLO model từ file best.pt"""
    global model
    try:
        print("   Loading model file...")
        model = YOLO(str(Path(__file__).resolve().parent / 'models' / 'best.pt'))
        print(f"   ✅ Model loaded: {len(model.names)} classes")
        return True
    except Exception as e:
        print(f"   ❌ Model error: {e}")
        print("   ⚠️ AI Detection will be disabled")
        return False

# ============================================
# 📹 CAMERA INITIALIZATION
# ============================================
def init_camera():
    """Khởi tạo camera"""
    global camera, camera_ready
    
    # Thử các camera index
    for cam_id in [1, 0, 2]:
        try:
            print(f"   Trying camera {cam_id}...")
            cam = cv2.VideoCapture(cam_id)
            
            if cam.isOpened():
                # Test đọc frame
                ret, frame = cam.read()
                if ret and frame is not None:
                    camera = cam
                    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    camera.set(cv2.CAP_PROP_FPS, 30)
                    
                    print(f"   ✅ Camera {cam_id} OK")
                    print(f"   Resolution: {int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
                    camera_ready = True
                    return True
                else:
                    cam.release()
            else:
                cam.release()
        except Exception as e:
            print(f"   ⚠️ Camera {cam_id} failed: {e}")
            continue
    
    print("   ❌ No camera available")
    return False

# ============================================
# 🎯 AI DETECTION FUNCTION
# ============================================
def detect_objects(frame):
    """Thực hiện detection trên frame"""
    global detection_results
    
    if model is None:
        return frame, []
    
    try:
        results = model(frame, conf=0.5, iou=0.45, verbose=False)
        annotated_frame = results[0].plot()
        
        detections = []
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            
            detections.append({
                'class_id': cls_id,
                'class_name': model.names[cls_id],
                'confidence': round(conf * 100, 1)
            })
        
        detection_results = detections
        return annotated_frame, detections
        
    except Exception as e:
        return frame, []

# ============================================
# 🎥 VIDEO STREAMING THREAD
# ============================================
def video_stream():
    """Thread để stream video với AI detection"""
    global latest_frame, is_detecting, camera_ready
    
    print("   🎬 Video streaming started")
    
    # Chờ camera sẵn sàng
    wait_time = 0
    while not camera_ready and wait_time < 10:
        time.sleep(0.5)
        wait_time += 0.5
    
    if not camera_ready:
        print("   ❌ Camera not ready, using placeholder")
    
    frame_count = 0
    
    while True:
        try:
            if camera is not None and camera.isOpened() and camera_ready:
                ret, frame = camera.read()
                
                if ret and frame is not None:
                    frame_count += 1
                    
                    # AI Detection
                    if is_detecting and model is not None:
                        frame, detections = detect_objects(frame)
                        
                        # Chỉ emit detection mỗi 10 frames để tránh spam
                        if detections and frame_count % 10 == 0:
                            try:
                                socketio.emit('detection_update', {
                                    'count': len(detections),
                                    'objects': detections,
                                    'timestamp': datetime.now().strftime('%H:%M:%S')
                                })
                            except:
                                pass
                    
                    # Encode frame
                    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    
                    if ret:
                        with frame_lock:
                            latest_frame = buffer.tobytes()
                else:
                    time.sleep(0.1)
            else:
                # Tạo placeholder frame
                if latest_frame is None:
                    placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(placeholder, 'Camera Initializing...', (140, 240), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    _, buffer = cv2.imencode('.jpg', placeholder)
                    with frame_lock:
                        latest_frame = buffer.tobytes()
                
                time.sleep(0.5)
        
        except Exception as e:
            print(f"   ⚠️ Stream error: {e}")
            time.sleep(0.5)
        
        time.sleep(0.033)  # ~30 FPS

# ============================================
# 📡 VIDEO FEED GENERATOR
# ============================================
def generate_frames():
    """Generator cho video stream"""
    global latest_frame
    
    # Placeholder ban đầu
    placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(placeholder, 'Loading Camera...', (160, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    _, buffer = cv2.imencode('.jpg', placeholder)
    placeholder_bytes = buffer.tobytes()
    
    while True:
        try:
            with frame_lock:
                if latest_frame is not None:
                    frame_data = latest_frame
                else:
                    frame_data = placeholder_bytes
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
            
            time.sleep(0.033)  # ~30 FPS
        
        except GeneratorExit:
            break
        except Exception as e:
            print(f"Generator error: {e}")
            time.sleep(0.1)

# ============================================
# 🌐 HTML TEMPLATE (INLINE)
# ============================================
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Robot Control + AI Detection</title>
    <script src="https://cdn.socket.io/4.8.3/socket.io.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root { 
            --bg: #0a0e27; --panel: #1a1f3a; --border: #2d3458;
            --text: #e8eaf6; --text-secondary: #9fa8da;
            --accent: #00e5ff; --success: #00ff88; --danger: #ff1744;
            --ai-glow: rgba(0, 229, 255, 0.3);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            padding: 20px; min-height: 100vh;
        }
        .header { text-align: center; margin-bottom: 25px; }
        .header h1 {
            font-size: 32px; font-weight: 800;
            background: linear-gradient(135deg, var(--accent) 0%, var(--success) 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            display: flex; align-items: center; justify-content: center; gap: 12px;
        }
        .container { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
            gap: 20px; max-width: 1800px; margin: 0 auto;
        }
        .panel { 
            background: var(--panel); border-radius: 20px; padding: 24px;
            border: 1px solid var(--border); box-shadow: 0 8px 32px rgba(0,0,0,0.5);
        }
        .panel-header {
            display: flex; align-items: center; gap: 10px;
            margin-bottom: 20px; padding-bottom: 12px;
            border-bottom: 2px solid var(--border);
        }
        .panel-header i { color: var(--accent); font-size: 22px; }
        .panel-header h3 {
            font-size: 16px; font-weight: 700;
            text-transform: uppercase; letter-spacing: 1px;
        }
        .ai-controls { display: flex; gap: 12px; margin-bottom: 16px; }
        .btn-ai {
            flex: 1; padding: 12px 20px; border: none;
            border-radius: 12px; font-size: 14px; font-weight: 600;
            cursor: pointer; display: flex; align-items: center;
            justify-content: center; gap: 8px; transition: all 0.3s;
        }
        .btn-ai-start {
            background: linear-gradient(135deg, var(--success) 0%, #00c853 100%);
            color: white;
        }
        .btn-ai-stop {
            background: linear-gradient(135deg, var(--danger) 0%, #d50000 100%);
            color: white;
        }
        .btn-ai:hover { transform: translateY(-2px); }
        .camera-box {
            background: #000; border-radius: 16px; overflow: hidden;
            position: relative; aspect-ratio: 4/3;
            border: 2px solid var(--border);
            box-shadow: 0 0 30px var(--ai-glow);
        }
        .camera-feed { width: 100%; height: 100%; object-fit: contain; }
        .cam-overlay {
            position: absolute; top: 16px; right: 16px;
            background: rgba(255, 23, 68, 0.95); color: white;
            padding: 8px 16px; border-radius: 24px;
            font-size: 12px; font-weight: 700;
            display: flex; align-items: center; gap: 8px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
        .detection-overlay {
            position: absolute; bottom: 0; left: 0; right: 0;
            background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, transparent 100%);
            padding: 16px; color: white;
        }
        .count-badge {
            background: var(--accent); color: var(--bg);
            padding: 4px 12px; border-radius: 12px;
            font-weight: 800; font-size: 16px;
        }
        .detection-list {
            display: flex; flex-wrap: wrap; gap: 8px;
            max-height: 80px; overflow-y: auto; margin-top: 8px;
        }
        .detection-item {
            background: rgba(0, 229, 255, 0.2);
            border: 1px solid var(--accent);
            padding: 4px 10px; border-radius: 8px; font-size: 11px;
        }
        .position-display {
            display: flex; justify-content: space-around;
            background: var(--bg); padding: 20px;
            border-radius: 16px; margin-bottom: 20px;
        }
        .pos-value {
            font-size: 28px; font-weight: 800;
            background: linear-gradient(135deg, var(--accent) 0%, var(--success) 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            font-family: 'Courier New', monospace;
        }
        .controller-area {
            display: flex; justify-content: space-around;
            align-items: center; gap: 20px; margin-bottom: 20px;
        }
        .joystick {
            display: grid;
            grid-template: 
                ". up ." auto
                "left home right" auto
                ". down ." auto / 1fr 1fr 1fr;
            gap: 8px;
        }
        .joy-btn {
            width: 70px; height: 70px;
            border: 2px solid var(--border);
            background: var(--panel); border-radius: 12px;
            cursor: pointer; display: flex;
            align-items: center; justify-content: center;
            font-size: 24px; color: var(--accent);
            transition: all 0.2s;
        }
        .joy-btn:hover {
            background: var(--accent); color: var(--bg);
            transform: scale(1.05);
        }
        .joy-btn.home {
            background: var(--border); cursor: default;
            font-size: 16px; font-weight: 700;
        }
        .joy-btn.home:hover { background: var(--border); transform: none; }
        .gripper-controls { display: flex; flex-direction: column; gap: 10px; }
        .grip-btn {
            padding: 16px 24px; border: none; border-radius: 12px;
            font-size: 14px; font-weight: 600; cursor: pointer;
            transition: all 0.3s;
        }
        .grip-open { background: linear-gradient(135deg, var(--success) 0%, #00c853 100%); color: white; }
        .grip-close { background: linear-gradient(135deg, #ffab00 0%, #ff8f00 100%); color: white; }
        .grip-btn:hover { transform: translateY(-2px); }
        .status-log {
            background: var(--bg); border-radius: 12px;
            padding: 16px; max-height: 300px; overflow-y: auto;
            font-family: 'Courier New', monospace; font-size: 12px;
        }
        .log-time { color: var(--text-secondary); font-weight: 600; }
        .log-success { color: var(--success); }
        .log-error { color: var(--danger); }
        @media (max-width: 768px) {
            .container { grid-template-columns: 1fr; }
            .joy-btn { width: 60px; height: 60px; font-size: 20px; }
        }
    </style>
</head>
<body>

<div class="header">
    <h1><i class="fas fa-robot"></i> ROBOT CONTROL + AI DETECTION</h1>
    <p style="color: var(--text-secondary); font-size: 14px;">⚡ Real-time Object Detection with YOLOv8</p>
</div>

<div class="container">
    <!-- Camera Panel -->
    <div class="panel">
        <div class="panel-header">
            <i class="fas fa-video"></i>
            <h3>Camera + AI Detection</h3>
        </div>
        <div class="ai-controls">
            <button class="btn-ai btn-ai-start" onclick="startDetection()">
                <i class="fas fa-play"></i> BẬT AI DETECT
            </button>
            <button class="btn-ai btn-ai-stop" onclick="stopDetection()">
                <i class="fas fa-stop"></i> TẮT AI DETECT
            </button>
        </div>
        <div class="camera-box">
            <img class="camera-feed" src="/video_feed" alt="Camera Feed">
            <div class="cam-overlay">
                <i class="fas fa-circle"></i> LIVE
            </div>
            <div class="detection-overlay" id="detection-info" style="display: none;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span>Phát hiện:</span>
                    <span class="count-badge" id="object-count">0</span>
                    <span>đối tượng</span>
                </div>
                <div class="detection-list" id="detection-list"></div>
            </div>
        </div>
    </div>

    <!-- Control Panel -->
    <div class="panel">
        <div class="panel-header">
            <i class="fas fa-gamepad"></i>
            <h3>Robot Control</h3>
        </div>
        <div class="position-display">
            <div style="text-align: center;">
                <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 8px;">X-AXIS</div>
                <div class="pos-value" id="cur-x">0</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 8px;">Y-AXIS</div>
                <div class="pos-value" id="cur-y">0</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 8px;">Z-AXIS</div>
                <div class="pos-value" id="cur-z">0</div>
            </div>
        </div>
        <div class="controller-area">
            <div class="joystick">
                <div class="joy-btn" style="grid-area: up" onclick="move('Y', 1)">
                    <i class="fas fa-arrow-up"></i>
                </div>
                <div class="joy-btn" style="grid-area: left" onclick="move('X', -1)">
                    <i class="fas fa-arrow-left"></i>
                </div>
                <div class="joy-btn home" style="grid-area: home">XY</div>
                <div class="joy-btn" style="grid-area: right" onclick="move('X', 1)">
                    <i class="fas fa-arrow-right"></i>
                </div>
                <div class="joy-btn" style="grid-area: down" onclick="move('Y', -1)">
                    <i class="fas fa-arrow-down"></i>
                </div>
            </div>
            <div class="joystick">
                <div class="joy-btn" style="grid-area: up" onclick="move('Z', 1)">
                    <i class="fas fa-arrow-up"></i>
                </div>
                <div class="joy-btn home" style="grid-area: home">Z</div>
                <div class="joy-btn" style="grid-area: down" onclick="move('Z', -1)">
                    <i class="fas fa-arrow-down"></i>
                </div>
            </div>
            <div class="gripper-controls">
                <button class="grip-btn grip-open" onclick="grip('open')">
                    <i class="fas fa-hand-paper"></i> MỞ
                </button>
                <button class="grip-btn grip-close" onclick="grip('close')">
                    <i class="fas fa-hand-rock"></i> ĐÓNG
                </button>
            </div>
        </div>
    </div>

    <!-- Status Log -->
    <div class="panel">
        <div class="panel-header">
            <i class="fas fa-terminal"></i>
            <h3>System Log</h3>
        </div>
        <div class="status-log" id="log"></div>
    </div>
</div>

<script>
    function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
var socket = io({auth: {token: window.YEAR2_ARCHIVE_TOKEN}});
    var stepVal = 10;

    socket.on('connect', function() {
        console.log('✅ Connected to server');
    });

    function startDetection() {
        socket.emit('start_detection');
        document.getElementById('detection-info').style.display = 'block';
    }

    function stopDetection() {
        socket.emit('stop_detection');
        document.getElementById('detection-info').style.display = 'none';
    }

    socket.on('detection_update', function(data) {
        document.getElementById('object-count').innerText = data.count;
        var list = document.getElementById('detection-list');
        list.innerHTML = '';
        data.objects.forEach(obj => {
            list.innerHTML += `
                <div class="detection-item">
                    <i class="fas fa-cube"></i>
                    ${escapeHtml(obj.class_name)} (${escapeHtml(obj.confidence)}%)
                </div>
            `;
        });
    });

    function move(axis, dir) {
        socket.emit('control_command', { axis: axis, val: dir * stepVal });
    }

    function grip(state) {
        socket.emit('gripper_command', { state: state });
    }

    socket.on('update_pos', function(pos) {
        document.getElementById('cur-x').innerText = pos.x;
        document.getElementById('cur-y').innerText = pos.y;
        document.getElementById('cur-z').innerText = pos.z;
    });

    socket.on('status', function(msg) {
        var log = document.getElementById('log');
        var time = new Date().toLocaleTimeString('vi', { hour12: false });
        var logClass = 'log-info';
        if (msg.msg.includes('✅')) logClass = 'log-success';
        if (msg.msg.includes('❌')) logClass = 'log-error';
        log.innerHTML += `<div><span class="log-time">[${escapeHtml(time)}]</span> <span class="${escapeHtml(logClass)}">${escapeHtml(msg.msg)}</span></div>`;
        log.scrollTop = log.scrollHeight;
    });
</script>

</body>
</html>'''

# ============================================
# 🌐 FLASK ROUTES
# ============================================
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

# ============================================
# 🔌 SOCKET.IO EVENTS
# ============================================
@socketio.on('connect')
def handle_connect():
    print(f"✅ Client connected: {datetime.now().strftime('%H:%M:%S')}")
    emit('status', {'msg': '✅ Kết nối thành công!'})
    emit('update_pos', robot_position)

@socketio.on('disconnect')
def handle_disconnect():
    print(f"❌ Client disconnected")

@socketio.on('start_detection')
@guarded('start_detection')
def handle_start_detection():
    global is_detecting
    is_detecting = True
    emit('status', {'msg': '🎯 Bật AI Detection'})

@socketio.on('stop_detection')
@guarded('stop_detection')
def handle_stop_detection():
    global is_detecting
    is_detecting = False
    emit('status', {'msg': '⏸️ Tắt AI Detection'})

@socketio.on('control_command')
@guarded('control_command')
def handle_control(data):
    axis = data.get('axis', '')
    val = data.get('val', 0)
    
    if axis == 'X':
        robot_position['x'] += val
    elif axis == 'Y':
        robot_position['y'] += val
    elif axis == 'Z':
        robot_position['z'] += val
    
    emit('update_pos', robot_position, broadcast=True)
    emit('status', {'msg': f'🎮 {axis}: {val:+d}mm'})

@socketio.on('gripper_command')
@guarded('gripper_command')
def handle_gripper(data):
    state = data.get('state', '')
    msg = '✊ Gripper đóng' if state == 'close' else '🤚 Gripper mở'
    emit('status', {'msg': msg})

# ============================================
# 🚀 MAIN EXECUTION
# ============================================
secure_connect(socketio, handle_connect)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🤖 ROBOT CONTROL + AI DETECTION SYSTEM v2.0")
    print("="*60)
    
    print("\n📦 Step 1: Loading YOLO Model...")
    model_loaded = init_model()
    
    print("\n📹 Step 2: Initializing Camera...")
    camera_loaded = init_camera()
    
    if camera_loaded:
        print("\n🎥 Step 3: Starting Video Stream...")
        video_thread = threading.Thread(target=video_stream, daemon=True)
        video_thread.start()
        time.sleep(1)  # Đợi thread khởi động
    
    print("\n🌐 Step 4: Starting Web Server...")
    print("   📍 Local:  http://localhost:5000")
    print("   📍 Network: http://127.0.0.1:5000")
    print("="*60)
    print("\n✅ System Ready! Open browser and navigate to:")
    print("   👉 http://localhost:5000")
    print("\n⏹️  Press Ctrl+C to stop\n")
    
    try:
        socketio.run(app, host='127.0.0.1', port=5000, debug=False, 
                    allow_unsafe_werkzeug=True, log_output=False)
    except KeyboardInterrupt:
        print("\n\n⏹️ Shutting down gracefully...")
        if camera is not None:
            camera.release()
        print("✅ Goodbye!\n")