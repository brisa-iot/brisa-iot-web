console.log('Loading sensors.js');

let nodeId = null; // Variable to store the current node ID

const socket = io.connect('http://localhost:5000');

const sensors = [
    "conductivity",
    "gps",
    "humidity",
    "imu", 
    "wind",
    "oxygen",
    "pH",
    "pressure",
    "temperature", 
    "water_temperature",
    "soc",
    "current"
];

const titles = {
    "conductivity": "Conductivity",
    "gps": "GPS",
    "humidity": "Humidity",
    "imu": "IMU",
    "wind": "Wind",
    "oxygen": "Oxygen",
    "pH": "pH Level",
    "pressure": "Pressure",
    "temperature": "Temperature",
    "water_temperature": "Water Temperature",
    "soc": "State of Charge",
    "current": "Current",
}

const units = {
    "conductivity": "µS/cm",
    "wind_direction": "°",
    "gps_lat": "Latitude",
    "gps_lon": "Longitude",
    "humidity": "%",
    "imu_ax": "m/s²",
    "imu_ay": "m/s²",
    "imu_az": "m/s²",
    "wind_magnitude": "m/s",
    "oxygen": "mg/L",
    "pH": "pH",
    "pressure": "hPa",
    "temperature": "°C",
    "water_temperature": "°C",
    "soc": "%",
    "current": "A",
}

// Create a WebSocket connection
window.onload = () => {
    const container = document.getElementById('sensor-cards-container');

    const groupedSensors = {
        gps: ['gps_lat', 'gps_lon'],
        imu: ['imu_ax', 'imu_ay', 'imu_az'],
        wind: ['wind_direction', 'wind_magnitude']
    };

    sensors.forEach(sensor => {
        if (["gps", "imu", "wind"].includes(sensor)) {
            return; // Skip grouped sensors
        }

        const card = document.createElement('div');
        card.classList.add('sensor-card');
        card.id = `${sensor}-card`;
        card.onclick = () => showModal(sensor);

        card.innerHTML = `
            <div class="sensor-icon">
                <img src="static/img/svg/${sensor}.svg" class="icon" alt="${sensor} Icon">
                <div class="sensor-info">
                    <h3>${titles[sensor]}</h3>
                    <p class="value" id="${sensor}-value">Loading...</p>
                    <p class="unit">${units[sensor]}</p>
                </div>
            </div>
        `;

        container.appendChild(card);
    });

    // Create grouped cards
    Object.keys(groupedSensors).forEach(group => {
        const card = document.createElement('div');
        card.classList.add('sensor-card');
        card.id = `${group}-card`;
        card.onclick = () => showModal(group);

        card.innerHTML = `
            <div class="sensor-icon">
                <img src="static/img/svg/${group}.svg" class="icon" alt="${group} Icon">
                <div class="sensor-info">
                    <h3>${titles[group]}</h3>
                    <p class="value">
                        ${groupedSensors[group].map(sensor => `
                            <span id="${sensor}-value">Loading...</span> <span class="unit">${units[sensor]}</span>
                        `).join(' | ')}
                    </p>
                </div>
            </div>
        `;

        container.appendChild(card);
    });

    console.log('Initializing sensor cards...');
    fetchInitialSensorData();
};

// Fetch initial sensor data
function fetchInitialSensorData() {
    console.log('Fetching initial sensor data...');
    fetch('/api/sensors')
        .then(response => response.json())
        .then(data => {
            console.log('Initial sensor data received:', data);
            nodeId = data.node_id; // Store the node ID
            data.sensors.forEach(sensor => {
                console.log(`Sensor: ${sensor.sensor}, Value: ${sensor.value}`);
                const valueElement = document.getElementById(`${sensor.sensor}-value`);
                valueElement.innerText = `${sensor.value}`;
            });
        });
}

// WebSocket listener for sensor updates
socket.on('sensor_update', (data) => {
    console.log('Sensor update received:', data);
    if (nodeId == data.node_id) {
        const valueElement = document.getElementById(`${data.sensor}-value`);
        valueElement.innerText = `${data.value}`;
        
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
                    const timestamps = data.map(d => new Date(d.time).toLocaleString());
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
                                        text: 'Fecha',
                                        color: '#E0E0E0'
                                    },
                                    ticks: { color: '#E0E0E0' },
                                    grid: { color: '#455A64' }
                                },
                                y: {
                                    title: {
                                        display: true,
                                        text: units[sensor],
                                        color: '#E0E0E0'
                                    },
                                    ticks: { color: '#E0E0E0' },
                                    grid: { color: '#455A64' }
                                }
                            },
                            plugins: {
                                legend: {
                                    labels: { color: '#E0E0E0' }
                                },
                                zoom: {
                                    zoom: {
                                        wheel: {
                                            enabled: true, // Enable zooming with mouse wheel
                                        },
                                        pinch: {
                                            enabled: true // Enable zooming with pinch gesture
                                        },
                                        drag: {
                                            enabled: true, // Enable zooming by dragging a selection box
                                            modifierKey: 'ctrl', // Optional: require Ctrl key to drag-zoom
                                        },
                                        mode: 'xy', // Allow zooming both axes
                                    },
                                    pan: {
                                        enabled: true,
                                        mode: 'xy'
                                    },
                                    limits: {
                                        x: { min: 'original', max: 'original' },
                                        y: { min: 'original', max: 'original' }
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
