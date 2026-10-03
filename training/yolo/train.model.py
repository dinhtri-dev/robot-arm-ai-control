"""
YOLOv11 Training Script for Vietnamese Product Detection
Optimized for 16 classes with ~32,000 total images (2000 per class)
"""
import os
from pathlib import Path

from ultralytics import YOLO
import torch
import yaml
from pathlib import Path
import os

# ===========================
# CONFIGURATION
# ===========================

class TrainingConfig:
    """Cấu hình training cho YOLOv11"""
    
    # Dataset paths (cập nhật theo đường dẫn thực tế của bạn)
    DATA_YAML = str(Path(os.environ.get("YEAR2_DATA_ROOT", str(Path(__file__).resolve().parent / "data"))) / 'Year2/KT ROBOT/DATASET_ALL/data.yaml')  # File data.yaml của bạn
    
    # Model selection - chọn model phù hợp
    # 'n' - nano: nhanh, nhẹ (2.6M params) - cho edge devices   
    # 's' - small: cân bằng tốt (9.4M params) - recommended cho bạn
    # 'm' - medium: mạnh hơn (20M params) - nếu có GPU mạnh
    # 'l' - large: rất mạnh (25M params)
    # 'x' - xlarge: mạnh nhất (57M params)
    MODEL_SIZE = 's'  # Recommended cho dataset của bạn
    
    # Training hyperparameters
    EPOCHS = 50  # Số epoch training (có early stopping)
    BATCH_SIZE = 16  # Tùy vào VRAM GPU (16GB: batch=16, 8GB: batch=8)
    IMG_SIZE = 640  # Kích thước ảnh training
    
    # Device
    DEVICE = '0'  # GPU 0, hoặc '0,1' cho multi-GPU, 'cpu' cho CPU
    
    # Workers
    WORKERS = 10  # Số workers cho dataloader
    
    # Project paths
    PROJECT_NAME = 'vietnamese_products_yolov11'
    RUN_NAME = 'yolov11s_16classes'
    
    # Advanced settings
    PATIENCE = 50  # Early stopping patience
    SAVE_PERIOD = 10  # Lưu checkpoint mỗi N epochs
    
    # Optimizer
    OPTIMIZER = 'AdamW'  # 'SGD', 'Adam', 'AdamW', 'NAdam', 'RAdam', 'RMSProp'
    LR0 = 0.001  # Initial learning rate
    LRF = 0.01  # Final learning rate (lr0 * lrf)
    MOMENTUM = 0.937  # SGD momentum/Adam beta1
    WEIGHT_DECAY = 0.0005  # Optimizer weight decay
    
    # Augmentation - tối ưu cho product detection
    AUGMENT = True
    HSEINPUT = 0.015  # HSV-Hue augmentation
    SATURATION = 0.7  # HSV-Saturation augmentation
    VALUE = 0.4  # HSV-Value augmentation
    DEGREES = 0.0  # Rotation (+/- deg)
    TRANSLATE = 0.1  # Translation (+/- fraction)
    SCALE = 0.5  # Scale (+/- gain)
    SHEAR = 0.0  # Shear (+/- deg)
    PERSPECTIVE = 0.0  # Perspective (+/- fraction)
    FLIPUD = 0.0  # Vertical flip (probability)
    FLIPLR = 0.5  # Horizontal flip (probability)
    MOSAIC = 1.0  # Mosaic augmentation (probability)
    MIXUP = 0.0  # MixUp augmentation (probability)
    COPY_PASTE = 0.0  # Copy-paste augmentation (probability)

