**系统 Python 包简表**

完整包清单（按 `pip3 list` 导出）见： [outputs/python_packages.txt](outputs/python_packages.txt)

重点关注的包：
- `torch`: 2.5.0a0+... (Location: /usr/local/lib/python3.10/dist-packages)
- `torchvision`: 0.20.0a0+...
- `torchaudio`: 2.5.1a0+...
- `ultralytics`: 8.3.59
- `mediapipe`: 0.10.18
- `onnx`: 1.17.0
- `tensorrt`: 10.7.0
- `ollama`: 0.5.3 (位于 /home/jetson/.local/lib...)

这些包表明设备已具备进行 YOLO/TensorRT 推理验证的基础依赖（需要在脚本中验证 GPU 可用性）。
