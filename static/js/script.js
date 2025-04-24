const socket = io.connect('http://localhost:5000');

document.addEventListener("DOMContentLoaded", () => {
    inicializarGraficos();
});


// Configuración de los gráficos
const maxPoints = 30; // Número máximo de puntos a mostrar en el gráfico

const sensorToChartId = {
    "conductividad": "condChart",
    "direccion_viento": "windDirChart",
    "gps": "gpsChart",
    "humedad": "humChart",
    "imu": "imuChart",
    "magnitud_viento": "windMagChart",
    "oxigeno_disuelto": "oxygenChart",
    "pH": "pHChart",
    "presion": "presChart",
    "temperatura": "tempChart",
    "temperatura_agua": "waterTempChart"
};

const chartsConfig = [
    { id: 'tempChart', label: 'Temperatura (°C)', color: 'red' },
    { id: 'humChart', label: 'Humedad Relativa (%)', color: 'blue' },
    { id: 'presChart', label: 'Presión Atmosférica (hPa)', color: 'green' },
    { id: 'windMagChart', label: 'Magnitud del Viento (m/s)', color: 'purple' },
    { id: 'windDirChart', label: 'Dirección del Viento (°)', color: 'orange' },
    { id: 'pHChart', label: 'pH', color: 'brown' },
    { id: 'condChart', label: 'Conductividad (µS/cm)', color: 'cyan' },
    { id: 'waterTempChart', label: 'Temperatura del Agua (°C)', color: 'pink' },
    { id: 'oxygenChart', label: 'Oxígeno Disuelto (mg/L)', color: 'gray' },
    { id: 'gpsChart', labelLat: 'Latitud GPS (°)', labelLon: 'Longitud GPS (°)', colorLat: 'black', colorLon: 'blue' },
    { id: 'imuChart', labelAX: 'Acelerómetro X (m/s²)', labelAY: 'Acelerómetro Y (m/s²)', labelAZ: 'Acelerómetro Z (m/s²)', colorAX: 'magenta', colorAY: 'cyan', colorAZ: 'orange' }
];

const charts = {};

function inicializarGraficos() {
    chartsConfig.forEach(config => {
        const canvas = document.getElementById(config.id);
        console.log(`Buscando elemento: ${config.id}`, canvas);  // Verifica que los elementos existen

        if (!canvas) {
            console.error(`No se encontró el canvas con id ${config.id}`);
            return;
        }

        const ctx = canvas.getContext('2d');

        if (config.id === 'gpsChart') {
            charts[config.id] = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        { label: config.labelLat, data: [], borderColor: config.colorLat, fill: false },
                        { label: config.labelLon, data: [], borderColor: config.colorLon, fill: false }
                    ]
                },
                options: { responsive: true }
            });
        } else if (config.id === 'imuChart') {
            charts[config.id] = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        { label: config.labelAX, data: [], borderColor: config.colorAX, fill: false },
                        { label: config.labelAY, data: [], borderColor: config.colorAY, fill: false },
                        { label: config.labelAZ, data: [], borderColor: config.colorAZ, fill: false }
                    ]
                },
                options: { responsive: true }
            });
        } else {
            charts[config.id] = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{ label: config.label, data: [], borderColor: config.color, fill: false }]
                },
                options: { responsive: true }
            });
        }

        console.log(`Gráfico ${config.id} creado correctamente.`);
    });
}


// Conectar con WebSockets para datos en tiempo real
socket.on('connect', () => {
    console.log('Conectado al servidor WebSocket');
    socket.emit('subscribe', {});
});

// Desconectar del WebSocket cuando se cierra la pestaña
window.addEventListener('beforeunload', () => {
    socket.emit('unsubscribe', {});
});

// Recibir datos en tiempo real y actualizar los gráficos
socket.on('live_update', (data) => {
    // console.log('Datos recibidos:', data);

    // get timestamp from data and delete it
    const timestamp = data.timestamp;
    delete data.timestamp;
    
    // Actualizar gráficos de temperatura, humedad, etc.
    Object.keys(data).forEach(sensor => {
        const chartId = sensorToChartId[sensor];

        if (sensor === 'gps') {
            // Actualizar gráfico GPS
            charts.gpsChart.data.labels.push(new Date().toLocaleTimeString());
            charts.gpsChart.data.datasets[0].data.push(data[sensor].lat);
            charts.gpsChart.data.datasets[1].data.push(data[sensor].lon);
            charts.gpsChart.update();
            // Limitar el número de puntos mostrados en el gráfico
            if (charts.gpsChart.data.labels.length > maxPoints) {
                charts.gpsChart.data.labels.shift();
                charts.gpsChart.data.datasets[0].data.shift();
                charts.gpsChart.data.datasets[1].data.shift();
            }
        } else if (sensor === 'imu') {
            // Actualizar gráfico IMU
            charts.imuChart.data.labels.push(new Date().toLocaleTimeString());
            charts.imuChart.data.datasets[0].data.push(data[sensor].ax);
            charts.imuChart.data.datasets[1].data.push(data[sensor].ay);
            charts.imuChart.data.datasets[2].data.push(data[sensor].az);
            charts.imuChart.update();
            // Limitar el número de puntos mostrados en el gráfico
            if (charts.imuChart.data.labels.length > maxPoints) {
                charts.imuChart.data.labels.shift();
                charts.imuChart.data.datasets[0].data.shift();
                charts.imuChart.data.datasets[1].data.shift();
                charts.imuChart.data.datasets[2].data.shift();
            }
        } else {
            // Actualizar gráficos de otros sensores
            if (charts[chartId]) {
                // Añadir los nuevos datos
                charts[chartId].data.labels.push(new Date().toLocaleTimeString());
                charts[chartId].data.datasets[0].data.push(data[sensor]);
                charts[chartId].update();
                // Limitar el número de puntos mostrados en cada gráfico
                if (charts[chartId].data.labels.length > maxPoints) {
                    charts[chartId].data.labels.shift();
                    charts[chartId].data.datasets[0].data.shift();
                }
            }
        }
    });
});
