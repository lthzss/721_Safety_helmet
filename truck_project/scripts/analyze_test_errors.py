from pathlib import Path
from ultralytics import YOLO
import shutil
import csv

# ========== 1. 项目根目录 ==========
project_root = Path(__file__).resolve().parent.parent

# ========== 2. 模型路径 ==========
model_path = project_root / "runs" / "axle_cls_baseline" / "weights" / "best.pt"

# ========== 3. test 集路径 ==========
test_root = project_root / "datasets" / "toll_axle_cls" / "test"

# ========== 4. 输出目录 ==========
output_root = project_root / "analysis" / "test_error_analysis"
wrong_dir = output_root / "wrong_predictions"
output_root.mkdir(parents=True, exist_ok=True)
wrong_dir.mkdir(parents=True, exist_ok=True)

# ========== 5. 类别列表 ==========
classes = ["non_truck", "axle2", "axle3", "axle4", "axle5"]

# ========== 6. 加载模型 ==========
model = YOLO(str(model_path))

# ========== 7. 结果保存文件 ==========
csv_path = output_root / "test_predictions.csv"

total = 0
correct = 0
wrong = 0

with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["image_name", "true_label", "pred_label", "confidence", "is_correct"])

    for true_label in classes:
        class_dir = test_root / true_label
        images = [p for p in class_dir.iterdir() if p.is_file() and p.suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]]

        for img_path in images:
            total += 1

            results = model(str(img_path), verbose=False)
            r = results[0]

            pred_idx = int(r.probs.top1)
            pred_label = r.names[pred_idx]
            conf = float(r.probs.top1conf)

            is_correct = (pred_label == true_label)

            if is_correct:
                correct += 1
            else:
                wrong += 1
                # 复制错误图片到 wrong_predictions
                # 文件名里写清楚“真实类别”和“预测类别”
                new_name = f"true-{true_label}__pred-{pred_label}__conf-{conf:.4f}__{img_path.name}"
                shutil.copy2(img_path, wrong_dir / new_name)

            writer.writerow([img_path.name, true_label, pred_label, round(conf, 4), int(is_correct)])

print("\n批量分析完成！")
print(f"总样本数：{total}")
print(f"预测正确：{correct}")
print(f"预测错误：{wrong}")
print(f"准确率：{correct / total:.4f}")
print(f"结果表保存位置：{csv_path}")
print(f"错分图片保存位置：{wrong_dir}")