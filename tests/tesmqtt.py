import paho.mqtt.client as mqtt

# MQTT Configuration
MQTT_CLIENT_ID = "test_subscriber"
MQTT_BROKER = "broker.emqx.io"  # Change if needed
MQTT_TOPIC_SUB = "/UNI544/ADHYAKSAWARUNAPUTRO/data_sensor"

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(MQTT_TOPIC_SUB, qos=1)  # Use QoS 1 for reliability

def on_message(client, userdata, msg):
    print(f"Received message from {msg.topic}: {msg.payload}")

def main():
    client = mqtt.Client(client_id=MQTT_CLIENT_ID, protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, 1883, keepalive=10)
    client.loop_forever()  # Keep listening for messages

if __name__ == "__main__":
    main()
