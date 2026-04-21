from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import joblib
import numpy as np

import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("flood-edge-ai-dbacc0d28855.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://flood-edge-ai-default-rtdb.firebaseio.com/'
})

app = Flask(__name__)
CORS(app)

# Load model once
model = joblib.load("high_accuracy_flood_model.pkl")

@app.route('/')
def home():
    return "Server is running"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    features = data.get("features")

    # Convert to correct format
    input_data = np.array(features).reshape(1, -1)

    # Measure latency
    start = time.perf_counter()
    prediction = model.predict(input_data)
    # time.sleep(0.1)
    # time.sleep(0.05)
    end = time.perf_counter()

    latency = (end - start) * 1000  # in ms

    result = prediction[0]

    # ref = db.reference("logs")

    # ref.push({
    #     "edge_latency": request.json.get("edge_latency", 0),
    #     "cloud_latency": request.json.get("cloud_latency", 0),
    #     "prediction": str(result),
    #     "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    # })

    print("Prediction:", result, "| Latency:", latency)

    return jsonify({
        "prediction": str(result),
        "cloud_latency": round(latency, 2)
    })

@app.route('/log_latency', methods=['POST'])
def log_latency():
    data = request.get_json()

    ref = db.reference("logs")

    ref.push({
        "edge_latency": data.get("edge_latency"),
        "cloud_latency": data.get("cloud_latency"),
        "prediction": data.get("prediction"),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })

    return jsonify({"status": "logged"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)