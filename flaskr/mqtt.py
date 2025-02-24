import paho.mqtt.client as mqtt
import json
import threading
import queue
import camera

# MQTT Configuration
MQTT_CLIENT_ID = "sic6_stage2_rest"
MQTT_BROKER = "broker.emqx.io"
MQTT_TOPIC_SUB = "/UNI544/ADHYAKSAWARUNAPUTRO/data_sensor"

# Queue for processing frames in a separate thread
message_queue = queue.Queue()

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(MQTT_TOPIC_SUB)

def on_message(client, userdata, msg):
    print(f"Received message from {msg.topic}")

    # Add message to queue instead of processing directly
    message_queue.put(msg.payload)

def mqtt_thread():
    client = mqtt.Client(client_id=MQTT_CLIENT_ID, protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_start()

def process_frames():
    """ Continuously process frames from the queue without blocking MQTT """
    while True:
        if not message_queue.empty():
            img_buffer = message_queue.get()
            camera.flame_detector(img_buffer)
            print("Camera has finished its job")

def main():
    mqtt = threading.Thread(target=mqtt_thread)
    processor = threading.Thread(target=process_frames)

    mqtt.start()
    processor.start()
    
if __name__ == "__main__":
    main()
