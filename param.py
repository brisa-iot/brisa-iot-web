import os

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", 8086))
DB_USERNAME = os.environ.get("DB_USERNAME", "admin")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "admin")
DB_NAME = os.environ.get("DB_NAME", "sensors_db")

BROKER_ADDRESS = os.environ.get("BROKER_ADDRESS", "localhost")
BROKER_PORT = int(os.environ.get("BROKER_PORT", 1883))
CLIENT_ID = os.environ.get("CLIENT_ID", "brisa-iot-web")
CONTROL_TOPIC = os.environ.get("CONTROL_TOPIC", "brisa-iot/control")
SENSORS_TOPIC = os.environ.get("SENSORS_TOPIC", "brisa-iot/sensors")
