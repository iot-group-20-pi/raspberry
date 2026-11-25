import os

from ultralytics import YOLO


def get_model(path: str) -> YOLO:
    if not os.path.exists(path):
        raise FileNotFoundError()

    return YOLO(path)
