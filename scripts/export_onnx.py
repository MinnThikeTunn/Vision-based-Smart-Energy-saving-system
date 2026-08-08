#!/usr/bin/env python3
"""
Model Acceleration Script: Export PyTorch YOLOv8 model to ONNX format.
"""
import sys
import time
from pathlib import Path


def export_model(model_path: str = "yolov8n.pt", output_format: str = "onnx") -> bool:
    print(f"==================================================")
    print(f" Exporting YOLO Model ({model_path}) -> {output_format.upper()} ")
    print(f"==================================================")

    model_file = Path(model_path)
    if not model_file.exists():
        print(f"Model file {model_path} not found. Skipping export.")
        return False

    try:
        from ultralytics import YOLO

        print("Loading PyTorch model weights...")
        t0 = time.time()
        model = YOLO(model_path)
        print(f"Model loaded in {time.time() - t0:.2f}s")

        print(f"Exporting to {output_format} format...")
        t1 = time.time()
        exported_path = model.export(format=output_format)
        print(f"Export successful in {time.time() - t1:.2f}s! Exported model saved at: {exported_path}")
        return True
    except Exception as e:
        print(f"Export failed or ultralytics export dependencies missing: {e}")
        return False


if __name__ == "__main__":
    model_arg = sys.argv[1] if len(sys.argv) > 1 else "yolov8n.pt"
    export_model(model_arg, "onnx")
