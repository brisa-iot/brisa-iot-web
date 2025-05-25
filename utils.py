import json
import time
import threading
from datetime import datetime
import paho.mqtt.client as mqtt
from google.cloud.firestore import FieldFilter
from firebase_admin import credentials, firestore, initialize_app



class DBManager:
    def __init__(self, credentials_path, database_url):
        # Initialize Firebase
        cred = credentials.Certificate(credentials_path)
        initialize_app(cred, database_url)

        # Connect to Firestore
        self.firestore_db = firestore.client()
        self.firestore_collection = self.firestore_db.collection("sensors")

    def save_to_firestore(self, data):
        for key, value in data.items():
            if key == "timestamp":
                continue
            self.firestore_collection.add({
                "sensor": key,
                "value": value,
                "timestamp": time.time()  # TODO: Use the timestamp from the data
            })
    
    def get_sensor_data_from_db(self, sensor, start_date, end_date):
        # Convert the start and end dates to Firestore Timestamp objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d').timestamp()
        # round end_date to the next day
        end_date = datetime.strptime(end_date, '%Y-%m-%d').timestamp() + 86400  # Add 24 hours in seconds
        # Query the Firestore collection for the sensor history within the date range
        docs = (
            self.firestore_db.collection("sensors")
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
        return data

    def get_last_sensor_data(self):
        # Get the last sensor data from Firestore
        docs = self.firestore_collection.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1).stream()
        data = {}
        for doc in docs:
            data = doc.to_dict()
        print(data)
        return data


class MQTTConnector:
    def __init__(self, broker_address, port=1883, client_id=""):
        self.broker_address = broker_address
        self.port = port
        self.client_id = client_id
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.db_manager = None  # Placeholder for the interface, to be set later
        self.socketio = None  # Placeholder for the socketio instance, to be set later

    def on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")
        msg = json.loads(msg.payload.decode())
        self.socketio.emit("sensor_update", msg)
        self.db_manager.save_to_firestore(msg)

    def connect(self):
        self.client.connect(self.broker_address, self.port)

    def subscribe(self, topic):
        self.client.subscribe(topic)
        print(f"Subscribed to topic: {topic}")

    def publish(self, topic, message):
        self.client.publish(topic, message)
        print(f"Published message: {message} to topic: {topic}")

    def loop(self):
        t = threading.Thread(target=self.client.loop_forever)
        t.daemon = True
        t.start()
    def stop_loop(self):
        self.client.loop_stop()
    
    def close(self):
        self.client.loop_stop()
        self.client.disconnect()
        print("Disconnected from MQTT Broker.")
