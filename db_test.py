from firebase_admin import credentials, firestore, db, initialize_app
from google.cloud.firestore import FieldFilter
from datetime import datetime

# Configurar Firebase
cred = credentials.Certificate("data/firebase_credentials.json")  # Asegúrate de tener este archivo
initialize_app(cred, {
    "databaseURL": "https://brisa-iot-default-rtdb.firebaseio.com/"  # Reemplaza con tu URL de Realtime Database
})

# Conectar a Firestore y Realtime Database
firestore_db = firestore.client()

def get_sensor_history(sensor, start, end):

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

    print(docs)
    data = []
    print(f"Sensor: {sensor}, Start: {start_date}, End: {end_date}")
    for doc in docs:
        history_entry = doc.to_dict()
        data.append({
            'timestamp': history_entry['timestamp'],
            'value': history_entry['value']
        })

    return data


print(get_sensor_history("temperature", "2025-04-01", "2025-04-06"))