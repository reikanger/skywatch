// Base Maps Layers:
//
// create base map layer
let street = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
	attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
});

// create topographic view layer
let topo = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
	attribution: 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
});

// Create a baseMaps object to store the two map layers with friendly names
let baseMaps = {
	"Street Map": street,
	"Topographic Map": topo
};

// Create Leaflet map:
//
// add leaflet map to 'map' div in index.html
let myMap = L.map("map", {
	center: [
		45.00, -93.00
	],
	zoom: 7,
	layers: [street]
});

L.control.layers(baseMaps, {
	collapsed: false
}).addTo(myMap);

