# 安全帽佩戴检测系统

基于 YOLOv11 的安全帽佩戴检测系统，用于工地/厂区场景下通过 CSI 摄像头实时检测人员是否佩戴安全帽，统计安全帽佩戴情况。

## 环境要求

- **硬件**: 树莓派 5 + CSI 摄像头 (OV5647)
- **Python**: 3.13
- **依赖**: PyTorch, Ultralytics, OpenCV, Flask, Picamera2

## 项目结构

```
truck_project/
├── heatyolo11/heatyolo11/     # 安全帽检测模型
│   ├── data.yaml              # 数据集配置 (hat / person)
│   └── weights/
│       └── best.pt            # 训练好的检测模型
├── datasets/toll_axle_cls/    # 数据集 (train/val/test)
├── web_demo/
│   ├── app.py                 # Web 实时检测服务
│   └── templates/index.html   # 前端页面
├── scripts/                   # 工具脚本
│   ├── train_yolo_cls.py      # 模型训练
│   ├── eval_test.py           # 测试集评估
│   ├── predict_image.py       # 单张图片检测
│   ├── predict_video.py       # 视频文件检测
│   ├── predict_webcam.py      # 本地摄像头实时检测
│   └── export_onnx.py         # 导出 ONNX 模型
├── analysis/                  # 检测结果输出
│   ├── image_predictions/     # 图片检测结果
│   └── video_predictions/     # 视频检测结果
└── demo_videos/               # 演示视频文件
```

## 快速开始

### 1. 激活虚拟环境

```bash
cd ~/721/truck_project/truck_project
source venv/bin/activate
```

### 2. 释放摄像头资源（每次重启需执行，仅需一次）

Pipewire 桌面服务默认占用 CSI 摄像头，需先停掉释放设备：

```bash
systemctl --user stop pipewire.socket pipewire.service wireplumber.service
```

### 3. 启动 Web 实时检测服务

```bash
python web_demo/app.py
```

### 4. 浏览器访问

在任意同局域网设备打开：

```
http://<树莓派IP>:5000
```

页面包含：
- **实时视频流**：CSI 摄像头画面，叠加检测边界框和 FPS
- **信息面板**：当前检测目标、置信度、FPS、系统状态
- **今日检测统计**：柱状图展示当天 hat / person 检测数量（跨天自动清零）
- **检测日志**：实时打印 `[时间] 检测类别 (置信度)`

## 常用脚本

### 模型训练

```bash
python scripts/train_yolo_cls.py
```

### 测试集评估

```bash
python scripts/eval_test.py
```

输出 mAP 等检测指标。

### 单张图片检测

```bash
python scripts/predict_image.py
```

修改脚本中的 `image_path` 变量指向目标图片，输出带边界框的结果图到 `analysis/image_predictions/`。

### 视频文件检测

```bash
python scripts/predict_video.py
```

输入 `demo_videos/1.mp4`，输出带标注的结果视频到 `analysis/video_predictions/`。

### 本地摄像头实时检测（需显示器）

```bash
DISPLAY=:0 python scripts/predict_webcam.py
```

按 ESC 退出。

### 导出 ONNX 模型

```bash
python scripts/export_onnx.py
```

## 检测类别

| 类别 | 含义 |
|------|------|
| hat | 已佩戴安全帽 |
| person | 未佩戴安全帽（人） |

## API 接口

| 路由 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 首页 |
| `/video_feed` | GET | MJPEG 视频流 |
| `/result` | GET | 当前检测结果 (JSON) |
| `/stats` | GET | 今日检测统计 (JSON) |
| `/logs` | GET | 检测日志 (JSON) |

## 常见问题

**Q: 启动报 `Camera __init__ sequence did not complete`**
A: 摄像头被占用，执行步骤 2 释放设备。

**Q: 网页图片显示不全**
A: 确保浏览器窗口足够宽，图片按 4:3 比例自适应显示。

**Q: `ModuleNotFoundError: No module named 'ultralytics'`**
A: 用的系统 Python，需要用 `venv/bin/python` 或先 `source venv/bin/activate`。
