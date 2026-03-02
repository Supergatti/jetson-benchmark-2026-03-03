**模型文件扫描清单**

已全局扫描并收集常见模型后缀（`.pt`, `.pth`, `.onnx`, `.engine`, `.trt`, `.gguf`, `.safetensors`）。完整列表见：

- [outputs/models_list.txt](outputs/models_list.txt)

示例（截取）：
- /home/jetson/yahboom_ws/src/largemodel/MODELS/asr/SenseVoiceSmall/model.pt  (约 936,291,369 bytes)
- /home/jetson/Desktop/MX219/yolo11n-seg.pt (约 6,182,636 bytes)
- 多个 Isaac ROS 资产目录下存在 `.onnx` 与 `.engine` 文件（stereo disparity、peoplenet、centerpose 等）

建议：对较大的模型文件进行备份与归档，避免占用设备可用空间；第三阶段将优先使用小型 YOLO 模型（如 `yolov8n` 或 `yolo11n-seg.pt`）进行推理验证。
