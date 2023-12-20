"""
MQTT utils file.
Created by: Leyla Kandé on 9 november 2023
Updated by: LK on 20 dec 2023
"""

import json
import logging
import os
import threading
from datetime import datetime
from os import getenv

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from dotenv import load_dotenv
import thingy_api.dal.maintenance as maintenance_dal
from thingy_api.dal.thingy_id import add_new_id, get_all_thingy_ids, update_id
from thingy_api.influx import write_point

# take environment variables from api.env
load_dotenv(dotenv_path='environments/api.env')
# MQTT parameters
mqtt_broker = getenv('MQTT_BROKER', "127.0.0.1")
mqtt_port = int(getenv('MQTT_PORT', "1889"))
mqtt_username = getenv('MQTT_USERNAME', "user")
mqtt_password = getenv('MQTT_PASSWORD', "password")
mqtt_topic = 'things/+/shadow/update'

latest_sensor_data = { }

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
    # retrieves thingy's ID
    thingy_id = msg.topic.split('/')[1] # Works only if id is in between first and second slash
    message = json.loads(data)

    update_thingy_id_list(thingy_id)

    if "appId" in message and message["appId"] == "BUTTON" and message["data"] == "1":
        update_maintenance(thingy_id)
    else: 
        #Update real-time on FE 
        add_to_latest(message, thingy_id)
        # Append the data to the file in a non-blocking way
        threading.Thread(target=append_data_to_backup, args=(data, thingy_id)).start()
        # print(f"Received `{data}` from `{msg.topic}` topic")

        if "appId" in json.loads(data) and json.loads(data)["appId"] in INFLUX_DATA_IDS:
            # Only send metric data to influx, ignore others
            send_influx(message, thingy_id)


def publish_led_color(thingy_id, color):
    """Changes led color of the selected thingy using a publish message."""
    try:
        topic = f'things/{thingy_id}/shadow/update/accepted'
        payload = {
            "appId": "LED",
            "data": {
                "color": color
            },
            "messageType": "CFG_SET"
        }
        payload_str = json.dumps(payload)

        auth = {'username': mqtt_username, 'password': mqtt_password}

        publish.single(
            topic,
            payload=payload_str,
            qos=1,
            retain=False,
            hostname=mqtt_broker,
            port=mqtt_port,
            auth=auth # type: ignore
        )
    except Exception as e:
        logging.error(e)


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

def add_to_latest(msg, thingy_id):
    #create sensor data object if thingy id unknonw
    if thingy_id not in latest_sensor_data:
        latest_sensor_data[thingy_id] = {}

    if "appId" in msg and msg["appId"] in appId_map:
        key = appId_map[msg["appId"]]
        latest_sensor_data[thingy_id][key] = msg["data"]

def send_influx(msg, thingy_id):
    """Writes thingy data to Influxdb."""
    measurement = msg.get('appId') # Label
    value = msg["data"] # Value
    # Timestamp value removed (incoherent)
    # Using current time instead
    # timestamp = data["ts"]

    res = write_point(value, measurement, thingy_id)
    return res

def get_thingy_data():
    """ returns the latest thingy data """
    global latest_sensor_data
    return latest_sensor_data

def get_thingy_id_data(thingy_id):
    """ returns the latest thingy data for ID"""
    id_data = { thingy_id: latest_sensor_data[thingy_id]}
    return id_data

def update_thingy_id_list(thingy_id):
    existing = get_all_thingy_ids()
    maintenance = maintenance_dal.get_all_maintenance_thingies()
    if thingy_id not in existing:
        add_new_id(thingy_id)
    else:
        update_id(thingy_id)
    if thingy_id not in maintenance:
        maintenance_dal.add_new_thingy_id(thingy_id)

def update_maintenance(thingy_id):
    status = maintenance_dal.get_maintenance_status(thingy_id)
    if status['maintenance_status'] == True:
        maintenance_dal.set_maintenance_end(thingy_id)
    else:
        maintenance_dal.set_maintenance_start(thingy_id)
