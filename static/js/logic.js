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

// Airports data:
//
// array to hold airport geo-locations
const airports = [
	{'city': 'Minneapolis-St. Paul', 'icao': 'KMSP', 'faa': 'MSP', 'coordinates': [-93.22, 44.88], 'website': 'https://www.mspairport.com/'},
	{'city': 'Duluth', 'icao': 'KDLH', 'faa': 'DLH', 'coordinates': [-92.18, 46.84], 'website': 'https://duluthairport.com/'},
	{'city': 'Rochester', 'icao': 'KRST', 'faa': 'RST', 'coordinates': [-92.50, 43.91], 'website': 'https://flyrst.com/'},
];

// array to hold airport layers for Leaflet for each airport
let airports_array = [];

// loop airports object and make markers
for (let i = 0; i < airports.length; i++) {
	let lon = airports[i].coordinates[0];
	let lat = airports[i].coordinates[1];

	let feature = L.circleMarker(
		[lat, lon]
	)
	.bindPopup(`
		Website: <a href="${airports[i].website}">${airports[i].website}</a>
	`);

	//add new layer to airports_array
	airports_array.push(feature);
};

// create a layer group for the airport markers
let airports_group = L.layerGroup(airports_array);

// Overlay map:
//
// create an object to hold the layer groups for toggle on/off
let overlayMaps = {
	Airports: airports_group
};

// Create Leaflet map:
//
// add leaflet map to 'map' div in index.html
let myMap = L.map("map", {
	center: [
		45.00, -93.00
	],
	zoom: 7,
	layers: [street, airports_group]
});

L.control.layers(baseMaps, overlayMaps, {
	collapsed: false
}).addTo(myMap);

