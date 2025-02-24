from flask import Flask, request, jsonify
import requests
import paho.mqtt.client as mqtt
import threading
import queue
import camera

app = Flask(__name__)

# Token Ubidots
UBIDOTS_TOKEN = "BBUS-YRFncRgHQkiPjyr0qTLncnR6EKZ00F"  # Ganti dengan token API Ubidots
DEVICE_LABEL = "SymbIoT"    # Sesuaikan dengan nama perangkat di Ubidots

UBIDOTS_URL = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}/"
HEADERS = {
    "X-Auth-Token": UBIDOTS_TOKEN,
    "Content-Type": "application/json"
}

# MQTT Configuration
MQTT_CLIENT_ID = "sic6_stage2_rest"
MQTT_BROKER = "broker.emqx.io"
MQTT_TOPIC_SUB = "/UNI544/ADHYAKSAWARUNAPUTRO/data_sensor"

# Queue for processing frames in a separate thread
message_queue = queue.Queue()

# Shared variable for camera result
camera_result = None
camera_result_lock = threading.Lock()

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
    global camera_result
    while True:
        img_buffer = message_queue.get()
        result = camera.flame_detector(img_buffer)
        print("RESULT", result)
        with camera_result_lock:
            camera_result = result
            print("CAMERA RESULT", camera_result)

@app.route('/data', methods=['POST'])
def receive_data():
    try:
        data = request.json
        with camera_result_lock:
            current_result = camera_result
            print("CURRENT RESULT: ", current_result)
        data["status"] = current_result
        print("Data diterima dari ESP32:", data)
        
        # Kirim ke Ubidots
        response = requests.post(UBIDOTS_URL, json=data, headers=HEADERS)
        print("Respon dari Ubidots:", response.text)

        return jsonify({"message": "Data dikirim ke Ubidots", "ubidots_response": response.json()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def mqtt_main():
    mqtt = threading.Thread(target=mqtt_thread)
    processor = threading.Thread(target=process_frames)
    mqtt.start()
    processor.start()

if __name__ == '__main__':
    mqtt_main()  # Start MQTT threads first
    app.run(host="0.0.0.0", port=5000, debug=True)
