import camera
import network
import time
import ujson
from umqtt.simple import MQTTClient

# Konfigurasi WiFi
WIFI_SSID = "UGM eduroam"
WIFI_PASSWORD = "moyf7667"

# Konfigurasi MQTT
MQTT_CLIENT_ID = "sic6_stage2"
MQTT_BROKER = "broker.emqx.io"
MQTT_TOPIC_SUB = "/UNI544/ADHYAKSAWARUNAPUTRO/aktuasi_kamera"
MQTT_TOPIC_PUB = "/UNI544/ADHYAKSAWARUNAPUTRO/data_sensor"

class ESP32CamController:
    def __init__(self):
        self.client = MQTTClient(
            client_id=MQTT_CLIENT_ID,
            server=MQTT_BROKER,
            port=1883
        )
        self.last_message = None
        self.camera_active = True
        
        # Inisialisasi kamera
        try:
            camera.init(0, format=camera.JPEG)
            camera.framesize(camera.FRAME_QQVGA)
            camera.quality(10) 
            print("Camera initialized successfully")
        except Exception as e:
            print(f"Camera init failed: {e}")

    def wifi_connect(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        print("Connecting to WiFi", end="")
        for _ in range(20):
            if wlan.isconnected():
                break
            print(".", end="")
            time.sleep(1)
        
        if wlan.isconnected():
            print("\nWiFi Connected!")
            print("IP Address:", wlan.ifconfig()[0])
            return True
        else:
            print("\nFailed to connect to WiFi")
            return False

    def mqtt_connect(self):
        try:
            self.client.connect()
            self.client.set_callback(self.mqtt_callback)
            self.client.subscribe(MQTT_TOPIC_SUB)
            print("Connected to MQTT Broker")
            return True
        except Exception as e:
            print(f"MQTT Connection Error: {e}")
            return False

    def mqtt_callback(self, topic, msg):
        try:
            self.last_message = ujson.loads(msg)
            print("Received message:", self.last_message)
            
            if self.last_message.get('status') == 'off':
                self.camera_active = False
        except Exception as e:
            print("Error processing message:", e)

    def capture_image(self):
        try:
            buf = camera.capture()
            return buf
        except Exception as e:
            print("Error capturing image:", e)
            return None

    def run(self):
        if not self.wifi_connect():
            return
            
        if not self.mqtt_connect():
            return

        while self.camera_active:
            try:
                img_buffer = self.capture_image()
                
                # Kirim raw buffer secara langsung ke topic
                if img_buffer:
                    self.client.publish(MQTT_TOPIC_PUB, img_buffer)
                    print("Image published")
                    time.sleep(1)
                
                # Periksa pesan masuk
                self.client.check_msg()
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print("Error in main loop:", e)
                time.sleep(5)

        # Cleanup
        #camera.deinit()
        #self.client.disconnect()
        #print("System shutdown")

if __name__ == "__main__":
    esp32cam = ESP32CamController()
    esp32cam.run()