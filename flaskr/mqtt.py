import base64
import paho.mqtt.client as mqtt
import json
import cv2
import numpy as np
import queue
import threading

# MQTT Configuration
MQTT_CLIENT_ID = "sic6_stage2_rest"
MQTT_BROKER = "broker.emqx.io"
MQTT_TOPIC_SUB = "/UNI544/ADHYAKSAWARUNAPUTRO/data_sensor"

# Thread-safe queue to store incoming frames
frame_queue = queue.Queue()

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(MQTT_TOPIC_SUB)

def on_message(client, userdata, msg):
    print(f"Received message from {msg.topic}")
    
    try:
        # Decode MQTT JSON message
        message = json.loads(msg.payload.decode())

        # Convert hex to base64
        img_base64 = hex_to_base64(message["camera_buffer"])

        # Convert base64 to OpenCV Image
        img = base64_to_image(img_base64)

        # Put the frame into the queue
        if img is not None:
            if not frame_queue.full():  # Avoid excessive memory usage
                frame_queue.put(img)

    except Exception as e:
        print("Error processing frame:", e)

def hex_to_base64(hex_string):
    """ Convert hex string to base64 string """
    byte_data = bytes.fromhex(hex_string)
    base64_data = base64.b64encode(byte_data)
    return base64_data.decode('utf-8')

def base64_to_image(base64_string):
    """ Convert base64 string to OpenCV image """
    img_data = base64.b64decode(base64_string)
    np_arr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)  # Convert to image
    return img

def mqtt_thread():
    """ Run MQTT loop in a separate thread """
    client = mqtt.Client(client_id=MQTT_CLIENT_ID, protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_forever()

def main():
    """ Main loop to display frames """
    threading.Thread(target=mqtt_thread, daemon=True).start()  # Start MQTT in the background

    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            cv2.imshow("ESP32 Stream", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break  # Press 'q' to exit

    cv2.destroyAllWindows()  # Cleanup OpenCV windows

if __name__ == "__main__":
    main()
