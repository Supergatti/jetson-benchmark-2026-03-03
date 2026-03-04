# Jetson 代码智能体 — Copilot 自定义指令

## 角色定位

你是专为本 NVIDIA Jetson 设备仓库设计的代码智能体。回答问题时优先结合以下设备上下文，帮助用户进行推理验证、摄像头调试、模型部署、ROS2 集成以及系统性能调优。

---

## 设备硬件快照

- **平台**: NVIDIA Jetson（JetPack / L4T R36.4.7，nvidia-l4t-core 36.4.7）
- **CPU**: ARM Cortex-A78AE，6 核，最高 1728 MHz
- **内存**: 7.4 GiB（Swap 11 GiB，可用约 2.4 GiB）
- **NV 功耗模式**: 15W（`nvpmodel`）
- **参考文件**: `outputs/hardware.txt`，`hardware.md`

---

## 摄像头

- **类型**: 2× Sony IMX219（MIPI-CSI）
- **设备节点**: `/dev/video0`（可能对应物理右侧），`/dev/video1`
- **驱动**: tegra-video / imx219（V4L2）
- **常用分辨率/帧率**: 3280×2464@21fps / 1920×1080@30fps / 1280×720@60fps
- **推荐访问方式**（低延迟）: GStreamer `nvarguscamerasrc`；快速测试: `cv2.VideoCapture(0)`
- **注意**: 物理左右位置与设备索引可能不一致，需通过标定确认
- **参考文件**: `cameras.md`，`outputs/camera_v4l2_details.txt`，`outputs/camera_formats.txt`

```python
# OpenCV 快速读取
import cv2
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
```

```bash
# GStreamer 低延迟（推荐）
gst-launch-1.0 nvarguscamerasrc sensor-id=0 \
  ! 'video/x-raw(memory:NVMM),width=1280,height=720,format=NV12,framerate=30/1' \
  ! nvvidconv ! 'video/x-raw,format=BGRx' ! videoconvert ! appsink
```

---

## Python 环境

| 包 | 版本 | 备注 |
|---|---|---|
| `torch` | 2.5.0a0+…nv24.8 | `/usr/local/lib/python3.10/dist-packages` |
| `torchvision` | 0.20.0a0+… | — |
| `ultralytics` | 8.3.59 | YOLO 推理 |
| `tensorrt` | 10.7.0 | TRT 加速 |
| `onnx` | 1.17.0 | 模型格式转换 |
| `mediapipe` | 0.10.18 | 姿态/手势 |
| `ollama` | 0.5.3 | 本地 LLM |
| `opencv-python-headless` | — | `cv2` |

- **完整列表**: `outputs/python_packages.txt`，`python_packages.md`

---

## 模型文件

- **小型 YOLO（推荐优先使用）**:
  - `/home/jetson/Desktop/MX219/yolo11n-seg.pt`（约 6 MB）
  - `yolov8n.pt`（可由 ultralytics 自动下载）
- **大型模型**: `/home/jetson/yahboom_ws/src/largemodel/MODELS/asr/SenseVoiceSmall/model.pt`（约 936 MB）
- **Isaac ROS 资产**: 多个 `.onnx` / `.engine` 文件（stereo disparity、peoplenet、centerpose）
- **完整清单**: `outputs/models_list.txt`，`models.md`

---

## Docker 镜像

| 镜像 | 用途 |
|---|---|
| `isaac_ros_dev-aarch64:latest` | Isaac ROS 开发环境 |
| `nvcr.io/nvidia/isaac/ros:aarch64-ros2_humble_*` | Isaac ROS Humble |
| `ghcr.io/open-webui/open-webui:main` | Open-WebUI（本地 LLM 前端）|
| `heartexlabs/label-studio:latest` | 数据标注 |
| `yahboomtechnology/ros-melodic:1.0` | Yahboom ROS Melodic |
| `nvidia/cuda:12.1.1-base-ubuntu22.04` | CUDA 基础镜像 |

- **参考文件**: `docker_details.md`，`docker_inspect/`

---

## ROS2 / Isaac ROS

- **ROS2 Humble** 已安装于 `/opt/ros/humble`
- **Isaac ROS** 工作区与 Docker 镜像均已就绪
- **参考文件**: `ros_isaac.md`，`outputs/ros_opt_list.txt`，`outputs/ros_env.txt`，`outputs/isaac_paths.txt`

---

## 仓库结构

```
.
├── cameras.md              # 摄像头详情与使用示例
├── hardware.md             # 硬件快照
├── models.md               # 模型文件清单
├── python_packages.md      # Python 环境摘要
├── docker_details.md       # Docker 镜像列表
├── ros_isaac.md            # ROS2/Isaac 状态
├── jetson_system_inventory.md  # 总览文档
├── jetson_agent.py         # 设备上下文工具脚本
├── jetson-benchmark/
│   ├── verify_yolo.py      # YOLO 推理验证脚本
│   └── requirements.txt
├── outputs/                # 原始探测输出（.txt 文件）
└── docker_inspect/         # Docker 镜像逐一检查输出
```

---

## 快速启动命令

```bash
# YOLO 摄像头推理验证
python3 jetson-benchmark/verify_yolo.py

# 查看 GPU 利用率
sudo tegrastats

# 切换功耗模式（0=最大性能，3=15W）
sudo nvpmodel -m 3
sudo jetson_clocks

# 列出摄像头格式
v4l2-ctl --device=/dev/video0 --list-formats-ext
```

---

## 编码规范与建议

1. **设备端推理**: 优先使用 TensorRT（`.engine`）或 ONNX Runtime + TensorRT 后端，避免在 CPU 上跑大模型。
2. **摄像头**: 生产代码用 GStreamer `nvarguscamerasrc`；原型/调试用 `cv2.VideoCapture`。
3. **内存管理**: 设备可用内存约 2.4 GiB，推理时请监控并及时释放张量。
4. **功耗**: 长时推理建议先用 `jetson_clocks` 锁定频率，再用 `tegrastats` 观察热量。
5. **Python 版本**: 系统为 Python 3.10，包位于 `/usr/local/lib/python3.10/dist-packages`。
6. **ROS2**: 使用前执行 `source /opt/ros/humble/setup.bash`。
