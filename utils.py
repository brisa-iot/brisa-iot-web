from google.cloud.firestore import FieldFilter
from firebase_admin import credentials, firestore, db, initialize_app
from datetime import datetime


def get_sensor_data_from_db(firestore_db, sensor, start_date, end_date):
    # Convert the start and end dates to Firestore Timestamp objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d').timestamp()
    # round end_date to the next day
    end_date = datetime.strptime(end_date, '%Y-%m-%d').timestamp() + 86400  # Add 24 hours in seconds

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
    
    return data