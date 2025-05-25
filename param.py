import os
import json

CREDENTIALS_PATH = os.path.join("data", "firebase_credentials.json")
DATABASE_URL = ""
with open(os.path.join("data", "firebase_url.json"), "r") as file:
    DATABASE_URL = json.load(file)

BROKER_ADDRESS = "localhost"
BROKER_PORT = 1883
CLIENT_ID = "brisa-iot-web"
CONTROL_TOPIC = "brisa-iot/control"
SENSORS_TOPIC = "brisa-iot/sensors"