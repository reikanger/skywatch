#!/usr/bin/env python

# Import the dependencies.
import requests
import time
from datetime import datetime, timezone, timedelta
from flask import Flask, jsonify
from flask_cors import CORS

# opensky_api module setup
from opensky_api import OpenSkyApi
from config import opensky_user, opensky_pass

# global variables
# Set ICAO values of the airports of interest:
# - Minneapolis–St. Paul International: KMSP
# - Duluth International Airport: KDLH
# - Rochester International Airport: KRST
airports = ['KMSP', 'KDLH', 'KRST']

# supporting functions
def datetime_to_unix(dt):
    return int(time.mktime(dt.timetuple()))

def get_arrival_transponders():
    # connect to OpenSky API
    api = OpenSkyApi(opensky_user, opensky_pass)

    # determine timestamp values for time range: one half day ago to current
    now = datetime.now()
    day_ago = now - timedelta(hours=24)
    start_ts = datetime_to_unix(day_ago)
    end_ts = datetime_to_unix(now)

    # array to hold unique transponders
    transponders = []

    # get the unique flights going to or from our airports
    for airport in airports:
        # get unique arrival aircraft
        arrivals = api.get_arrivals_by_airport(airport, start_ts, end_ts)
        if arrivals is not None:
            for flight in arrivals:
                if flight.icao24 not in transponders:
                    transponders.append(flight.icao24)

    # check that we got values and return them
    print(type(transponders))
    print(transponders)
    return transponders

def get_departure_transponders():
    # connect to OpenSky API
    api = OpenSkyApi(opensky_user, opensky_pass)

    # determine timestamp values for time range: one half day ago to current
    now = datetime.now()
    day_ago = now - timedelta(hours=24)
    start_ts = datetime_to_unix(day_ago)
    end_ts = datetime_to_unix(now)

    # array to hold unique transponders
    transponders = []

    # get the unique flights going to or from our airports
    for airport in airports:
        # get unique departure aircraft
        departures = api.get_departures_by_airport(airport, start_ts, end_ts)
        if departures is not None:
            for flight in departures:
                if flight.icao24 not in transponders:
                    transponders.append(flight.icao24)

    # check that we got values and return them
    print(type(transponders))
    print(transponders)
    return transponders

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


@app.route('/api/v1/midwest-airspace/')
def minnesota_airspace():
    print('Hello midwest_airspace() function!')
    lat_min = 40.0000
    lat_max = 50.0000
    lon_min = -105.0000
    lon_max = -80.0000
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
    
@app.route('/api/v1/minnesota-departures/')
def minnesota_departures():
    return get_departure_transponders()

@app.route('/api/v1/minnesota-arrivals/')
def minnesota_arrivals():
    return get_arrival_transponders()

if __name__ == '__main__':
    app.run(debug=True)
