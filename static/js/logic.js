// set URL for OpenSky REST API
//let url = 'https://opensky-network.org/api/states/all';  // all flights
//let url = 'https://opensky-network.org/api/states/all?lamin=42.0000&lomin=-98.0000&lamax=50.0000&lomax=-89.0000';  // bounding box covering Minnesota
let url = 'http://127.0.0.1:5000/api/v1/minnesota-airspace/'

// request data from URL - with basic HTTP authentication, and execute callback function once loaded
//d3.json(url, {
//	method: 'GET',
//	headers: {'Authorization': 'Basic ' + btoa('USERNAME' + ':' + 'PASSWORD')}, // NOTE: Add your OpenSky credentials here
//	creadentials: 'include'
//}).then(function (data) {
//d3.json(url, { mode: 'no-cors' }).then(function (data) {
d3.json(url).then(function (data) {
	// dev work
	console.log(data);

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

	// Flights data:
	//
	// array to hold aircraft layers for Leaflet for each aircraft
	let aircrafts_array = [];
	
	// loop aircraft object and make markers
	for (let i = 0; i < data.length; i++) {
		//console.log(data.states[i]);
		let callsign = data[i]['callsign'];
		let icao24 = data[i]['icao24'];
		let lat = data[i]['latitude'];
		let lon = data[i]['longitude'];
		let true_track = data[i]['true_track'];

		//console.log(`callsign: ${callsign} lon: ${lon} lat: ${lat}`);
		var aircraftIcon = L.icon({
			iconUrl: 'static/images/airplaneIcon.png',
			iconSize: [30, 30],
			iconAnchor: [22, 22]
		});

		// create a new Leaflet geoJSON layer, and attach a popup with more info
		let feature = L.marker(
			[lat, lon],
			{
				icon: aircraftIcon,
				rotationAngle: true_track,
				draggable: false
			}
		).bindPopup(`
			<h3>Callsign ${callsign}</h3>
			Transponder ICAO24: ${icao24}
		`).on('popupopen', function (e) {
			// on clicking popup for individual aircraft, request and display its trajectory as a line
			console.log(`User clicked aircraft with ICAO24 value of: ${icao24}`);
			console.log(e);
			let track_url = `http://127.0.0.1:5000/api/v1/trajectory/${icao24}`;
			d3.json(track_url).then(function (data) {
				//console.log(data);
				let path = data.path;
				//console.log(path);
				waypoints = [];
				for (let j = 0; j < path.length; j++) {
					console.log(path[j]);
					let waypoint_lat = path[j][1];
					let waypoint_lon = path[j][2]; 
					console.log(waypoint_lat);
					console.log(waypoint_lon);
				};
			});
		});

		//feature._icon.style.transform = `rotate(${true_track}deg)`;
		//feature._icon.style.transformOrigin = 'center';

		// add new layer to aircrafts_array
		aircrafts_array.push(feature);
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

		var airportIcon = L.icon({
			iconUrl: 'static/images/airportIcon.png',
			iconSize: [50, 50],
			iconAnchor: [22, 22]
		});

		let feature = L.marker(
			[lat, lon],
			{icon: airportIcon}
		)
		.bindPopup(`
			Website: <a href="${airports[i].website}">${airports[i].website}</a>
		`);
	
		//add new layer to airports_array
		airports_array.push(feature);
	};
	
	// create a layer group for the airport markers
	let aircrafts_group = L.layerGroup(aircrafts_array);
	let airports_group = L.layerGroup(airports_array);
	
	// Overlay map:
	//
	// create an object to hold the layer groups for toggle on/off
	let overlayMaps = {
		Aircraft: aircrafts_group,
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
		layers: [street, aircrafts_group, airports_group]
	});
	
	L.control.layers(baseMaps, overlayMaps, {
		collapsed: false
	}).addTo(myMap);

	// add radar layer
	L.control.radar({}).addTo(myMap);

})
.catch(error => {
	// handle errors
	console.error('Error fetching data: ', error);
});
