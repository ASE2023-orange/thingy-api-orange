import json
from os import getenv
from dotenv import load_dotenv
from flask import jsonify
import paho.mqtt.client as mqtt

# take environment variables from api.env
load_dotenv(dotenv_path='api.env')
# MQTT parameters
mqtt_broker = getenv('MQTT_BROKER')
mqtt_port = int(getenv('MQTT_PORT'))
mqtt_username = getenv('MQTT_USERNAME')
mqtt_password = getenv('MQTT_PASSWORD')
mqtt_topic = 'things/+/shadow/update'

received_data = ''
latest_sensor_data = {
    'pressure': None,
    'humidity': None,
    'light': None
}

appId_map = {
    "HUMID": "humidity",
    "AIR_PRESS": "pressure",
    "LIGHT": "light"
}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(mqtt_topic)
    else:
        print("Failed to connect, return code %d\n", rc)

def on_message(client, userdata, msg):
    global received_data
    received_data = msg.payload.decode()
    add_to_latest(received_data)
    print(f"Received `{received_data}` from `{msg.topic}` topic")


async def start_mqtt(loop):
    client = mqtt.Client()

    # set callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    #set MQTT credentials
    client.username_pw_set(mqtt_username, mqtt_password)

    # establish conneciton
    client.connect_async(mqtt_broker, mqtt_port, 60)

    client.loop_start()

def add_to_latest(message):
    msg = json.loads(message)
    if "appId" in msg and msg["appId"] in appId_map:
        key = appId_map[msg["appId"]]
        latest_sensor_data[key] = msg["data"]

def get_thingy_data():
    """ returns the latest thingy data """
    global latest_sensor_data
    return latest_sensor_data

