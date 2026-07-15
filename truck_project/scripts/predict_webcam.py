from pathlib import Path
import cv2
from ultralytics import YOLO
from picamera2 import Picamera2
import time

project_root = Path(__file__).resolve().parent.parent

model_path = project_root / "heatyolo11" / "heatyolo11" / "weights" / "best.pt"

print("模型路径：", model_path)

model = YOLO(str(model_path))

picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

frame_count = 0
prev_time = time.time()

colors = {"hat": (0, 255, 0), "person": (255, 0, 0)}

while True:
    frame_rgba = picam2.capture_array()
    frame = cv2.cvtColor(frame_rgba, cv2.COLOR_RGBA2BGR)

    frame_count += 1

    results = model(frame, verbose=False)
    r = results[0]

    boxes = r.boxes
    if boxes is not None and len(boxes) > 0:
        for box in boxes:
            cls = int(box.cls[0])
            label = r.names[cls]
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            color = colors.get(label, (128, 128, 128))
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    current_time = time.time()
    fps = 1.0 / (current_time - prev_time) if current_time != prev_time else 0.0
    prev_time = current_time

    cv2.putText(
        frame,
        f"Frame: {frame_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 0, 0),
        2
    )

    cv2.putText(
        frame,
        f"FPS: {fps:.2f}",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 128, 255),
        2
    )

    cv2.putText(
        frame,
        "Press ESC to quit",
        (20, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    cv2.imshow("Hard Hat Detection", frame)

    key = cv2.waitKey(1)
    if key == 27:
        break

picam2.stop()
cv2.destroyAllWindows()
print("安全帽检测结束。")
