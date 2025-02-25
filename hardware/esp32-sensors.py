import network
import urequests
import machine
import dht
import time
import json

# WiFi Config
SSID = "UGM eduroam"
PASSWORD = "moyf7667"

# Koneksi WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    print("Menghubungkan ke WiFi...")
    time.sleep(1)

print("Terhubung ke WiFi:", wlan.ifconfig())

# Konfigurasi Sensor
DHT_PIN = 32
MQ135_PIN = 34
dht_sensor = dht.DHT11(machine.Pin(DHT_PIN))
mq135_sensor = machine.ADC(machine.Pin(MQ135_PIN))
mq135_sensor.atten(machine.ADC.ATTN_11DB)

# Alamat Flask API
FLASK_SERVER = "http://192.168.11.226:5000/data"  

while True:
    try:
        dht_sensor.measure()
        suhu = dht_sensor.temperature()
        kelembaban = dht_sensor.humidity()
        nilai_mq135 = mq135_sensor.read()

        data = {
            "suhu": suhu,
            "kelembaban": kelembaban,
            "mq135": nilai_mq135
        }

        print("Mengirim data:", data)
        response = urequests.post(FLASK_SERVER, json=data)
        print("Respon dari server:", response.text)
        response.close()

    except Exception as e:
        print("Error:", str(e))

    time.sleep(3)