# Computer Vision Assisted Mouse Control


A lightweight YOLOv8-based tool for real-time object detection and automated mouse positioning. 
Tracks detected objects in a screen region and smoothly centers the cursor on the largest one using relative movements.


Note: This tool is for educational and accessibility purposes. Ensure compliance with your system's usage policies.
Features


Real-Time Object Tracking: Identifies the largest object in a cropped screen region for precise cursor alignment.
Head/Object Bias Option: Optionally targets the upper portion of detected bounding boxes for focused positioning.
Relative Cursor Adjustments: Leverages Windows API for natural, sensitivity-aware mouse movements—no abrupt repositioning.
High Performance: Achieves 100-200+ FPS on mid-range hardware with optimized YOLOv8 nano model.
Simple Controls: F1 to start, F2 to stop, V to toggle assistance.
Debug Visualization: Optional overlay to visualize detections and tuning.
Built-In Model: Uses standard YOLOv8n for general 'person' or object detection—versatile and auto-downloading.

Requirements

OS: Windows 10/11 (DirectX compatible for efficient capture).

Hardware: NVIDIA GPU recommended (CUDA acceleration); CPU fallback ~60 FPS.

Python: 3.8+.
