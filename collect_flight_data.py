#!/usr/bin/env python

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
#mongo_server = "146.190.144.51"
mongo_server = "localhost" # since we're running this script on the VPS itself, we can connect to localhost
mongo_port = "27017"

# Set ICAO values of the airports of interest:
# - Minneapolis–St. Paul International: KMSP
# - Duluth International Airport: KDLH
# - Rochester International Airport: KRST
airports = ['KMSP', 'KDLH', 'KRST']


def datetime_to_unix(dt):
    return int(time.mktime(dt.timetuple()))


def get_transponders():
    # connect to OpenSky API
    api = OpenSkyApi(opensky_user, opensky_pass)

    # determine timestamp values for time range: one half day ago to current
    now = datetime.now()
    half_day_ago = now - timedelta(hours=12)
    start_ts = datetime_to_unix(half_day_ago)
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

        # get unique departure aircraft
        departures = api.get_departures_by_airport(airport, start_ts, end_ts)
        if departures is not None:
            for flight in departures:
                if flight.icao24 not in transponders:
                    transponders.append(flight.icao24)

    # check that we got values and return them
    print(type(transponders))
    print(transponders)
    del api
    return transponders

def collect_flight_data():
    """main function for collecting weather data and shipping it to mongo"""

    # connect to mongo database
    mongo_connection_string = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_server}:{mongo_port}/"
    mongo_client = MongoClient(mongo_connection_string)
    db = mongo_client['flights']
    flights_collection = db['flights']

    # get list of aircraft to collect data from
    transponders = get_transponders()

    # connect to OpenSky API
    api = OpenSkyApi(opensky_user, opensky_pass)

    # get state vectors of each tracked arrival aircraft
    if transponders: # only run if we have a list of aircraft (don't pass empty lists to API)
        state_data = api.get_states(icao24=transponders)
        print(f'Just pulled {len(state_data.states)} flight states from API!')

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
            print(f'Shipped flight data for {flight_document['callsign']} to Mongo')

    # close mongo and API connection
    mongo_client.close()
    del api

def main():
    """main function for executing when run as a script"""

    print('Starting flight data collection every hour (Ctrl-C to exit):')

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
