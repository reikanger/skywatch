#!/usr/bin/env python

# script designed to run on backend server,
# to collect the same flight data displayed in the app,
# and save it to the mongo database

# Dependencies
import requests
import schedule
import time
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient
from config import mongo_user, mongo_pass

# opensky_api module setup
from opensky_api import OpenSkyApi
from config import opensky_user, opensky_pass

# Global Variables
mongo_server = "localhost"
mongo_port = "27017"


def datetime_to_unix(dt):
    return int(time.mktime(dt.timetuple()))


def collect_flight_data():
    """main function for collecting flight data of upper midwest airspace and shipping it to mongo"""

    lat_min = 40.0000
    lat_max = 50.0000
    lon_min = -105.0000
    lon_max = -80.0000

    # connect to mongo database
    mongo_connection_string = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_server}:{mongo_port}/"
    mongo_client = MongoClient(mongo_connection_string)
    db = mongo_client['flights']
    flights_collection = db['flights']

    # connect to OpenSky API
    api = OpenSkyApi(opensky_user, opensky_pass)

    # get state vectors of each aircraft in upper midwest airspace
    state_data = api.get_states(bbox=(lat_min, lat_max, lon_min, lon_max))
    print(f'Pulled {len(state_data.states)} flight states from OpenSky API!')

    # convert class 'opensky_api.OpenSkyStates' to Python dictionary, and ship to Mongo
    if state_data:
        for s in state_data.states:
            flight_document = {
                'icao24': s.icao24,
                'callsign': s.callsign,
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

            # strip extra whitespace from callsign string
            flight_document['callsign'] = flight_document['callsign'].rstrip()

            # send the flight data dictionary to mongo
            insert_result = flights_collection.insert_one(flight_document)

    # close mongo and API connection
    mongo_client.close()
    del api

def main():
    """main function for executing when run as a script"""

    print('Starting flight data collection from midwest airspace every hour (Ctrl-C to exit):')

    # collect weather data every hour, at the top of the hour
    schedule.every().hour.at(':00').do(collect_flight_data)

    # run indefinitely on a schedule, exit on KeyboardInterrupt
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print('Exiting!')

if __name__ == '__main__':
    main()
