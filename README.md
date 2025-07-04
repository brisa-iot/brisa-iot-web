# brisa-iot-web

This is a Flask web application for monitoring and controlling IoT sensors using InfluxDB and MQTT.

## Deployment

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (optional, see below for Windows)
- External instances of:
  - InfluxDB (for sensor data)
  - MQTT Broker (e.g., Mosquitto)
- [Python 3.11+](https://www.python.org/downloads/) (for running locally)

---

## 1. Configure `param.py`

The file [`param.py`](param.py) contains the configuration for connecting to your InfluxDB and MQTT broker.  
**By default, these values are hardcoded.**  
For Docker deployments, it is recommended to update `param.py` to read from environment variables, for example:

```python
import os

DB_HOST = os.environ.get("DB_HOST", "host.docker.internal")
DB_PORT = int(os.environ.get("DB_PORT", 8086))
DB_USERNAME = os.environ.get("DB_USERNAME", "admin")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "admin")
DB_NAME = os.environ.get("DB_NAME", "sensors_db")

BROKER_ADDRESS = os.environ.get("BROKER_ADDRESS", "host.docker.internal")
BROKER_PORT = int(os.environ.get("BROKER_PORT", 1883))
CLIENT_ID = os.environ.get("CLIENT_ID", "brisa-iot-web")
CONTROL_TOPIC = os.environ.get("CONTROL_TOPIC", "brisa-iot/control")
SENSORS_TOPIC = os.environ.get("SENSORS_TOPIC", "brisa-iot/sensors")
```

This allows you to configure the app using environment variables in your Docker Compose file or your local environment.

---

## 2. Running with Docker Compose (Recommended for Linux/macOS)

Edit [`docker-compose.yml`](docker-compose.yml) and set the environment variables to match your external InfluxDB and MQTT broker addresses and credentials.

Example:

```yaml
services:
  web:
    build: .
    command: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
    # for localhost access
    extra_hosts:
      - "host.docker.internal:host-gateway"
    ports:
      - "5000:5000"
    volumes:
      - .:/app
    environment:
      - DB_HOST=host.docker.internal
      - DB_PORT=8086
      - DB_USERNAME=admin
      - DB_PASSWORD=admin
      - DB_NAME=sensors_db
      - BROKER_ADDRESS=host.docker.internal
      - BROKER_PORT=1883
      - CLIENT_ID=brisa-iot-web
      - CONTROL_TOPIC=brisa-iot/control
      - SENSORS_TOPIC=brisa-iot/sensors
```

**Replace** `host.docker.internal` with the actual addresses of your external services if needed.

Then, build and start the web server:

```sh
docker compose up -d --build
```

The web application will be available at [http://localhost:5000](http://localhost:5000).

---

## 3. Running Locally with Python (Recommended for Windows)

> **Note:** On Windows, Docker networking can cause issues with MQTT and Flask-SocketIO.  
> If you experience problems, run the app directly with Python.

### Steps:

1. Install Python 3.11+
2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```
3. Set environment variables as needed (or edit `param.py` directly).
4. Run the app:
    ```sh
    python app.py
    ```
5. Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## 4. Access the Web Interface

- Home: `/home`
- Monitoring: `/monitoring`
- Update Parameters: `/update`
- Sensors: `/sensors`

---

## 5. Notes

- Make sure your external InfluxDB and MQTT broker are accessible from your machine or container.
- If running everything on the same host, you can use `host.docker.internal` as the host address for local development (on Docker for Linux/macOS).
- On Windows, you may need to use `localhost` or your actual IP address for broker/database connections.

---

## Project Structure

- `app.py` - Main Flask application
- `param.py` - Configuration for database and MQTT
- `utils.py` - Utility functions and connectors
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker build instructions
- `docker-compose.yml` - Docker Compose configuration
- `templates/` - HTML templates
- `static/` - Static files (CSS, JS, images)

---

## Troubleshooting

- If the web server cannot connect to the database or broker, check your network settings and environment variables.
- Logs can be viewed with:

  ```sh
  docker compose logs web
  ```
