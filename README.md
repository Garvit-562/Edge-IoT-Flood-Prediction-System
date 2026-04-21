# ⚙️ SETUP & EXECUTION GUIDE
## Flood Prediction Edge AI System

---

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9 – 3.11** (CatBoost and scikit-learn 1.3.x have limited support on 3.12+)
- **pip** (comes with Python)
- A modern browser — Chrome or Edge recommended (Firefox has WebAssembly thread restrictions)
- Both machines (edge device and cloud server) must be on the **same local network** for cloud comparison to work

---

## Step 1 — Clone or Download the Project

```bash
git clone https://github.com/your-username/flood-edge-ai.git
cd flood-edge-ai
```

Or download and unzip the project folder. Make sure the following files are present:

```
flood-edge-ai/
├── index.html
├── model.onnx
├── app.py
├── high_accuracy_flood_model.pkl
├── convert.py
├── requirements-1.txt
└── flood-edge-ai-dbacc0d28855.json
```

---

## Step 2 — Set Up the Python Environment

It is recommended to use a virtual environment to avoid dependency conflicts.

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements-1.txt
```

Then install the web server dependencies (not in requirements-1.txt):

```bash
pip install flask flask-cors firebase-admin catboost
```

> **Note:** `catboost` is required only if you need to run `convert.py` to regenerate `model.onnx`. For just running the Flask server, it is not needed.

---

## Step 3 — (Optional) Regenerate the ONNX Model

This step is only needed if `model.onnx` is missing or you have retrained the model.

```bash
python convert.py
```

Expected output:
```
Loading High-Accuracy CatBoost model...
Exporting to ONNX Edge format...
✅ Success! 'model.onnx' has been created.
```

This converts `high_accuracy_flood_model.pkl` into `model.onnx` for use in the browser.

---

## Step 4 — Start the Cloud Inference Server

The Flask server loads the `.pkl` model and handles prediction and latency logging requests.

```bash
python app.py
```

Expected output:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

Find your machine's local IP address (you'll need this for the frontend):

```bash
# Windows
ipconfig

# macOS/Linux
ifconfig
# or
ip addr show
```

Look for your IPv4 address, e.g. `10.245.125.60`.

> **Keep this terminal open.** The server must stay running for cloud inference and Firebase logging to work.

---

## Step 5 — Update the Cloud Server IP in the Frontend

Open `index.html` in a text editor and find line ~354. Update both fetch URLs to match your server's IP:

```javascript
// Change this IP to your Flask server's local IP address
fetch("http://YOUR_SERVER_IP:5000/predict", {
```

```javascript
fetch("http://YOUR_SERVER_IP:5000/log_latency", {
```

**Example:** If your server IP is `10.245.125.60`, both URLs should read:
```
http://10.245.125.60:5000/predict
http://10.245.125.60:5000/log_latency
```

---

## Step 6 — Start the Edge Web Server

The frontend must be served over HTTP (not opened directly as a file) because ONNX Runtime Web uses WebAssembly, which browsers block from `file://` paths.

From the **project folder** (same folder as `index.html` and `model.onnx`), run:

```bash
python -m http.server 8000
```

---

## Step 7 — Open the Dashboard

On any device connected to the same network, open a browser and go to:

```
http://localhost:8000/index.html
```

Or to access from another device (e.g., a phone):

```
http://YOUR_EDGE_DEVICE_IP:8000/index.html
```

The page will show a loading spinner while the ONNX model initializes, then display the live dashboard.

---

## Step 8 — Using the Dashboard

- Adjust the **9 environmental sliders** (Monsoon Intensity, Drainage, River Management, etc.)
- Prediction updates **instantly** via Edge inference (ONNX in browser)
- Simultaneously, a cloud request is sent to the Flask server
- The bottom chip displays real-time latency:

```
⚡ Edge: 2.45 ms  |  ☁️ Cloud: 87.30 ms
```

- Results are color-coded:
  - 🟢 **LOW RISK** — Safe
  - 🟡 **HIGH RISK** — Elevated
  - 🔴 **ALARMING RISK** — Critical

---

## Step 9 — Viewing Firebase Logs

All predictions and latency data are logged to Firebase Realtime Database.

1. Go to [https://console.firebase.google.com](https://console.firebase.google.com)
2. Open the **flood-edge-ai** project
3. Navigate to **Realtime Database → logs**

Each entry contains:
```json
{
  "edge_latency": "2.45",
  "cloud_latency": "87.30",
  "prediction": "Low",
  "timestamp": "2025-04-21 10:30:00"
}
```

---

## API Endpoints Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /` | GET | Health check — returns `"Server is running"` |
| `/predict` | POST | Runs cloud inference on 20 features, returns prediction + latency |
| `/log_latency` | POST | Logs edge latency, cloud latency, and prediction to Firebase |

### `/predict` — Request Body
```json
{
  "features": [7, 5, 6, 5, 5, 5, 8, 6, 5, 5, 5, 6, 7, 5, 6, 5, 5, 5, 5, 5],
  "edge_latency": "2.45"
}
```

### `/predict` — Response
```json
{
  "prediction": "High",
  "cloud_latency": 3.21
}
```

---

## Troubleshooting

**"ERROR LOADING MODEL" on the browser page**
- Confirm `model.onnx` is in the same folder as `index.html`
- Confirm you started the server with `python -m http.server 8000` (not by opening the file directly)
- Try Chrome or Edge browser instead of Firefox

**"Cloud: --" latency stays blank**
- Check the IP in `index.html` matches the Flask server's actual IP
- Confirm `python app.py` is running and shows no errors
- Both devices must be on the same Wi-Fi/network
- Check browser console (`F12 → Console`) for CORS or connection errors

**`ModuleNotFoundError` when starting `app.py`**
- Run `pip install flask flask-cors firebase-admin joblib numpy`
- Make sure your virtual environment is activated

**Firebase permission errors**
- Confirm `flood-edge-ai-dbacc0d28855.json` is in the same folder as `app.py`
- Check Firebase Console → Realtime Database → Rules are set to allow writes for your service account

**Port 5000 already in use**
```bash
# Change the port in app.py (last line):
app.run(host='0.0.0.0', port=5001, debug=True)
# Then update the fetch URLs in index.html to use :5001
```

---

## Project Flow Summary

```
Browser opens index.html
        │
        ├──► Loads model.onnx via ONNX Runtime Web
        │
User moves slider
        │
        ├──► ⚡ Edge inference runs in WASM (< 5ms typical)
        │         └── Updates UI with risk level + edge latency
        │
        └──► ☁️ POST to Flask /predict
                  └── Cloud inference on .pkl model
                  └── Returns prediction + server latency
                  └── POST to /log_latency → Firebase
                  └── Updates UI with cloud latency chip
```