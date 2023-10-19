from os import getenv

from dotenv import load_dotenv
import paho.mqtt.client as mqtt

# take environment variables from api.env
load_dotenv(dotenv_path='api.env')
# MQTT parameters
mqtt_broker = getenv('MQTT_BROKER')
mqtt_port = int(getenv('MQTT_PORT'))
mqtt_username = getenv('MQTT_USERNAME')
mqtt_password = getenv('MQTT_PASSWORD')
mqtt_topic = 'things/+/shadow/update'


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(mqtt_topic)
    else:
        print("Failed to connect, return code %d\n", rc)

def on_message(client, userdata, msg):
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")


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