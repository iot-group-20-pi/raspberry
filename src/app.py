from __future__ import annotations

from multiprocessing import Process, Queue
from typing import Literal

from flask import Flask, Response, render_template

from file import FILE_DATA, file_thread
from mqtt_publish import MQTT_DATA, publisher_thread


def app_thread(
    model_path: str,
    frame: Literal["camera", "pi-camera", "video"] = "video",
    mqtt_q: Queue[MQTT_DATA] | None = None,
    file_q: Queue[FILE_DATA] | None = None,
):
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/video_feed")
    def video_feed():
        model = get_model(model_path)

        if frame == "camera":
            from app_frame import generate_frame_from_camera

            generator = generate_frame_from_camera(model, mqtt_q, file_q)
        elif frame == "pi-camera":
            from app_frame import generate_frame_from_pi_camera

            generator = generate_frame_from_pi_camera(
                model, app.config["picam2"], mqtt_q, file_q
            )
        else:
            from app_frame import generate_frame_from_video

            generator = generate_frame_from_video(model, mqtt_q, file_q)

        return Response(generator, mimetype="multipart/x-mixed-replace; boundary=frame")

    if frame == "pi-camera":
        from utils.camera import start_pi_camera

        app.config["picam2"] = start_pi_camera()
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("model_path", help="Path to the YOLO model")
    parser.add_argument(
        "frame",
        choices=["camera", "pi-camera", "video"],
        help="Frame to generate from (camera or video)",
    )
    parser.add_argument("--mqtt", default=False, action=argparse.BooleanOptionalAction)
    parser.add_argument("--file", default=False, action=argparse.BooleanOptionalAction)
    parser.add_argument(
        "--upload", default=False, action=argparse.BooleanOptionalAction
    )
    args = parser.parse_args()
    model_path = str(args.model_path)
    frame = str(args.frame)
    mqtt = bool(args.mqtt)
    file = bool(args.file)
    upload = bool(args.upload)

    from utils.model import get_model

    mqtt_q: Queue[MQTT_DATA] | None = None
    file_q: Queue[FILE_DATA] | None = None

    if mqtt:
        mqtt_q = Queue()
        mqtt_process = Process(target=publisher_thread, args=(mqtt_q,))
        mqtt_process.start()

    if file:
        file_q = Queue()
        file_process = Process(target=file_thread, args=(file_q, upload))
        file_process.start()

    app_process = Process(target=app_thread, args=(model_path, frame, mqtt_q, file_q))
    app_process.start()
