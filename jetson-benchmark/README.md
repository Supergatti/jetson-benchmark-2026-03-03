jetson-benchmark
================

This folder contains a lightweight YOLO verification script `verify_yolo.py` to test ultralytics inference and attempt TensorRT export on NVIDIA Jetson.

Quick run (from workspace root):

```bash
python3 jetson-benchmark/verify_yolo.py
```

Outputs will be written to `outputs/yolo_benchmark_results.txt` and an annotated image copy to `outputs/` if produced.
