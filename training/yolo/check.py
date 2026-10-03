import torch
print("Cuda available:", torch.cuda.is_available())
print("Number of GPUs:", torch.cuda.device_count())
print("cuDNN available:", torch.backends.cudnn.is_available())
print("cuDNN verision:", torch.backends.cudnn.version())