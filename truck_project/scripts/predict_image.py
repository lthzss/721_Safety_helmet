from pathlib import Path
import cv2
from ultralytics import YOLO

project_root = Path(__file__).resolve().parent.parent

model_path = project_root / "heatyolo11" / "heatyolo11" / "weights" / "best.pt"

image_path = project_root / "datasets" / "toll_axle_cls" / "else" / "0006.jpg"

print("模型路径：", model_path)
print("测试图片：", image_path)

model = YOLO(str(model_path))

results = model(str(image_path), verbose=False)

r = results[0]

boxes = r.boxes
if boxes is not None and len(boxes) > 0:
    print("\n检测完成！检测到以下目标：")
    for i, box in enumerate(boxes):
        cls = int(box.cls[0])
        label = r.names[cls]
        conf = float(box.conf[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        print(f"  {i+1}. {label}  置信度: {conf:.4f}  位置: ({x1},{y1})-({x2},{y2})")

    img = cv2.imread(str(image_path))
    colors = {"hat": (0, 255, 0), "person": (255, 0, 0)}
    for box in boxes:
        cls = int(box.cls[0])
        label = r.names[cls]
        conf = float(box.conf[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        color = colors.get(label, (128, 128, 128))
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        cv2.putText(img, f"{label} {conf:.2f}", (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    output_path = project_root / "analysis" / "image_predictions" / "result.jpg"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), img)
    print(f"\n结果图片已保存到：{output_path}")
else:
    print("\n未检测到任何目标。")
