# Cameras - Jetson 硬件/驱动 与 使用说明

概述
- 本设备检测到两个 MIPI-CSI 摄像头（Sony IMX219），分别映射为 `/dev/video0` 和 `/dev/video1`（见 outputs/camera_v4l2_details.txt）。
- 驱动：tegra-video / imx219（通过 V4L2 提供接口）。
- 推荐访问方式：测试/快速使用可用 OpenCV 的 `cv2.VideoCapture(0)`；为获得最低延迟和最佳性能建议使用 NVIDIA 的 GStreamer 元件（`nvarguscamerasrc`/`nvv4l2dec` 等）或 `nvcamerasrc`（取决于 JetPack 版本）。

检测摘要
- 设备节点：`/dev/video0`, `/dev/video1`
- V4L2 名称示例：`vi-output, imx219 9-0010`、`vi-output, imx219 10-0010`
- 常见可用格式（来自 `v4l2-ctl --list-formats-ext`）：
  - 3280x2464 @21fps (10-bit Bayer)
  - 3280x1848 @28fps
  - 1920x1080 @30fps
  - 1280x720 @60fps

参考文件（仓库内）
- `outputs/camera_v4l2_details.txt` — 每个 `/dev/video*` 的 `v4l2-ctl --all` 输出。
- `outputs/camera_formats.txt` — `--list-formats-ext` 结果。
- `outputs/camera_udev.txt`, `outputs/lsusb.txt` — udev/USB 列表（如适用）。

使用示例

- 简单 OpenCV（兼容多数用例）：
```
import cv2
cap = cv2.VideoCapture(0)  # 或 1
ret, frame = cap.read()
if ret:
    cv2.imshow('frame', frame)
cap.release()
```

- 推荐（更低延迟，Jetson 上常用）GStreamer / nvarguscamerasrc 示例（调整 `sensor-id`, `width`, `height`, `framerate`）：
```
gst-launch-1.0 nvarguscamerasrc sensor-id=0 ! 'video/x-raw(memory:NVMM),width=1280,height=720,format=NV12,framerate=30/1' ! nvvidconv ! 'video/x-raw,width=1280,height=720,format=BGRx' ! videoconvert ! 'video/x-raw,format=BGR' ! appsink
```
OpenCV 中使用 GStreamer 管道：
```
pipeline = "nvarguscamerasrc sensor-id=0 ! video/x-raw(memory:NVMM),width=1280,height=720,framerate=30/1 ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! appsink"
cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
```

注意与建议
- 若需最高吞吐和低延迟（用于实时推理），优先使用 `nvarguscamerasrc` / `nvcamerasrc` + GStreamer，然后在用户空间直接传入 TensorRT/ONNX 推理输入。
- 若碰到颜色格式或字节对齐问题，请在 `nvvidconv`/`videoconvert` 阶段明确指定格式为 `BGR` 或 `RGB`。
- 已保存的详细探测输出：`outputs/camera_v4l2_details.txt`、`outputs/camera_formats.txt`、`outputs/camera_udev.txt`（仓库内）。
