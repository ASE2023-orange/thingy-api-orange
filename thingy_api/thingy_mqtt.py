"""
MQTT utils file.
Created by: Leyla Kandé on 9 november 2023
Updated by: Leyla Kandé on 9 november 2023
"""

from datetime import datetime
import json
import logging
from os import getenv
import os
import threading

from dotenv import load_dotenv
import paho.mqtt.client as mqtt

from thingy_api.influx import write_point

# take environment variables from api.env
load_dotenv(dotenv_path='environments/api.env')
# MQTT parameters
mqtt_broker = getenv('MQTT_BROKER')
mqtt_port = int(getenv('MQTT_PORT'))
mqtt_username = getenv('MQTT_USERNAME')
mqtt_password = getenv('MQTT_PASSWORD')
mqtt_topic = 'things/+/shadow/update'

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
# Contains all measurements to retain in Influxdb.
INFLUX_DATA_IDS = ["AIR_PRESS", "AIR_QUAL", "CO2_EQUIV", 
                   "HUMID", "LIGHT", "RSRP", "TEMP"]

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        logging.info("Connected to MQTT Broker!")
        client.subscribe(mqtt_topic)
    else:
        print("Failed to connect, return code %d\n", rc)
        logging.error("Failed to connect, return code %d\n", rc)

def on_message(client, userdata, msg):  
    data = msg.payload.decode()
    add_to_latest(data)
    # retrieves thingy's ID
    thingy_id = msg.topic.split('/')[1] # Works only if id is in between first and second slash
    # Append the data to the file in a non-blocking way
    threading.Thread(target=append_data_to_backup, args=(data, thingy_id)).start()
    # print(f"Received `{data}` from `{msg.topic}` topic")

    if "appId" in json.loads(data) and json.loads(data)["appId"] in INFLUX_DATA_IDS:
        # Only send metric data to influx, ignore others
        send_influx(msg, thingy_id)


def append_data_to_backup(data, thingy_id):
    """Writes thingy data to a backup file inside data/ folder."""
    # Get the current date in 'yyyymmdd' format
    current_date = datetime.now().strftime('%Y%m%d')
    filename = f'data/{thingy_id}/{current_date}.txt'

    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'a') as file:
        file.write(data + '\n')


def start_mqtt():
    """
    Start mqtt server using client.loop_start() to allow multiple
    services to run.
    """
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

def send_influx(msg, thingy_id):
    """Writes thingy data to Influxdb."""
    data = json.loads(msg.payload.decode())
    measurement = data.get('appId') # Label
    value = data["data"] # Value
    # Timestamp value removed (incoherent)
    # Using current time instead
    # timestamp = data["ts"]

    res = write_point(value, measurement, thingy_id)
    return res

def get_thingy_data():
    """ returns the latest thingy data """
    global latest_sensor_data
    return latest_sensor_data