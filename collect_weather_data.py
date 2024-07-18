#!/usr/bin/env python

# Dependencies
import requests
import schedule
import time
from datetime import datetime
from pymongo import MongoClient
from config import weather_api_key, mongo_user, mongo_pass

# Global Variables
url_weather = f"http://api.weatherapi.com/v1/current.json?key={weather_api_key}&aqi=no"
#mongo_server = "146.190.144.51"
mongo_server = "localhost" # since we're running this script on the VPS itself, we can connect to localhost
mongo_port = "27017"

# Set zipcodes of the airport of interest:
# - MSP Terminal #1: 55111
# - Duluth: 55811
# - Rochester: 55902
airport_zipcodes = [55111, 55811, 55902]

def collect_weather_data():
    """main function for collecting weather data and shipping it to mongo"""

    # connect to mongo database
    mongo_connection_string = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_server}:{mongo_port}/"
    mongo_client = MongoClient(mongo_connection_string)
    db = mongo_client['weather']
    collection = db['weather']

    # collect weather data
    # Pull current weather of every airport location
    for zipcode in airport_zipcodes:
        request_url = f"{url_weather}&q={zipcode}"

        weather_document = requests.get(request_url).json()
        insert_result = collection.insert_one(weather_document)

        print(f'Shipped weather data for {zipcode} to Mongo at {datetime.now()}')

    # close mongo connection
    mongo_client.close()

def main():
    """main function for executing when run as a script"""

    print('Starting weather data collection every hour (Ctrl-C to exit):')

    # collect weather data every hour, at the top of the hour
    schedule.every(2).minutes.at(':00').do(collect_weather_data)

    # run indefinitely on a schedule, exit on KeyboardInterrupt
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print('Exiting!')

if __name__ == '__main__':
    main()
