import os
import json


DB_HOST = "localhost"
DB_PORT = 8086
DB_USERNAME = "admin"
DB_PASSWORD = "admin"
DB_NAME = "sensors_db"

BROKER_ADDRESS = "localhost"
BROKER_PORT = 1883
CLIENT_ID = "brisa-iot-web"
CONTROL_TOPIC = "brisa-iot/control"
SENSORS_TOPIC = "brisa-iot/sensors"