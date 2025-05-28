import json
import threading
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient


class InfluxDBConnector:
    def __init__(self, host='localhost', port=8086, username=None, password=None, database=None):
        self.client = InfluxDBClient(host=host, port=port, username=username, password=password, database=database)
        self.database = database
        if database:
            self.client.switch_database(database)

    def query(self, query_str):
        try:
            result = self.client.query(query_str)
            return result
        except Exception as e:
            print(f"Error executing query: {e}")
            return None
    
    def get_nodes_position(self):
        nodes_data = {}
        query = 'SELECT LAST("value") FROM "mqtt_consumer" WHERE "sensor" = \'gps_lat\' GROUP BY "node_id"'
        result = self.query(query)
        if result:
            for measurement, points in result.items():
                node_id = measurement[1]["node_id"]
                for point in points:
                    if node_id:
                        nodes_data[node_id] = {
                            'lat': point.get('last'),
                            'lon': None  # Placeholder for longitude
                        }
        query = 'SELECT LAST("value") FROM "mqtt_consumer" WHERE "sensor" = \'gps_lon\' GROUP BY "node_id"'
        result = self.query(query)
        if result:
            for measurement, points in result.items():
                node_id = measurement[1]["node_id"]
                for point in points:
                    if node_id and node_id in nodes_data:
                        nodes_data[node_id]['lon'] = point.get('last')
        
        data = []
        for node_id, node_data in nodes_data.items():
            if node_data['lat'] is not None and node_data['lon'] is not None:
                data.append({
                    'node_id': node_id,
                    'lat': node_data['lat'],
                    'lon': node_data['lon']
                })
        return data

    def get_sensor_history(self, node_id, sensor, start=None, end=None):
        if not self.database:
            print("No database selected")
            return None
        query = f'SELECT "value" FROM "mqtt_consumer" WHERE "node_id" = \'{node_id}\' AND "sensor" = \'{sensor}\''
        if start:
            query += f' AND time >= \'{start}\''
        if end:
            query += f' AND time <= \'{end}\''
        query += ' ORDER BY time DESC LIMIT 1000'
        result = self.query(query)
        return list(result.get_points())

    def get_last_sensor_values(self, node_id):
        if not self.database:
            print("No database selected")
            return None
        query = f'SELECT LAST("value") FROM "mqtt_consumer" WHERE "node_id" = \'{node_id}\' GROUP BY "sensor"'
        result = self.query(query)
        last_values = []
        for serie in result.raw.get('series', []):
            sensor_name = serie['tags'].get('sensor', 'unknown')
            last_value = serie['values'][0][1]  # el valor está en la segunda posición
            last_values.append({
                'sensor': sensor_name,
                'value': last_value
            })
        print(f"Last values for node {node_id}: {last_values}")
        return last_values

    def show_databases(self):
        return self.client.get_list_database()

    def show_measurements(self):
        if not self.database:
            print("No database selected")
            return None
        return self.client.get_list_measurements()

    def close(self):
        self.client.close()


class MQTTConnector:
    def __init__(self, broker_address, port=1883, client_id=""):
        self.broker_address = broker_address
        self.port = port
        self.client_id = client_id
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
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


def validate_json_data(data):
    success = True
    message = "Configuration updated successfully!"
    if "node_id" not in data:
        message = "Invalid data format. Must contain 'node_id'."
        success = False
    return success, message


if __name__ == "__main__":
    influx = InfluxDBConnector(host='localhost', port=8086, username='admin', password='admin', database='sensors_db')

    # Mostrar bases de datos
    # print("Databases:", influx.show_databases())

    # Mostrar mediciones
    # print("Measurements:", influx.show_measurements())

    # print(influx.get_nodes_position())

    # print(influx.get_sensor_history(1, 'temperature', start='2025-05-26', end='2025-05-28'))

    # print(influx.get_last_sensor_values(1))

    query = 'SELECT LAST("value") FROM "mqtt_consumer" WHERE "sensor" = \'gps_lon\' GROUP BY "node_id"'
    result = influx.query(query)
    print("Query Result:", result)
    if result:
        for measurement, points in result.items():
            node_id = measurement[1]["node_id"]
            for point in points:
                if node_id:
                    print(f"Node ID: {node_id}, Value: {point.get('last')}")


    influx.close()