from flask_socketio import SocketIO 
from flask import Flask, render_template, request, jsonify
from utils import DBManager, MQTTConnector
from param import (CREDENTIALS_PATH, DATABASE_URL, BROKER_ADDRESS, BROKER_PORT,
                  CLIENT_ID, CONTROL_TOPIC, SENSORS_TOPIC)


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

db_manager = DBManager(CREDENTIALS_PATH, DATABASE_URL)
mqtt_connector = MQTTConnector(BROKER_ADDRESS, BROKER_PORT, CLIENT_ID)
mqtt_connector.db_manager = db_manager
mqtt_connector.socketio = socketio
mqtt_connector.connect()
mqtt_connector.subscribe(SENSORS_TOPIC)


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

    data = db_manager.get_sensor_data_from_db(sensor, start, end)

    if not data:
        return jsonify({'message': 'No data found for the given date range'}), 404

    return jsonify(data)

@socketio.on("connect")
def handle_connect():
    print("Cliente conectado")

@app.route("/api/sensors")
def get_sensor_data():
    """Returns the latest sensor values from Realtime Database"""
    sensors = db_manager.get_last_sensor_data()
    if sensors:
        return jsonify(sensors)
    return jsonify({"status": "No data available"})


if __name__ == "__main__":
    try:
        mqtt_connector.loop()
        socketio.run(app, debug=False, host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        print("Exiting...")
        mqtt_connector.close()