def check_gpu():
    """Kiểm tra GPU availability"""
    if torch.cuda.is_available():
        print(f"✓ GPU Available: {torch.cuda.get_device_name(0)}")
        print(f"✓ CUDA Version: {torch.version.cuda}")
        print(f"✓ GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        return True
    else:
        print("⚠ No GPU found. Training will use CPU (slow)")
        return False

def create_training_config():
    """Tạo file hyperparameters cho training"""
    config = TrainingConfig()
    
    hyp = {
        # Learning rate
        'lr0': config.LR0,
        'lrf': config.LRF,
        'momentum': config.MOMENTUM,
        'weight_decay': config.WEIGHT_DECAY,
        
        # Warmup
        'warmup_epochs': 3.0,
        'warmup_momentum': 0.8,
        'warmup_bias_lr': 0.1,
        
        # Loss weights
        'box': 7.5,  # Box loss gain
        'cls': 0.5,  # Class loss gain
        'dfl': 1.5,  # DFL loss gain
        
        # Augmentation
        'hsv_h': config.HSEINPUT,
        'hsv_s': config.SATURATION,
        'hsv_v': config.VALUE,
        'degrees': config.DEGREES,
        'translate': config.TRANSLATE,
        'scale': config.SCALE,
        'shear': config.SHEAR,
        'perspective': config.PERSPECTIVE,
        'flipud': config.FLIPUD,
        'fliplr': config.FLIPLR,
        'mosaic': config.MOSAIC,
        'mixup': config.MIXUP,
        'copy_paste': config.COPY_PASTE,
    }
    
    return hyp

def train_yolov11():
    """Main training function"""
    
    config = TrainingConfig()
    
    print("="*70)
    print("YOLOv11 TRAINING - VIETNAMESE PRODUCTS DETECTION")
    print("="*70)
    
    # Check GPU
    has_gpu = check_gpu()
    print()
    
    # Load model
    print(f"📦 Loading YOLOv11{config.MODEL_SIZE} model...")
    
    # Sử dụng pretrained weights từ COCO
    model = YOLO(f'yolov8{config.MODEL_SIZE}.pt')
    print(f"✓ Model loaded: yolov11{config.MODEL_SIZE}.pt")
    print()
    
    # Get hyperparameters
    hyp = create_training_config()
    
    # Training configuration summary
    print("📊 TRAINING CONFIGURATION:")
    print(f"   Model: YOLOv11{config.MODEL_SIZE}")
    print(f"   Classes: 16")
    print(f"   Epochs: {config.EPOCHS}")
    print(f"   Batch Size: {config.BATCH_SIZE}")
    print(f"   Image Size: {config.IMG_SIZE}")
    print(f"   Device: {config.DEVICE}")
    print(f"   Optimizer: {config.OPTIMIZER}")
    print(f"   Initial LR: {config.LR0}")
    print(f"   Workers: {config.WORKERS}")
    print()
    
    # Train the model
    print("🚀 Starting training...")
    print("="*70)
    print()
    
    results = model.train(
        # Data
        data=config.DATA_YAML,
        
        # Training
        epochs=config.EPOCHS,
        batch=config.BATCH_SIZE,
        imgsz=config.IMG_SIZE,
        
        # Device
        device=config.DEVICE,
        workers=config.WORKERS,
        
        # Project
        project=config.PROJECT_NAME,
        name=config.RUN_NAME,
        exist_ok=True,
        
        # Optimizer
        optimizer=config.OPTIMIZER,
        
        # Callbacks
        patience=config.PATIENCE,
        save=True,
        save_period=config.SAVE_PERIOD,
        
        # Validation
        val=True,
        
        # Augmentation
        augment=config.AUGMENT,
        
        # Resume
        resume=False,
        
        # Other
        pretrained=True,
        verbose=True,
        seed=42,
        deterministic=False,
        single_cls=False,
        rect=False,
        cos_lr=True,  # Cosine learning rate scheduler
        close_mosaic=10,  # Disable mosaic for last N epochs
        
        # Apply custom hyperparameters
        **hyp
    )
    
    print()
    print("="*70)
    print("✓ TRAINING COMPLETED!")
    print("="*70)
    
    # Save best model path
    best_model = Path(config.PROJECT_NAME) / config.RUN_NAME / 'weights' / 'best.pt'
    print(f"\n📁 Best model saved at: {best_model}")
    
    return results, best_model

def validate_model(model_path, data_yaml):
    """Validate model on test set"""
    print("\n" + "="*70)
    print("VALIDATING MODEL")
    print("="*70 + "\n")
    
    model = YOLO(model_path)
    results = model.val(data=data_yaml)
    
    print(f"\n✓ Validation Results:")
    print(f"   mAP50: {results.box.map50:.4f}")
    print(f"   mAP50-95: {results.box.map:.4f}")
    print(f"   Precision: {results.box.mp:.4f}")
    print(f"   Recall: {results.box.mr:.4f}")
    
    return results

def export_model(model_path, formats=['onnx', 'torchscript']):
    """Export model to different formats"""
    print("\n" + "="*70)
    print("EXPORTING MODEL")
    print("="*70 + "\n")
    
    model = YOLO(model_path)
    
    for fmt in formats:
        print(f"Exporting to {fmt.upper()}...")
        model.export(format=fmt)
        print(f"✓ {fmt.upper()} export completed")
    
    print("\n✓ All exports completed!")

if __name__ == "__main__":
    # Kiểm tra file data.yaml tồn tại
    config = TrainingConfig()
    
    if not Path(config.DATA_YAML).exists():
        print(f"❌ Error: {config.DATA_YAML} not found!")
        print("Please make sure your data.yaml file exists with correct paths.")
        print("\nYour data.yaml should look like:")
        print("""
# Vietnamese Products Dataset
path: /path/to/DATASET_ALL  # dataset root dir
train: images/train
val: images/val

nc: 16
names:
  - chau_cay_quat_tac
  - chau_cuc_van_tho
  - fanta_chai
  - gio_qua_tet
  - ket_coca
  - khay_coca_nho
  - khay_lon_nuoc_coca
  - khay_lon_nuoc_pepsi
  - mi_hao_hao
  - mi_omachi
  - nuoc_khoang
  - pepsi_chai
  - pho_goi_xua_va_nay
  - pho_tron_de_nhat
  - sprite_chai
  - thung_mi_siukay
        """)
        exit(1)
    
    # Train model
    results, best_model = train_yolov11()
    
    # Validate
    val_results = validate_model(best_model, config.DATA_YAML)
    
    # Export (optional)
    # export_model(best_model, formats=['onnx', 'torchscript'])
    
    print("\n" + "="*70)
    print("🎉 ALL DONE!")
    print("="*70)