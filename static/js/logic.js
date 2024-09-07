// set URL for OpenSky REST API
//let url = 'https://opensky-network.org/api/states/all';  // all flights
//let url = 'https://opensky-network.org/api/states/all?lamin=42.0000&lomin=-98.0000&lamax=50.0000&lomax=-89.0000';  // bounding box covering Minnesota
let url = 'http://127.0.0.1:5000/api/v1/midwest-airspace/'

//let waypoints = [];
//let polyline = null;


// request data from URL - with basic HTTP authentication, and execute callback function once loaded
//d3.json(url, {
//	method: 'GET',
//	headers: {'Authorization': 'Basic ' + btoa('USERNAME' + ':' + 'PASSWORD')}, // NOTE: Add your OpenSky credentials here
//	creadentials: 'include'
//}).then(function (data) {
//d3.json(url, { mode: 'no-cors' }).then(function (data) {
d3.json(url).then(function (data) {
	// dev work
	//console.log(data);

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

	// function to set an aircraft icons size based on altitude
	function getMarkerStyle(category, on_ground, true_track) {
		return {
			icon: aircraftIcon,
			rotationAngle: true_track + 90,
			draggable: false
		};
	};

	function getIconSize(altitude) {
		// size scaling factor based on altitude (0 to 10,000 meters)
		let size = altitude >= 10000 ? 35 :
			altitude >= 5000 ? 30 :
			altitude >= 2000 ? 25 :
			altitude >= 500 ? 20 :
			15;
		return size;
	};
	
	function getAircraftIcon(on_ground) {
		if (on_ground === false) {
			return 'static/images/airplaneIcon.png'
		} else {
			return 'static/images/airplaneLanded.png'
		};
	};

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
		//console.log(data[i]);
		let callsign = data[i]['callsign'];
		let category = data[i]['category'];
		let altitude = data[i]['geo_altitude']; // geometric altitude in meters
		let icao24 = data[i]['icao24'];
		let last_contact = data[i]['last_contact'];
		let lat = data[i]['latitude'];
		let lon = data[i]['longitude'];
		let on_ground = data[i]['on_ground']; // true if aircraft is on ground
		let origin_country = data[i]['origin_country']; // inferred through the ICAO24 address
		let true_track = data[i]['true_track'];

		////console.log(`callsign: ${callsign} lon: ${lon} lat: ${lat}`);
		let iconSize = getIconSize(altitude);
		var aircraftIcon = L.icon({
			//iconUrl: 'static/images/airplaneIcon.png',
			iconUrl: getAircraftIcon(on_ground),
			iconSize: [iconSize, iconSize],
			iconAnchor: [22, 22]
		});

		// create a new Leaflet geoJSON layer, and attach a popup with more info
		let markerStyle = getMarkerStyle(category, on_ground, true_track);
		let feature = L.marker(
			[lat, lon],
			markerStyle
		// show popup on a click
		).bindPopup(`
			<h3>Callsign ${callsign}</h3>
			Altitude: ${altitude} meters<br>
			On Ground: ${on_ground}<br>
			Origin Country: ${origin_country}<br>
			<br>
			Last Updated:<br>${Date(last_contact)}
			`,
			{offset: L.point(0, -10)} // move 10px up
		// display trajectory on click
		).on('popupopen', function (e) {
			// clear out the old polylines
			myMap.eachLayer(function (layer) {
				if (layer instanceof L.Polyline) {
					myMap.removeLayer(layer);
				}
			});

			// on clicking popup for individual aircraft, request and display its trajectory as a line
			//console.log(`User clicked aircraft with ICAO24 value of: ${icao24}`);
			//console.log(e);
			let track_url = `http://127.0.0.1:5000/api/v1/trajectory/${icao24}`;
			d3.json(track_url).then(function (data) {
				////console.log(data);
				let path = data.path;
				////console.log(path);
				waypoints = [];
				for (let j = 0; j < path.length; j++) {
					//console.log(path[j]);
					let waypoint_lat = path[j][1];
					let waypoint_lon = path[j][2]; 
					//console.log(waypoint_lat);
					//console.log(waypoint_lon);
					waypoints.push([waypoint_lat, waypoint_lon]);
				};
				polyline = L.polyline(waypoints, {color: 'red', weight: 3, opacity: 1, dashArray: '5,10'}).addTo(myMap);
			});
		});

		// add new layer to aircrafts_array
		aircrafts_array.push(feature);
	};
	
	// Airports and local weather data:
	//
	// array to hold airport geo-locations
	const airports = [
		{'city': 'Minneapolis-St. Paul', 'zipcode': [55111], 'icao': 'KMSP', 'faa': 'MSP', 'coordinates': [-93.22, 44.88], 'website': 'https://www.mspairport.com/'},
		{'city': 'Duluth', 'zipcode': [55811], 'icao': 'KDLH', 'faa': 'DLH', 'coordinates': [-92.18, 46.84], 'website': 'https://duluthairport.com/'},
		{'city': 'Rochester', 'zipcode': [55902], 'icao': 'KRST', 'faa': 'RST', 'coordinates': [-92.50, 43.91], 'website': 'https://flyrst.com/'},
	];
	
	// array to hold airport layers for Leaflet for each airport
	let airports_array = [];

	// array to hold airport weather data
	let weatherApiPromiseArray = [];
	
	// loop airports object and make markers
	for (let i = 0; i < airports.length; i++) {
		let lon = airports[i].coordinates[0];
		let lat = airports[i].coordinates[1];

		var airportIcon = L.icon({
			iconUrl: 'static/images/airportIcon.png',
			iconSize: [30, 30],
			iconAnchor: [22, 22]
		});

		let feature = L.marker(
			[lat, lon],
			{ icon: airportIcon })
		.bindPopup(`
			<strong>Airport:</strong> ${airports[i].faa}<br>
			<strong>City:</strong> ${airports[i].city}<br>
			<strong>Website:</strong> <a href="${airports[i].website}">${airports[i].website}</a><br>
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
