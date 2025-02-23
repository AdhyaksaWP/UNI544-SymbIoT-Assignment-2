from flask import Flask, request, jsonify
from .db import send_data, get_data

app = Flask(__name__)

@app.route("/sensors_data", methods=["GET", "POST"])
def sensor_handler():
    if request.method == "POST":
        res = send_data()
        
    elif request.method == "GET":
        res = get_data()
    
    return jsonify(res)

if __name__=='__main__': 
    app.run(debug=True)