from pathlib import Path
from ultralytics import YOLO

project_root = Path(__file__).resolve().parent.parent

model_path = project_root / "heatyolo11" / "heatyolo11" / "weights" / "best.pt"

print("待导出的模型路径：", model_path)

if not model_path.exists():
    raise FileNotFoundError(f"找不到模型文件：{model_path}")

model = YOLO(str(model_path))

export_path = model.export(
    format="onnx",
    imgsz=640,
    opset=12,
    simplify=False
)

print("\n导出完成！")
print("导出结果：", export_path)
