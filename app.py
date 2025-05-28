import json
from flask_socketio import SocketIO 
from flask import Flask, render_template, request, jsonify
from utils import InfluxDBConnector, MQTTConnector, validate_json_data
from param import (DB_HOST, DB_PORT, DB_USERNAME, DB_PASSWORD, DB_NAME, BROKER_ADDRESS,
                   BROKER_PORT, CLIENT_ID, CONTROL_TOPIC, SENSORS_TOPIC)


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

db_connector = InfluxDBConnector(
    host=DB_HOST,
    port=DB_PORT,
    username=DB_USERNAME,
    password=DB_PASSWORD,
    database=DB_NAME
)

mqtt_connector = MQTTConnector(BROKER_ADDRESS, BROKER_PORT, CLIENT_ID)
mqtt_connector.socketio = socketio
mqtt_connector.connect()
mqtt_connector.subscribe(SENSORS_TOPIC)

node_id = ""  # Placeholder for node_id, to be set later

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/monitoring")
def index():
    node_id = ""
    return render_template("monitoring.html")

@app.route("/update")
def update():
    return render_template("update.html")

@app.route("/sensors")
def sensors():
    return render_template("sensors.html")

@app.route("/api/nodes-data")
def get_nodes_data():
    nodes_data = db_connector.get_nodes_position()
    if not nodes_data:
        return jsonify({"error": "No nodes data available"}), 404
    return jsonify(nodes_data)

@app.route("/api/node/<id>", methods=["POST"])
def change_node_id(id):
    global node_id
    node_id = id
    if not node_id:
        return jsonify({"error": "Node ID is required"}), 400
    return jsonify({"message": f"Node ID {node_id} received!"}), 200 

@app.route("/update-config", methods=["POST"])
def update_config_route():
    """
    Handles the submission from the update_config_form.html.
    Processes either an uploaded JSON file or JSON text input.
    """
    config_data = None
    error_message = None
    input_method = request.form.get("inputType")

    if input_method == "file":
        if 'file' not in request.files:
            error_message = "No file part in the request."
        else:
            file = request.files['file']
            if file.filename == '':
                error_message = "No file selected for uploading."
            elif file and file.filename.endswith('.json'):
                try:
                    json_string = file.read().decode('utf-8')
                    if not json_string.strip():
                        error_message = "Uploaded JSON file is empty."
                    else:
                        config_data = json.loads(json_string)
                except json.JSONDecodeError:
                    error_message = "Invalid JSON format in the uploaded file."
                except UnicodeDecodeError:
                    error_message = "Uploaded file is not valid UTF-8 encoded text."
                except Exception as e:
                    error_message = f"Error processing file: {str(e)}"
            else:
                error_message = "Invalid file type. Please upload a .json file."

    elif input_method == "text":
        json_text = request.form.get("jsonText", "").strip()
        if not json_text:
            error_message = "No JSON text provided."
        else:
            try:
                config_data = json.loads(json_text)
            except json.JSONDecodeError:
                error_message = "Invalid JSON format in the text input."
            except Exception as e:
                error_message = f"Error processing JSON text: {str(e)}"
    else:
        error_message = "Invalid input type selected."

    if error_message:
        # Using flash for messages, assuming your template is set up for it
        # Or pass directly via render_template
        # flash(error_message, 'error')
        # return redirect(url_for('show_update_config_form'))
        return render_template("update.html", message=error_message, success=False)

    if config_data is not None:
        success, message = validate_json_data(config_data)
        if success:
            mqtt_connector.publish(CONTROL_TOPIC, json.dumps(config_data))
        
        return render_template("update.html", message=message, success=success)
    else:
        # This case should ideally be caught by earlier checks, but as a fallback:
        # flash("No configuration data was processed.", 'error')
        return render_template("update.html", message="No configuration data was processed.", success=False)

@app.route('/api/history/<sensor>', methods=['GET'])
def get_sensor_history(sensor):
    # Get the start and end dates from the query parameters
    start = request.args.get('start')  # format: YYYY-MM-DD
    end = request.args.get('end')      # format: YYYY-MM-DD

    if not start or not end:
        return jsonify({'error': 'Start and end date are required'}), 400

    data = db_connector.get_sensor_history(
        node_id=node_id,
        sensor=sensor,
        start=start,
        end=end
    )
    print(node_id, sensor, start, end, data)
    if not data:
        return jsonify({'message': 'No data found for the given date range'}), 404

    return jsonify(data)

@app.route("/api/sensors")
def get_sensor_data():
    """Returns the latest sensor values from Database"""
    sensors = db_connector.get_last_sensor_values(node_id)
    data = {"node_id": node_id, "sensors": sensors} if sensors else {}
    if data:
        return jsonify(data)
    return jsonify({"status": "No data available"})

@socketio.on("connect")
def handle_connect():
    print("Cliente conectado")


if __name__ == "__main__":
    try:
        mqtt_connector.loop()
        socketio.run(app, debug=False, host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        print("Exiting...")
        mqtt_connector.close()
