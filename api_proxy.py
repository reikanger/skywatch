#!/usr/bin/env python

# Import the dependencies.
import requests
from flask import Flask, jsonify
from flask_cors import CORS

# opensky_api module setup
from opensky_api import OpenSkyApi
from config import opensky_user, opensky_pass


#################################################
# Flask Setup
#################################################
app = Flask(__name__)
CORS(app) # enable CORS for the entire app


#################################################
# HTML (front end) Routes
#################################################
# Define what to do when a user hits the index route
@app.route('/')
def home():
    # List all available api routes.
    return (
        '<h1>API Routes:</h1>'
        '/api/v1/all-flights/<br>'
        '/api/v1/trajectory/<br>'
        '/api/v1/minnesota-airspace/<br>'
        '/api/v1/minnesota-departures/<br>'
        '/api/v1/minnesota-arrivals/<br>'
    )


#################################################
# API (back end) Routes
#################################################
@app.route('/api/v1/all-flights/')
def all_flights():
    print('Hello all_flights() function!')
    api = OpenSkyApi(opensky_user, opensky_pass)
    state_data = api.get_states()
    flights = []
    if state_data:
        print(f'Processing {len(state_data.states)} flight state documents')
        for s in state_data.states:
            flight_document = {
                'icao24': s.icao24,
                'callsign': s.callsign.rstrip(),
                'origin_country': s.origin_country,
                'time_position': s.time_position,
                'last_contact': s.last_contact,
                'longitude': s.longitude,
                'latitude': s.latitude,
                'geo_altitude': s.geo_altitude,
                'on_ground': s.on_ground,
                'true_track': s.true_track,
                'vertical_rate': s.vertical_rate,
                'sensors': s.sensors,
                'baro_altitude': s.baro_altitude,
                'squawk': s.squawk,
                'spi': s.spi,
                'position_source': s.position_source,
                'category': s.category
            }

            flights.append(flight_document)
        return jsonify(flights)
    else:
        return False


@app.route('/api/v1/trajectory/<icao24>')
def trajectory(icao24):
    print('Hello trajectory() function!')
    api = OpenSkyApi(opensky_user, opensky_pass)
    track = api.get_track_by_aircraft(icao24)
    return {
        'icao24': track.icao24,
        'startTime': track.startTime,
        'endTime': track.endTime,
        'callsign': track.callsign.rstrip(),
        'path': track.path
    }


@app.route('/api/v1/minnesota-airspace/')
def minnesota_airspace():
    print('Hello minnesota_airspace() function!')
    lat_min = 42.0000
    lat_max = 50.0000
    lon_min = -98.0000
    lon_max = -89.0000
    print((lat_min, lat_max, lon_min, lon_max))

    # print(opensky_user, opensky_pass)
    #response = requests.get(OPENSKY_NETWORK_URL, auth=(opensky_user, opensky_pass), params=params)
    #return jsonify(response.json())
    api = OpenSkyApi(opensky_user, opensky_pass)
    state_data = api.get_states(bbox=(lat_min, lat_max, lon_min, lon_max))
    flights = []
    if state_data:
        print(f'Processing {len(state_data.states)} flight state documents')
        for s in state_data.states:
            flight_document = {
                'icao24': s.icao24,
                'callsign': s.callsign.rstrip(),
                'origin_country': s.origin_country,
                'time_position': s.time_position,
                'last_contact': s.last_contact,
                'longitude': s.longitude,
                'latitude': s.latitude,
                'geo_altitude': s.geo_altitude,
                'on_ground': s.on_ground,
                'true_track': s.true_track,
                'vertical_rate': s.vertical_rate,
                'sensors': s.sensors,
                'baro_altitude': s.baro_altitude,
                'squawk': s.squawk,
                'spi': s.spi,
                'position_source': s.position_source,
                'category': s.category
            }

            flights.append(flight_document)
        return jsonify(flights)
    else:
        return False
    

if __name__ == '__main__':
    app.run(debug=True)
