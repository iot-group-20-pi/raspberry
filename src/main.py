from datetime import UTC, datetime
from multiprocessing import Process, Queue

from ultralytics.engine.results import Results

from file import FILE_DATA, file_thread
from mqtt_publish import MQTT_DATA, publisher_thread
from pipeline import result_pipeline
from utils.camera import start_pi_camera
from utils.model import get_model


def main_thread(model_path, out_mqtt_q: Queue[MQTT_DATA], out_file_q: Queue[FILE_DATA]):
    picam2 = start_pi_camera()
    model = get_model(model_path)

    while True:
        current_time = datetime.now(tz=UTC)
        frame = picam2.capture_array()
        for result in model.predict(frame, verbose=False):
            # OPTIM: remove after everything works
            if not isinstance(result, Results):
                raise TypeError(
                    "The model result type mismatch, predict parameters may be wrong"
                )

            result_pipeline(
                result,
                mqtt_q=out_mqtt_q,
                file_q=out_file_q,
                current_time=current_time,
            )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("model_path", help="Path to the YOLO model")
    args = parser.parse_args()
    model_path = str(args.model_path)

    mqtt_q: Queue[MQTT_DATA] = Queue()
    file_q: Queue[FILE_DATA] = Queue()

    publisher_process = Process(target=publisher_thread, args=(mqtt_q,))
    file_process = Process(target=file_thread, args=(file_q,))
    main_process = Process(target=main_thread, args=(mqtt_q,))

    publisher_process.start()
    file_process.start()
    main_process.start()
