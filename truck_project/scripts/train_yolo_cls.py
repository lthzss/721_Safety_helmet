from pathlib import Path
from ultralytics import YOLO
import torch

# ========== 1. 项目根目录 ==========
project_root = Path(__file__).resolve().parent.parent

# ========== 2. 数据集路径 ==========
data_dir = project_root / "datasets" / "toll_axle_cls"

# ========== 3. 自动选择设备 ==========
device = 0 if torch.cuda.is_available() else "cpu"

print("项目根目录：", project_root)
print("数据集路径：", data_dir)
print("训练设备：", device)

# ========== 4. 加载预训练分类模型 ==========
# 这里用最轻量的分类模型，先跑通 baseline
model = YOLO("yolov8n-cls.pt")

# ========== 5. 开始训练 ==========
results = model.train(
    data=str(data_dir),          # 分类数据集根目录
    epochs=50,                   # 先训练50轮
    imgsz=224,                   # 分类任务常用 224
    batch=16,                    # 如果显存不够，后面可以改小
    device=device,               # 自动用 GPU 或 CPU
    workers=4,                   # 数据加载线程
    project=str(project_root / "runs"),
    name="axle_cls_baseline",
    pretrained=True,
    verbose=True
)

print("训练完成！")

# ========== 6. 验证 ==========
metrics = model.val(data=str(data_dir), split="val", device=device)
print("验证完成！")
print("top1 =", metrics.top1)
print("top5 =", metrics.top5)