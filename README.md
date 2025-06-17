# brisa-iot-web

This is a Flask web application for monitoring and controlling IoT sensors using InfluxDB and MQTT.

## Deployment

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- External instances of:
  - InfluxDB (for sensor data)
  - MQTT Broker (e.g., Mosquitto)

### 1. Configure `param.py`

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

This allows you to configure the app using environment variables in your Docker Compose file.

### 2. Build and Run with Docker Compose

Edit [`docker-compose.yml`](docker-compose.yml) and set the environment variables to match your external InfluxDB and MQTT broker addresses and credentials.

Example:

```yaml
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DB_HOST=your_external_db_host
      - DB_PORT=8086
      - DB_USERNAME=your_username
      - DB_PASSWORD=your_password
      - DB_NAME=your_database
      - BROKER_ADDRESS=your_external_broker_host
      - BROKER_PORT=1883
      - CLIENT_ID=your_client_id
      - CONTROL_TOPIC=control_topic
      - SENSORS_TOPIC=sensors_topic
```

**Replace** `your_external_db_host` and `your_external_broker_host` with the actual addresses of your external services.

Then, build and start the web server:

```sh
docker compose up -d --build
```

The web application will be available at [http://localhost:5000](http://localhost:5000).

### 3. Access the Web Interface

- Home: `/home`
- Monitoring: `/monitoring`
- Update Parameters: `/update`
- Sensors: `/sensors`

### 4. Notes

- Make sure your external InfluxDB and MQTT broker are accessible from the Docker container.
- If running everything on the same host, you can use `host.docker.internal` as the host address for local development.

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

---

## License

MIT License