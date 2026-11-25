from __future__ import annotations

from multiprocessing import Queue
from typing import Literal

from paho.mqtt.client import Client, PayloadType
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode

from mqtt_client import MQTTClient

MQTT_TOPIC = Literal["detection"]
MQTT_DATA = tuple[MQTT_TOPIC, PayloadType]


def on_publish(
    client: Client,
    userdata,
    mid: int,
    reason_code: ReasonCode,
    properties: Properties,
):
    print("on_publish", reason_code)


def publisher_thread(in_q: Queue[MQTT_DATA]):
    mqttc = MQTTClient()
    mqttc.connect()

    mqttc.loop_start()
    while True:
        topic, message = in_q.get()
        mqttc.publish(topic, message)

    mqttc.loop_stop()


if __name__ == "__main__":
    mqttc = MQTTClient()

    mqttc.on_publish = on_publish

    mqttc.connect()

    mqttc.loop_start()

    mqttc.publish("test", "my message", qos=1).wait_for_publish()
    mqttc.disconnect()

    mqttc.loop_stop()
