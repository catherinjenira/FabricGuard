import torch
import cv2
import ultralytics

print("PyTorch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
print("OpenCV:", cv2.__version__)
print("Ultralytics:", ultralytics.__version__)

print("Training device: CPU")