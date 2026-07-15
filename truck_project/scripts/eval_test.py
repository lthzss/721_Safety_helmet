from pathlib import Path
from ultralytics import YOLO
import torch

# ========== 1. 项目根目录 ==========
project_root = Path(__file__).resolve().parent.parent

# ========== 2. 数据集路径 ==========
data_dir = project_root / "datasets" / "toll_axle_cls"

# ========== 3. 模型路径 ==========
model_path = project_root / "runs" / "axle_cls_baseline" / "weights" / "best.pt"

# ========== 4. 自动选择设备 ==========
device = 0 if torch.cuda.is_available() else "cpu"

print("项目根目录：", project_root)
print("数据集路径：", data_dir)
print("模型路径：", model_path)
print("测试设备：", device)

# ========== 5. 加载模型 ==========
model = YOLO(str(model_path))

# ========== 6. 在 test 集上评估 ==========
metrics = model.val(
    data=str(data_dir),
    split="test",
    imgsz=224,
    batch=16,
    device=device,
    project=str(project_root / "runs"),
    name="axle_cls_test_eval"
)

print("\n测试完成！")
print("top1 =", metrics.top1)
print("top5 =", metrics.top5)