# dmigridcell.py --- Get Daisy hourly weather data from a DMI grid cell.

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

import pandas as pd

from daisy_tools.dmi import DMIOpenDataClient

client = DMIOpenDataClient(api_key=DMI_API_KEY, api_name="climateData")

# Call it
def create_weatherfile():
    [p, m] = client.get_data (latitude=LATITUDE, longitude=LONGITUDE, timeres=TIMERES,
                   pars=PARS)
    # find the cell that contains the coordinate LATITUDE, LONGITUDE
    cell_id = client.grid_name (latitude=LATITUDE, longitude=LONGITUDE)

    result = pd.DataFrame ()
    for par in PARS:
        result[par]=client.get_grid_cell_data_df(cell_id, par)

    # Sorting
    result.sort_index (inplace=True)
    file = cell_id + "_" + TIMERES + ".csv"
    result.to_csv (file)
    return 101

if __name__ == '__main__':
    create_weatherfile();

# dmigridcell.py ends here.
