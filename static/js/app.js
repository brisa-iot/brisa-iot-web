const socket = io.connect('http://localhost:5000');

const sensors = [
    "conductivity",
    // "wind_direction",
    "gps",
    "humidity",
    "imu", 
    "wind_magnitude",
    "oxygen",
    "pH",
    "pressure",
    "temperature", 
    "water_temperature"
];

const titles = {
    "conductivity": "Conductivity",
    "wind_direction": "Wind Direction",
    "gps": "GPS",
    "humidity": "Humidity",
    "imu": "IMU",
    "wind_magnitude": "Wind Magnitude",
    "oxygen": "Oxygen",
    "pH": "pH Level",
    "pressure": "Pressure",
    "temperature": "Temperature",
    "water_temperature": "Water Temperature"
}

const units = {
    "conductivity": "µS/cm",
    "wind_direction": "°",
    "gps": "Latitude/Longitude",
    "humidity": "%",
    "imu": "m/s²",
    "wind_magnitude": "m/s",
    "oxygen": "mg/L",
    "pH": "pH",
    "pressure": "hPa",
    "temperature": "°C",
    "water_temperature": "°C"
}

// Create a WebSocket connection
window.onload = () => {
    const container = document.getElementById('sensor-cards-container');

    sensors.forEach(sensor => {
        const card = document.createElement('div');
        card.classList.add('sensor-card');
        card.id = `${sensor}-card`;
        // card.onclick = () => showModal(sensor);

        card.innerHTML = `
            <div class="sensor-icon" onclick="showModal('${sensor}')">
                <img src="static/img/svg/${sensor}.svg" class="icon" alt="${sensor} Icon">
                <div class="sensor-info">
                    <h3>${titles[sensor]}</h3>
                    <p class="value" id="${sensor}-value">Loading...</p>
                    <p class="unit">${units[sensor]}</p>
                </div>
            </div>
            <div class="switch-container">
                <label class="switch">
                    <input type="checkbox" id="${sensor}-switch" onchange="toggleSubscription('${sensor}')">
                    <span class="slider"></span>
                </label>
            </div>
        `;

        container.appendChild(card);
    });

    fetchSensorData();
};


// Unsubscribe from all sensors when the page is closed or refreshed
window.onbeforeunload = () => {
    sensors.forEach(sensor => {
        const url = `/api/unsubscribe/${sensor}`;
        const data = JSON.stringify({ sensor });
        navigator.sendBeacon(url, data);
    });
};

window.addEventListener("unload", () => {
    sensors.forEach(sensor => {
        const url = `/api/unsubscribe/${sensor}`;
        const data = JSON.stringify({ sensor });
        navigator.sendBeacon(url, data);
    });
});

// Fetch initial sensor data
function fetchSensorData() {
    fetch('/api/sensors')
        .then(response => response.json())
        .then(data => {
            sensors.forEach(sensor => {
                const valueElement = document.getElementById(`${sensor}-value`);
                if (data[sensor]) {
                    if (sensor === 'gps') {
                        valueElement.innerText = `Lat: ${data[sensor].lat}, Lon: ${data[sensor].lon}`;
                    }
                    else if (sensor === 'imu') {
                        valueElement.innerText = `X: ${data[sensor].ax}, Y: ${data[sensor].ay}, Z: ${data[sensor].az}`;
                    } else {
                        valueElement.innerText = `${data[sensor]}`;
                    }
                } else {
                    valueElement.innerText = 'N/A';
                }
            });
        });
}

// Toggle subscription for sensor updates
function toggleSubscription(sensorId) {
    const switchElement = document.getElementById(`${sensorId}-switch`);
    
    if (switchElement.checked) {
        fetch(`/api/subscribe/${sensorId}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => console.log(data.status))
            .catch(error => console.error('Subscription error:', error));
    } else {
        fetch(`/api/unsubscribe/${sensorId}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => console.log(data.status))
            .catch(error => console.error('Unsubscription error:', error));
    }
}

// WebSocket listener for sensor updates
socket.on('sensor_update', (data) => {
    console.log('Sensor update received:', data);
    for (const [sensor, value] of Object.entries(data)) {
        const valueElement = document.getElementById(`${sensor}-value`);
        if (valueElement) {
            valueElement.innerText = value;
            if (sensor === 'gps') {
                valueElement.innerText = `Lat: ${data[sensor].lat}, Lon: ${data[sensor].lon}`;
            }
            else if (sensor === 'imu') {
                valueElement.innerText = `X: ${data[sensor].ax}, Y: ${data[sensor].ay}, Z: ${data[sensor].az}`;
            } else {
                valueElement.innerText = `${data[sensor]}`;
            }
        }
    }
});


// Muestra el modal cuando se hace clic en un icono de sensor
function showModal(sensor) {
    // Establecer el título del sensor en el modal
    const modal = document.getElementById('sensorModal');
    const sensorTitle = document.getElementById('sensor-title');
    sensorTitle.innerText = titles[sensor];

    // Mostrar el modal
    modal.classList.add("show");

    // Cuando se haga clic en el botón de "Cargar Historial"
    document.getElementById('load-history').onclick = () => {
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;

        // Realiza la solicitud de los datos históricos para el sensor seleccionado
        console.log(`Cargando datos históricos para ${sensor} desde ${startDate} hasta ${endDate}`);
        fetch(`/api/history/${sensor}?start=${startDate}&end=${endDate}`)
            .then(response => response.json())
            .then(data => {
                if (Array.isArray(data) && data.length > 0) {
                    const timestamps = data.map(d => new Date(d.timestamp).toLocaleString());
                    const values = data.map(d => d.value);

                    // Verificar si ya existe un gráfico en el canvas y destruirlo
                    if (window.historyChart) {
                        window.historyChart.destroy();  // Destruir el gráfico anterior
                    }
                    // Crear gráfico con los datos históricos
                    const ctx = document.getElementById('history-chart').getContext('2d');
                    window.historyChart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: timestamps,
                            datasets: [{
                                label: titles[sensor],
                                data: values,
                                borderColor: 'rgba(75, 192, 192, 1)',
                                fill: false,
                            }]
                        },
                        options: {
                            responsive: true,
                            scales: {
                                x: {
                                    title: {
                                        display: true,
                                        text: 'Fecha'
                                    }
                                },
                                y: {
                                    title: {
                                        display: true,
                                        text: units[sensor]
                                    }
                                }
                            }
                        }
                    });
                } else {
                    alert('No se encontraron datos para el rango de fechas seleccionado');
                }
            })
            .catch(error => {
                console.error('Error al cargar los datos históricos:', error);
                alert('Ocurrió un error al obtener los datos');
            });
    };
}

// Cerrar el modal cuando se hace clic en el botón de "Cerrar" o en la "X"
document.getElementById('close-modal-x').onclick = () => {
    const modal = document.getElementById('sensorModal');
    modal.classList.remove("show");
    if (window.historyChart) {
        window.historyChart.destroy();
    }
};

// Cerrar el modal si se hace clic fuera del contenido del modal
window.onclick = (event) => {
    const modal = document.getElementById('sensorModal');
    if (event.target === modal) {
        modal.classList.remove("show");
        if (window.historyChart) {
            window.historyChart.destroy();
        }
    }
};
