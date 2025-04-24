from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from firebase_admin import credentials, firestore, db, initialize_app
from google.cloud.firestore import FieldFilter
from datetime import datetime


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configurar Firebase
cred = credentials.Certificate("data/firebase_credentials.json")  # Asegúrate de tener este archivo
initialize_app(cred, {
    "databaseURL": "https://brisa-iot-default-rtdb.firebaseio.com/"  # Reemplaza con tu URL de Realtime Database
})

# Conectar a Firestore y Realtime Database
firestore_db = firestore.client()
realtime_db = db.reference("sensors")  # Nodo en Realtime Database

subscribed_sensors = set()  # Track which sensors have subscriptions

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/monitoring")
def index():
    return render_template("monitoring.html")

@app.route('/api/history/<sensor>', methods=['GET'])
def get_sensor_history(sensor):
    # Get the start and end dates from the query parameters
    start = request.args.get('start')  # format: YYYY-MM-DD
    end = request.args.get('end')      # format: YYYY-MM-DD

    if not start or not end:
        return jsonify({'error': 'Start and end date are required'}), 400

    # Convert the start and end dates to Firestore Timestamp objects
    start_date = datetime.strptime(start, '%Y-%m-%d').timestamp()
    # round end_date to the next day
    end_date = datetime.strptime(end, '%Y-%m-%d').timestamp() + 86400  # Add 24 hours in seconds

    # Query the Firestore collection for the sensor history within the date range
    docs = (
        firestore_db.collection("sensors")
        .where(filter=FieldFilter("sensor", "==", sensor))
        .where(filter=FieldFilter("timestamp", ">=", start_date))
        .where(filter=FieldFilter("timestamp", "<=", end_date))
        .order_by("timestamp", direction=firestore.Query.ASCENDING)
        .stream()
    )

    data = []
    for doc in docs:
        history_entry = doc.to_dict()
        data.append({
            'timestamp': history_entry['timestamp'],
            'value': history_entry['value']
        })
    if not data:
        return jsonify({'message': 'No data found for the given date range'}), 404

    return jsonify(data)

@socketio.on("connect")
def handle_connect():
    print("Cliente conectado")
    # Escuchar cambios en tiempo real desde Firebase Realtime Database
    def stream_handler(event):
        data = event.data
        # Eliminar campos no suscritos
        if data and isinstance(data, dict):
            for sensor_id in list(data.keys()):
                if sensor_id not in subscribed_sensors:
                    del data[sensor_id]
        if data:
            # Enviar datos a través de WebSocket
            socketio.emit("sensor_update", data)
    realtime_db.listen(stream_handler)

@app.route("/api/sensors")
def get_sensor_data():
    """Returns the latest sensor values from Realtime Database"""
    sensors = realtime_db.get()
    if sensors:
        return jsonify(sensors)
    return jsonify({"status": "No data available"})

@app.route("/api/subscribe/<sensor_id>", methods=["POST"])
def subscribe_sensor(sensor_id):
    """Adds a sensor to the subscription list"""
    subscribed_sensors.add(sensor_id)
    return {"status": f"Subscribed to {sensor_id}"}

@app.route("/api/unsubscribe/<sensor_id>", methods=["POST"])
def unsubscribe_sensor(sensor_id):
    """Removes a sensor from the subscription list"""
    subscribed_sensors.discard(sensor_id)
    return {"status": f"Unsubscribed from {sensor_id}"}

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
