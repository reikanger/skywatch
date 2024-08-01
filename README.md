# Project 3
Group Members:

- Ryan Eikanger
- Melissa Judy
- Robin Ryan

Initial project proposal found under 'Proposal_GroupProject3'

Explanation of process, map usage, data ethics, and citations found under 'Project3Info'

Presentation: [https://docs.google.com/presentation/d/1AmBSM6ayavU_XtMIRKjHrXmCjitdwrjP2nzf14Lopvc/edit?usp=sharing](https://docs.google.com/presentation/d/1AmBSM6ayavU_XtMIRKjHrXmCjitdwrjP2nzf14Lopvc/edit?usp=sharing)


## Prerequisites
### Python Modules
Install the Python modules listed in the requirements file:
```shell
pip install -r requirements.txt
```

### OpenSky API Module
The flight tracker gets the data to display aircraft and their way points from the [OpenSky Network](https://opensky-network.org/). Installation of the Python module that OpenSky provides is required for this project.

#### Installation
First, download the opensky-api Python module from OpenSky, either by cloning their repository or as a ZIP file:  
```shell
# clone the opensky-api repository
git clone git@github.com:openskynetwork/opensky-api.git

# OR, download repository as ZIP file
https://github.com/openskynetwork/opensky-api/archive/refs/heads/master.zip
```

Then, install the opensky-api module with `pip`.
```shell
cd opensky-api
pip install -e ./support/opensky-api/python
```
### Leaflet Rotated Marker
Leaflet Rotated Marker is a plugin that enables rotation of marker icons in Leaflet.

The plugin is included in this project, but if needed, install the plugin through the npm package manager.

```shell
npm install leaflet-rotatedmarker
```

## Run Application
The application relied on the `api_proxy.py` Python Flask application to interact with the OpenSky API. The Flask application will run continuously in the background until stopped by the user.

Run `api_proxy.py` before using the application:
```shell
./api_proxy.py
```

Then, host the top level of this repository with your web server of choice.
```shell
python3 -m http.server 8000
```
### Back End Data Collection
Scheduled collection of flight and weather data happens through back-end Python scripts, that are designed to run continuously in the background until stopped by the user.

```
collect_flight_data.py
collect_weather_data.py
```

Both scripts save to a local MongoDB server, that needs to be hosted by the user.

## References
### OpenSky Network
[OpenSky Network](https://opensky-network.org/)

### Weather
[Weather API](https://www.weatherapi.com/)

### Leaflet Rotated Marker
[Leaflet.RotatedMarker](https://github.com/bbecquet/Leaflet.RotatedMarker)

### Leaflet Radar
[leaflet-radar](https://github.com/rwev/leaflet-radar)

- `leaflet-radar.js` uses Iowa State University's MESONET: [https://mesonet.agron.iastate.edu/](https://mesonet.agron.iastate.edu/)
