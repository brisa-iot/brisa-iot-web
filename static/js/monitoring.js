function fetchNodesData() {
    console.log('Fetching initial sensor data...');
    fetch('/api/nodes-data')
        .then(response => response.json())
        .then(data => {
            console.log('Nodes data fetched:', data);
            var map = L.map('map').setView([-33.499902, -70.613848], 3);  // PUC coordinates
            L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(map);
            
            data.forEach(node => {
                var marker = L.marker([node.lat, node.lon]).addTo(map)
                    .bindPopup(`<b>Node ID: ${node.node_id}</b>`);
                
                // Open popup on mouse over
                marker.on('mouseover', function() {
                    marker.openPopup();
                });

                // Close popup on mouse out
                marker.on('mouseout', function() {
                    marker.closePopup();
                });
            
                // Evento al hacer clic en el marcador
                marker.on('click', function() {
                    console.log(`Node clicked: ${node.node_id}`);
                    const url = `/api/node/${node.node_id}`;
                    const data = JSON.stringify({ id: node.node_id });
                    navigator.sendBeacon(url, data);
                    window.location.href = "/sensors"; // Redirect to the sensors page
                });
            });
        });
}

window.onload = function() {
    fetchNodesData();
}