from picamera2 import Picamera2


def start_pi_camera() -> Picamera2:
    picam2 = Picamera2()
    picam2.configure(
        picam2.create_preview_configuration(
            main={"format": "RGB888", "size": (1280, 720)}
        )
    )
    picam2.start()

    return picam2
