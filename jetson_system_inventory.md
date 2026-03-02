**Overview**

**Summary**: 本仓库包含针对当前 NVIDIA Jetson 设备的硬件与系统盘点、Docker 镜像检查、Python 环境清单、ROS/Isaac 检查与模型文件列表的原始输出和整理报告。

**Key findings (简要)**:
- JetPack / L4T: R36.4.7 (nvidia-l4t-core 36.4.7)
- CPU: 6-core ARM Cortex-A78AE
- Memory: ~7.4 GiB (可用约 2.4 GiB)
- Current NVPModel: 15W
- 已安装关键软件：PyTorch (torch 2.5.0a0...nv24.8), ultralytics 8.3.59, tensorrt 10.7.0, mediapipe 等
- 检测到若干大型 Docker 镜像（含 Isaac ROS、Open-WebUI、Label-Studio 等），以及多个工程下的模型文件（.pt/.onnx/.engine）

**Files (原始输出与详细信息)**

- 硬件与系统快照: [outputs/hardware.txt](outputs/hardware.txt)
- Docker 镜像逐个检查（原始输出目录）: [docker_inspect](docker_inspect)
- 已安装 Python 包（简表）: [outputs/python_packages.txt](outputs/python_packages.txt)
- ROS 信息: [outputs/ros_opt_list.txt](outputs/ros_opt_list.txt)  [outputs/ros_env.txt](outputs/ros_env.txt)
- Isaac 路径搜索: [outputs/isaac_paths.txt](outputs/isaac_paths.txt)
- 模型文件清单（全局扫描）: [outputs/models_list.txt](outputs/models_list.txt)

- Cameras: see [cameras.md](cameras.md)

请参阅下列分节文档了解每个部分的详细整理与结论。
