# ================================================
# OPPENSTEINER V3.5 – OW2 INSTANT HARLOCK (Generic)
# Biggest person → Instant relative snap to HEAD (respects sens)
# No special model: Uses yolov8n.pt (person class) + head bias
# ================================================

import os
import time
import keyboard
import numpy as np
import cv2
import win32api
import win32con

import dxcam
from ultralytics import YOLO

# Load generic model (auto-downloads ~6MB)
print("Loading YOLOv8n (person detection for OW2 heroes)...")
model = YOLO("yolov8n.pt")
print("MODEL LOADED – PERSON + HEAD BIAS MODE")

# ==================== CONFIG (Tweak Here) ====================
running = False
aim_enabled = True  # Start with aim ON
debugging = False  # True = draw boxes (hurts FPS) | False = pure aim

# ────── QUICK TWEAKS ──────
CONFIDENCE = 0.4     # 0.3=more locks (false positives), 0.5=fewer but sure
HEAD_BIAS = True     # True = aim head (top 30% bbox) | False = center torso
HARD_SNAP = True     # True = instant lock | False = light smooth (0.3 alpha)
REGION_SIZE = 512    # Crop px (512=fast, 800=wide view, lower FPS)
TARGET_FPS = 144     # Capture rate (144=constant, 60=conservative)
MIN_AREA = 200       # Ignore tiny detections
# ─────────────────────────

print("\n" + "="*50)
print("    OPPENSTEINER V3.5 – OW2 HEAD HARLOCK (GENERIC)")
print("="*50)
print("F1 → Start | F2 → Stop | V → Toggle Aim")
print("Fixed: Relative snaps | Constant 100+ FPS locks | Head bias ON")
print("Ready – Press F1 in OW2!\n")

camera = dxcam.create()
left, top = 0, 0  # Global offsets

# ==================== MAIN LOOP ====================
while True:
    # START
    if keyboard.is_pressed("f1") and not running:
        # Get screen dims (full primary)
        screen_w = camera.width
        screen_h = camera.height
        cx, cy = screen_w // 2, screen_h // 2
        half = REGION_SIZE // 2
        left = cx - half
        top = cy - half
        region = (left, top, left + REGION_SIZE, top + REGION_SIZE)
        camera.start(target_fps=TARGET_FPS, region=region)
        running = True
        print("BOT STARTED – HARLOCK MODE")

    # STOP
    if keyboard.is_pressed("f2") and running:
        camera.stop()
        running = False
        print("BOT STOPPED")

    # TOGGLE AIM
    if keyboard.is_pressed("v"):
        aim_enabled = not aim_enabled
        print(f"AIM {'ON' if aim_enabled else 'OFF'}")
        time.sleep(0.3)

    if not running:
        time.sleep(0.1)
        continue

    frame = camera.get_latest_frame()
    if frame is None:
        continue

    start = time.perf_counter()

    # Inference (person only, no show for speed)
    results = model.predict(
        frame, conf=CONFIDENCE, classes=[0], verbose=False, show=False
    )[0]

    # Find BIGGEST target (simple + fast)
    largest_area = 0
    largest_box = None
    try:
        if results.boxes is not None:
            for box in results.boxes.xyxy:
                x1, y1, x2, y2 = box
                area = (x2 - x1) * (y2 - y1)
                if area > largest_area:
                    largest_area = area
                    largest_box = (x1, y1, x2, y2)
    except:
        pass

    if largest_box and aim_enabled and largest_area > MIN_AREA:
        x1, y1, x2, y2 = largest_box
        if HEAD_BIAS:
            target_y = y1 + 0.3 * (y2 - y1)  # Head bias (top 30%)
        else:
            target_y = (y1 + y2) / 2
        target_x = (x1 + x2) / 2

        # Relative snap (no pull-away, respects sens)
        screen_target_x = left + target_x
        screen_target_y = top + target_y
        cur_x, cur_y = win32api.GetCursorPos()
        rel_dx = int(screen_target_x - cur_x)
        rel_dy = int(screen_target_y - cur_y)

        if HARD_SNAP:
            # Instant hard lock
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, rel_dx, rel_dy, 0, 0)
        else:
            # Light smooth
            rel_dx = int(rel_dx * 0.3)
            rel_dy = int(rel_dy * 0.3)
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, rel_dx, rel_dy, 0, 0)

        print(f"LOCK: {screen_target_x:.0f},{screen_target_y:.0f} (area:{largest_area:.0f})")

        # Debug draw
        if debugging:
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
            cv2.circle(frame, (int(target_x), int(target_y)), 5, (0, 255, 0), -1)
            cv2.imshow("Debug", frame)
            cv2.waitKey(1)

    else:
        print("NO TARGET")

    # FPS (constant now)
    took = time.perf_counter() - start
    fps = 1 / took
    print(f"FPS: {fps:.0f} | Time: {took*1000:.0f}ms | Aim: {'ON' if aim_enabled else 'OFF'}", end='\r')

camera.stop()
cv2.destroyAllWindows()
print("\nShutdown.")