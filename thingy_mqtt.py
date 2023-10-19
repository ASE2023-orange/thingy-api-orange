import paho.mqtt.client as mqtt

# MQTT parameters
mqtt_broker = "163.172.151.151"
mqtt_port = 1889 
mqtt_topic = "things/+/shadow/update"
mqtt_username = "orange"
mqtt_password = "3mxNdz9W7G"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(mqtt_topic)
    else:
        print("Failed to connect, return code %d\n", rc)

def on_message(client, userdata, msg):
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")


def start_mqtt():
    client = mqtt.Client()

    # set callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    #set MQTT credentials
    client.username_pw_set(mqtt_username, mqtt_password)

    # establish conneciton
    client.connect(mqtt_broker, mqtt_port, 60)

    client.loop_forever()