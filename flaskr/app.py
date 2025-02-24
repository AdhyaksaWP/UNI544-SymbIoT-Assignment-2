from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Token Ubidots
UBIDOTS_TOKEN = "BBUS-YRFncRgHQkiPjyr0qTLncnR6EKZ00F"  # Ganti dengan token API Ubidots
DEVICE_LABEL = "SymbIoT"    # Sesuaikan dengan nama perangkat di Ubidots

UBIDOTS_URL = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}/"
HEADERS = {
    "X-Auth-Token": UBIDOTS_TOKEN,
    "Content-Type": "application/json"
}

@app.route('/data', methods=['POST'])
def receive_data():
    try:
        data = request.json
        print("Data diterima dari ESP32:", data)

        # Kirim ke Ubidots
        response = requests.post(UBIDOTS_URL, json=data, headers=HEADERS)
        print("Respon dari Ubidots:", response.text)

        return jsonify({"message": "Data dikirim ke Ubidots", "ubidots_response": response.json()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
