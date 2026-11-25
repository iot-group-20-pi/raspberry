import os

from dotenv import load_dotenv

load_dotenv()

env = {
    "MQTT": {
        "HOSTNAME": os.getenv("MQTT_HOSTNAME", default="localhost"),
        "PORT": int(os.getenv("MQTT_PORT", default="8883")),
        "USERNAME": os.getenv("MQTT_USERNAME", default="username"),
        "PASSWORD": os.getenv("MQTT_PASSWORD", default="password"),
        "CACERTS": os.getenv("MQTT_CACERTS"),
        "CERTFILE": os.getenv("MQTT_CERTFILE"),
        "KEYFILE": os.getenv("MQTT_KEYFILE"),
        "KEYFILE_PASSWORD": os.getenv("MQTT_KEYFILE_PASSWORD"),
    },
    "AWS": {
        "REGION_NAME": os.getenv("AWS_REGION_NAME"),
        "ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
        "SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
    },
    "DATA_FOLDER": os.getenv("DATA_FOLDER"),
    "BUCKET_NAME": os.getenv("BUCKET_NAME"),
}
