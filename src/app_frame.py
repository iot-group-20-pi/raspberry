from __future__ import annotations

from multiprocessing import Queue

import cv2
from ultralytics import YOLO
from ultralytics.engine.results import Results

from file import FILE_DATA
from mqtt_publish import MQTT_DATA
from pipeline import result_pipeline


def generate_frame_from_camera(
    model: YOLO, mqtt_q: Queue[MQTT_DATA] | None, file_q: Queue[FILE_DATA] | None
):
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue

        for result in model.predict(frame, verbose=False):
            if not isinstance(result, Results):
                raise TypeError(
                    "The model result type mismatch, predict parameters may be wrong"
                )

            result_pipeline(result, mqtt_q, file_q)

            success, annotated_img = cv2.imencode(".jpg", result.plot())
            if not success:
                continue

            yield (
                b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                + annotated_img.tobytes()
                + b"\r\n"
            )


def generate_frame_from_pi_camera(
    model: YOLO,
    picam2,
    mqtt_q: Queue[MQTT_DATA] | None,
    file_q: Queue[FILE_DATA] | None,
):
    # TODO: i do this to avoid libcamera module not found on laptop testing
    from picamera2 import Picamera2

    if not isinstance(picam2, Picamera2):
        raise TypeError()

    while picam2.is_open:
        frame = picam2.capture_array()

        for result in model.predict(frame, verbose=False):
            if not isinstance(result, Results):
                raise TypeError(
                    "The model result type mismatch, predict parameters may be wrong"
                )

            result_pipeline(result, mqtt_q, file_q)

            success, annotated_img = cv2.imencode(".jpg", result.plot())
            if not success:
                continue

            yield (
                b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                + annotated_img.tobytes()
                + b"\r\n"
            )


def generate_frame_from_video(
    model: YOLO, mqtt_q: Queue[MQTT_DATA] | None, file_q: Queue[FILE_DATA] | None
):
    for result in model.predict("video.mp4", vid_stride=30, stream=True, verbose=False):
        if not isinstance(result, Results):
            raise TypeError(
                "The model result type mismatch, predict parameters may be wrong"
            )

        result_pipeline(result, mqtt_q, file_q)

        success, annotated_img = cv2.imencode(".jpg", result.plot())
        if not success:
            continue

        yield (
            b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
            + annotated_img.tobytes()
            + b"\r\n"
        )
