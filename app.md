# Object Detection Application using YOLO26 object detection model

## Useful documentations

<https://docs.ultralytics.com/guides/raspberry-pi>  
<https://docs.ultralytics.com/modes/predict>

## Setup

### Export model to NCNN format

See [YOLO export usage](https://docs.ultralytics.com/modes/export) to optionally quantize the model.

```sh
# Export a YOLO26n PyTorch model to NCNN format
yolo export model=model/yolo26n.pt format=ncnn # creates 'yolo26n_ncnn_model'

# Run inference with the exported model
yolo predict model='model/yolo26n_ncnn_model' source='https://ultralytics.com/images/bus.jpg'
```

## Application Usage

### [app.py](./src/app.py)

Run with extra web application for debugging purposes  
it takes model_path and input_mode (detail in [app_frame.py](./src/app_frame.py)).

Input Modes

1. camera, for laptop camera, used for testing
2. pi-camera, for raspberry pi camera (this will lock the camera device)
3. video, uses the [video.mp4](./video.mp4) file, used for testing

```sh
# args0                - model_path
# args1                - input {camera, pi-camera, video}
# --mqtt --no-mqtt     - send mqtt data when object is detected
# --file --no-file     - save file to device storage when object is detected
# --upload --no-upload - upload file to s3 when object is detected (requires file to be enabled)

uv run src/app.py model/yolo26n_ncnn_model pi-camera
```

### [main.py](./src/main.py) (code unfinished)

Run without extra web application for increased performance

### [mqtt_publish.py](./src/mqtt_publish.py) (main function unfinished)

Used to test publishing mqtt message

```sh
uv run src/mqtt_publish.py
```

### [mqtt_subscribe.py](./src/mqtt_subscribe.py) (main function unfinished)

Used to test subscribing to all mqtt topics

```sh
uv run src/mqtt_publish.py
```
