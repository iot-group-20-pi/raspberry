from paho.mqtt.client import Client, ConnectFlags, MQTTMessage
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode

from mqtt_client import MQTTClient


def on_subscribe(
    client: Client,
    userdata,
    mid: int,
    reason_code_list: list[ReasonCode],
    properties: Properties | None,
):
    print("on_subscribe", reason_code_list)


def on_unsubscribe(
    client: Client,
    userdata,
    mid: int,
    reason_code_list: list[ReasonCode],
    properties: Properties | None,
):
    print("on_unsubscribe", reason_code_list)
    client.disconnect()


def on_message(client: Client, userdata, message: MQTTMessage):
    print(f"({message.topic}) {message.payload}")


def on_connect(
    client: Client,
    userdata,
    flags: ConnectFlags,
    reason_code: ReasonCode,
    properties: Properties | None,
):
    print("on_connect", reason_code)

    if not reason_code.is_failure:
        client.subscribe("#")


if __name__ == "__main__":
    mqttc = MQTTClient()

    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.on_subscribe = on_subscribe
    mqttc.on_unsubscribe = on_unsubscribe

    mqttc.connect()

    mqttc.loop_forever()
