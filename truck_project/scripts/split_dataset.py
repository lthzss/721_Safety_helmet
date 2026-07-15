import random
import shutil
from pathlib import Path

# ========== 1. 固定随机种子，保证每次划分结果一致 ==========
random.seed(42)

# ========== 2. 路径设置 ==========
# 当前脚本位置：truck_axle_project/scripts/split_dataset.py
# project_root 就是 truck_axle_project
project_root = Path(__file__).resolve().parent.parent

src_root = project_root / "raw_data"
dst_root = project_root / "datasets" / "toll_axle_cls"

# ========== 3. 类别名称 ==========
# 这里必须和 raw_data 里的文件夹名字完全一致
classes = ["non_truck", "axle2", "axle3", "axle4", "axle5"]

# ========== 4. 划分比例 ==========
train_ratio = 0.7
val_ratio = 0.15
test_ratio = 0.15

assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "比例加起来必须等于 1"

# ========== 5. 支持的图片格式 ==========
valid_suffixes = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# ========== 6. 创建目标目录 ==========
for split in ["train", "val", "test"]:
    for cls in classes:
        (dst_root / split / cls).mkdir(parents=True, exist_ok=True)

# ========== 7. 开始划分 ==========
for cls in classes:
    class_dir = src_root / cls

    if not class_dir.exists():
        raise FileNotFoundError(f"找不到类别文件夹：{class_dir}")

    images = [p for p in class_dir.iterdir() if p.is_file() and p.suffix.lower() in valid_suffixes]

    if len(images) == 0:
        raise ValueError(f"类别 {cls} 文件夹里没有找到图片")

    random.shuffle(images)

    n = len(images)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)
    n_test = n - n_train - n_val

    train_imgs = images[:n_train]
    val_imgs = images[n_train:n_train + n_val]
    test_imgs = images[n_train + n_val:]

    for img in train_imgs:
        shutil.copy2(img, dst_root / "train" / cls / img.name)

    for img in val_imgs:
        shutil.copy2(img, dst_root / "val" / cls / img.name)

    for img in test_imgs:
        shutil.copy2(img, dst_root / "test" / cls / img.name)

    print(f"[{cls}] 总数={n}, train={len(train_imgs)}, val={len(val_imgs)}, test={len(test_imgs)}")

print("\n数据集划分完成！")
print(f"输出位置：{dst_root}")