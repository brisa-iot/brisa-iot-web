import json
import threading
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient


class InfluxDBConnector:
    """
    Handles connection and queries to an InfluxDB database for sensor data.

    Methods:
        query(query_str): Executes a raw InfluxQL query.
        get_nodes_position(): Returns the last known GPS positions for all nodes.
        get_sensor_history(node_id, sensor, start, end): Returns historical sensor data for a node.
        get_last_sensor_values(node_id): Returns the latest value for each sensor for a node.
        show_databases(): Lists all databases.
        show_measurements(): Lists all measurements in the current database.
        close(): Closes the database connection.
    """
    def __init__(self, host='localhost', port=8086, username=None, password=None, database=None):
        """
        Initialize the InfluxDBConnector.

        Args:
            host (str): Hostname of the InfluxDB server.
            port (int): Port number.
            username (str): Username for authentication.
            password (str): Password for authentication.
            database (str): Database name to use.
        """
        self.client = InfluxDBClient(host=host, port=port, username=username, password=password, database=database)
        self.database = database
        if database:
            self.client.switch_database(database)

    def query(self, query_str):
        """
        Execute a raw InfluxQL query.

        Args:
            query_str (str): The query string.

        Returns:
            ResultSet: The result of the query, or None if error.
        """
        try:
            result = self.client.query(query_str)
            return result
        except Exception as e:
            print(f"Error executing query: {e}")
            return None
    
    def get_nodes_position(self):
        """
        Get the last known GPS positions (lat/lon) for all nodes.

        Returns:
            list: List of dicts with 'node_id', 'lat', and 'lon' for each node.
        """
        nodes_data = {}
        # Get last latitude for each node
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
        # Get last longitude for each node
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
        """
        Get historical sensor data for a node.

        Args:
            node_id (str|int): Node identifier.
            sensor (str): Sensor name.
            start (str): Optional start date/time (InfluxDB format).
            end (str): Optional end date/time (InfluxDB format).

        Returns:
            list: List of points (dicts) with 'value' and 'time'.
        """
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
        """
        Get the latest value for each sensor for a node.

        Args:
            node_id (str|int): Node identifier.

        Returns:
            list: List of dicts with 'sensor' and 'value'.
        """
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
        """
        List all databases.

        Returns:
            list: List of database dicts.
        """
        return self.client.get_list_database()

    def show_measurements(self):
        """
        List all measurements in the current database.

        Returns:
            list: List of measurement dicts.
        """
        if not self.database:
            print("No database selected")
            return None
        return self.client.get_list_measurements()

    def close(self):
        """
        Close the database connection.
        """
        self.client.close()


class MQTTConnector:
    """
    Handles MQTT connection, subscription, publishing, and relaying messages via SocketIO.

    Attributes:
        broker_address (str): MQTT broker address.
        port (int): MQTT broker port.
        client_id (str): MQTT client ID.
        client (mqtt.Client): Paho MQTT client instance.
        socketio: Flask-SocketIO instance (set externally).
    """
    def __init__(self, broker_address, port=1883, client_id=""):
        """
        Initialize the MQTTConnector.

        Args:
            broker_address (str): MQTT broker address.
            port (int): MQTT broker port.
            client_id (str): MQTT client ID.
        """
        self.broker_address = broker_address
        self.port = port
        self.client_id = client_id
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.socketio = None  # Placeholder for the socketio instance, to be set later

    def on_connect(self, client, userdata, flags, rc, properties):
        """
        Callback for when the client receives a CONNACK response from the server.

        Args:
            client: The client instance for this callback.
            userdata: The private user data as set in Client() or userdata_set().
            flags: Response flags sent by the broker.
            rc: The connection result.
            properties: MQTT v5.0 properties.
        """
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        """
        Callback for when a PUBLISH message is received from the server.

        Args:
            client: The client instance for this callback.
            userdata: The private user data as set in Client() or userdata_set().
            msg: An instance of MQTTMessage.
        """
        # print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")
        msg = json.loads(msg.payload.decode())
        self.socketio.emit("sensor_update", msg)

    def connect(self):
        """
        Connect to the MQTT broker.
        """
        try:
            print(f"Connecting to MQTT Broker at {self.broker_address}:{self.port}...")
            self.client.connect(self.broker_address, self.port)
        except Exception as e:
            print(f"Failed to connect to MQTT broker at {self.broker_address}:{self.port} - {e}")
            print("Retrying connection in 5 seconds...")
            threading.Timer(5, self.connect).start()

    def subscribe(self, topic):
        """
        Subscribe to a topic.

        Args:
            topic (str): The topic to subscribe to.
        """
        self.client.subscribe(topic)
        print(f"Subscribed to topic: {topic}")

    def publish(self, topic, message):
        """
        Publish a message to a topic.

        Args:
            topic (str): The topic to publish to.
            message (str): The message to publish.
        """
        self.client.publish(topic, message)
        print(f"Published message: {message} to topic: {topic}")

    def loop(self):
        """
        Start the MQTT network loop in a background thread.
        """
        self.client.loop_start()

    def stop_loop(self):
        """
        Stop the MQTT network loop.
        """
        self.client.loop_stop()
    
    def close(self):
        """
        Stop the network loop and disconnect from the MQTT broker.
        """
        self.client.loop_stop()
        self.client.disconnect()
        print("Disconnected from MQTT Broker.")


def validate_json_data(data):
    """
    Validate the uploaded configuration JSON data.

    Args:
        data (dict): The configuration data.

    Returns:
        tuple: (success (bool), message (str))
    """
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
