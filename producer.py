import firebase_admin
from firebase_admin import credentials, db, firestore
import random
import time

# Initialize Firebase
cred = credentials.Certificate("data/firebase_credentials.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://brisa-iot-default-rtdb.firebaseio.com/"
})

# Connect to Realtime Database
realtime_db = db.reference("sensors")

# Connect to Firestore
firestore_db = firestore.client()
firestore_collection = firestore_db.collection("sensors")

def generate_data():
    return {
        "temperature": round(random.uniform(5, 35), 2),
        "humidity": round(random.uniform(30, 90), 2),
        "pressure": round(random.uniform(950, 1050), 2),
        "wind_magnitude": round(random.uniform(0, 20), 2),
        "wind_direction": round(random.uniform(0, 360), 2),
        "pH": round(random.uniform(6, 9), 2),
        "conductivity": round(random.uniform(100, 500), 2),
        "water_temperature": round(random.uniform(5, 30), 2),
        "oxygen": round(random.uniform(5, 12), 2),
        "gps": {
            "lat": round(random.uniform(-90, 90), 6),
            "lon": round(random.uniform(-180, 180), 6)
        },
        "imu": {
            "ax": round(random.uniform(-10, 10), 2),
            "ay": round(random.uniform(-10, 10), 2),
            "az": round(random.uniform(-10, 10), 2)
        },
        "timestamp": time.time()
    }

while True:
    data = generate_data()

    # Save to Realtime Database
    realtime_db.set(data)  

    # Save to Firestore for historical data
    for key, value in data.items():
        if key == "timestamp":
            continue
        firestore_collection.add({
            "sensor": key,
            "value": value,
            "timestamp": data["timestamp"]
        })

    print(f"\nData sended:")
    [print(f"{key}: {value}") for key, value in data.items()]
    time.sleep(0.1)
