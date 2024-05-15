# dmistation.py --- Get Daisy hourly weather data from a DMI station.

# Where we want data from
LATITUDE=55.707722
LONGITUDE=12.562119

# What data do we want
PARS = ["acc_precip", "mean_temp", "mean_relative_hum", "mean_wind_speed",
        "mean_radiation"]

# Time resolution 
TIMERES = "hour"

#Where we want data to go
OUTPUT_FILE = "dmidata.csv"

#Store information about data here
META_FILE = "dmimeta.csv"

# Your API key
DMI_API_KEY = ""

print ("Starting script")

from datetime import datetime
import numpy as np
import pandas as pd
from math import cos, asin, sqrt, pi

from daisy_tools.dmi import DMIOpenDataClient
from util import construct_datetime_argument, distance

# open-dmi-data: client.py

import requests
from tenacity import retry, stop_after_attempt, wait_random

# Get time series

print ("Opening DMI client")
client = DMIOpenDataClient(api_key=DMI_API_KEY, api_name="climateData")

# Following creates a .csv file containing meassured values for each of the parameters 
# in the list PARS. The values for each parameter are collected from the weather station
# closest to the given LATITUDE, LONGITUDE, with a recorded value for the given parameter.
# As such, the collected data may come from several weather stations.
# Weather data is stored in OUTPUT_FILE and meta data for each parameter is stored in 
# META_FILE
def create_weatherfiles():
    [p, m] = client.get_data (latitude=LATITUDE, longitude=LONGITUDE, timeres=TIMERES,
                   pars=PARS)

    # Sorting
    p.sort_index (inplace=True)

    # Write it.
    p.to_csv (OUTPUT_FILE)
    m.to_csv (META_FILE)
    return 101


if __name__ == '__main__':
    create_weatherfiles();

# dmistation.py ends here.
