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

安装/摆放与坐标系说明
- 摄像头安装姿态（由用户提供）:
  - Z 轴: 指向正前方（摄像头镜头指向的方向）。
  - Y 轴: 竖直向下。
  - X 轴: 水平向右。
- 注意事项: 按“常规”摆放编写的程序有可能出现上下颠倒或左右镜像的问题，且左右摄像头编号可能与物理左右相反（例如 `/dev/video0` 可能是右侧摄像头）。在涉及多摄像头拼接或空间定位的应用中，请在初始化阶段验证每个设备的朝向和左右顺序。
- 注意事项（工程化说明）：
  - 设备枚举不保证物理位置：`/dev/video*` 的索引是内核/驱动枚举结果，不应假定为“左/右”或“前/后”的固定映射；例如 `/dev/video0` 可能对应物理右侧摄像头。
  - 推荐的确定性映射流程（启动时执行）：
    1. 物理标记验证：在每个摄像头视野内放置易识别的方向标记（箭头/棋盘格），分别从每个 `/dev/video*` 采集一帧并识别标记位置，从而建立 "device -> physical position" 的映射表。
    2. Sysfs/udev 元信息匹配：读取 `/sys/class/video4linux/video*/name`、`/sys/class/video4linux/video*/device` 下的属性或 `udevadm info --attribute-walk --path=/sys/class/video4linux/videoX`，用硬件路径（如 i2c 地址或 CSI 端口）作为可靠键来区分物理接口。
    3. 持久化设备名：为避免重启或驱动更新导致的重排，使用 udev 规则创建稳定的符号链接（例如 `/dev/cam_left`、`/dev/cam_right`），基于上一步提取到的唯一硬件属性（serial/i2c/address/of_node 等）。
  - 程序实现要点（AI/自动化友好）：
    - 不要硬编码 `/dev/video0`/`/dev/video1` 为左右摄像头；在初始化阶段运行自动映射脚本并缓存映射结果供后续处理使用。
    - 如果检测到图像上下或左右颠倒，通过明确的、可配置的预处理步骤修正（例如 `cv2.flip()` 或图像矩阵转置），并将该修正作为配置参数写入运行时元数据以供后续模型/管道使用。
    - 将映射与校正结果记录为机器可读的 JSON（例如 `camera_map.json`），格式示例：
      ```json
      {
        "devices": [
          {"dev":"/dev/video0","position":"left","flip":"none","hw_key":"i2c-9-0010"},
          {"dev":"/dev/video1","position":"right","flip":"vertical","hw_key":"i2c-10-0010"}
        ]
      }
      ```
    - 在多摄像头拼接或几何校正流程中首选使用上述 `hw_key` 或持久化符号链接作为数据源，而非内核索引。

如何验证（建议）
- 在启动推理/标定前，拍一张标有方向的测试图（例如放置箭头/棋盘格），分别从 `/dev/video0` 与 `/dev/video1` 采集并确认左右与上下方向是否与期望一致。
- 若发现左右/上下颠倒，可在预处理阶段对帧执行 `cv2.flip()` 或交换摄像头索引来修正。

