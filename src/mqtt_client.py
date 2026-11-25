import ssl
from typing import Any, Literal

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion, MQTTErrorCode, MQTTProtocolVersion
from paho.mqtt.properties import Properties

from utils.config import env


class MQTTClient(mqtt.Client):
    def __init__(
        self,
        callback_api_version: CallbackAPIVersion = CallbackAPIVersion.VERSION2,
        client_id: str | None = "",
        clean_session: bool | None = None,
        userdata: Any = None,
        protocol: MQTTProtocolVersion = MQTTProtocolVersion.MQTTv5,
        transport: Literal["tcp", "websockets", "unix"] = "tcp",
        reconnect_on_failure: bool = True,
        manual_ack: bool = False,
    ):
        super().__init__(
            callback_api_version=callback_api_version,
            client_id=client_id,
            clean_session=clean_session,
            userdata=userdata,
            protocol=protocol,
            transport=transport,
            reconnect_on_failure=reconnect_on_failure,
            manual_ack=manual_ack,
        )
        self.tls_set(
            ca_certs=env["MQTT"]["CACERTS"],
            certfile=env["MQTT"]["CERTFILE"],
            keyfile=env["MQTT"]["KEYFILE"],
            keyfile_password=env["MQTT"]["KEYFILE_PASSWORD"],
            tls_version=ssl.PROTOCOL_TLSv1_2,
        )
        self.tls_insecure_set(False)
        self.username_pw_set(
            username=env["MQTT"]["USERNAME"], password=env["MQTT"]["PASSWORD"]
        )

    def connect(
        self,
        host: str = env["MQTT"]["HOSTNAME"],
        port: int = env["MQTT"]["PORT"],
        keepalive: int = 60,
        bind_address: str = "",
        bind_port: int = 0,
        clean_start: mqtt.CleanStartOption = mqtt.MQTT_CLEAN_START_FIRST_ONLY,
        properties: Properties | None = None,
    ) -> MQTTErrorCode:
        return super().connect(
            host,
            port,
            keepalive,
            bind_address,
            bind_port,
            clean_start,
            properties,
        )
