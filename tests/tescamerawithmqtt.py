import cv2
import binascii
import numpy as np
import paho.mqtt.client as mqtt
import json
import threading
import queue

# MQTT Configuration
MQTT_CLIENT_ID = "sic6_stage2_rest"
MQTT_BROKER = "broker.emqx.io"
MQTT_TOPIC_SUB = "/UNI544/ADHYAKSAWARUNAPUTRO/data_sensor"

# Queue for processing frames in a separate thread
message_queue = queue.Queue()

def buffer_to_img(img_buffer):
    np_arr = np.frombuffer(img_buffer, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img

def flame_detector(img_buffer):
    img = buffer_to_img(img_buffer)
    print("Processing frame in flame_detector")
    
    if img is not None:
        """ Parameters for fire detection based on HSV and minimum contour area """
        lower_red = np.array([8, 17, 50])
        upper_red = np.array([126, 149, 255])

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_red, upper_red)

        min_contour_area = 100
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        fire_detected = any(cv2.contourArea(contour) >= min_contour_area for contour in contours)

        cv2.drawContours(img, contours, -1, (0, 255, 0), 2)
        cv2.imshow("ESP32 Stream", img)
        cv2.waitKey(1)  # Ensure the window refreshes properly
        
        return int(fire_detected)

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(MQTT_TOPIC_SUB)

def on_message(client, userdata, msg):
    print(f"Received message from {msg.topic}")
    message_queue.put(msg.payload)  # Add message to queue instead of processing directly

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
            flame_status = flame_detector(img_buffer)
            print(f"Flame detection status: {flame_status}")

def main():
    mqtt_thread_instance = threading.Thread(target=mqtt_thread)
    processor_thread = threading.Thread(target=process_frames)
    
    mqtt_thread_instance.start()
    processor_thread.start()
    
    mqtt_thread_instance.join()
    processor_thread.join()
    
if __name__ == "__main__":
    main()
