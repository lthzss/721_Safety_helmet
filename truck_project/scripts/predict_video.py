from pathlib import Path
import cv2
from ultralytics import YOLO

project_root = Path(__file__).resolve().parent.parent

model_path = project_root / "heatyolo11" / "heatyolo11" / "weights" / "best.pt"

video_path = project_root / "demo_videos" / "1.mp4"

output_dir = project_root / "analysis" / "video_predictions"
output_dir.mkdir(parents=True, exist_ok=True)
output_video_path = output_dir / "test1_result.mp4"

print("模型路径：", model_path)
print("输入视频：", video_path)
print("输出视频：", output_video_path)

model = YOLO(str(model_path))

cap = cv2.VideoCapture(str(video_path))
if not cap.isOpened():
    raise RuntimeError(f"无法打开视频文件：{video_path}")

fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
writer = cv2.VideoWriter(str(output_video_path), fourcc, fps, (width, height))

frame_count = 0
colors = {"hat": (0, 255, 0), "person": (255, 0, 0)}

while True:
    ret, frame = cap.read()
    if not ret:
        break

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

    cv2.putText(
        frame,
        f"frame={frame_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 0, 0),
        2
    )

    cv2.imshow("Hard Hat Detection", frame)

    writer.write(frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
writer.release()
cv2.destroyAllWindows()

print("\n视频检测完成！")
print(f"输出文件已保存到：{output_video_path}")
