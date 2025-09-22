# Client for retrieving weather data from [Danmarks Meteorologiske Institut (DMI)](https://www.dmi.dk/frie-data).

## Overview

`DMIOpenDataClient` is a Python client library for accessing the Danish Meteorological Institute (DMI) Open Data API. This library supports fetching climate data, meteorological observations, and other related data from DMI's open data platform.

For examples of how to use this modules, please have a look in the `examples` folder.

## Features

- Retrieve metadata about weather stations
- Fetch meteorological observations and climate data
- Find the closest weather station based on geographic coordinates
- Convert geographic coordinates to DMI grid cell identifiers
- Extract data from specific grid cells

## Prerequisites
Firstly, make sure you have installed the `daisy_tools` package correctly. Next, make sure to activate the virtual environment where the package was installed.

To be able to use DMI's services, you will need an API key. You will need an API key for each of the APIs (and versions) you wish to retrieve data from.

To obtain an API key, go to [DMI Open Data](https://opendatadocs.dmi.govcloud.dk/DMIOpenData). The section [Getting Started](https://opendatadocs.dmi.govcloud.dk/en/Getting_Started) gives an introduction to the API service and available data. The section [Authentification](https://opendatadocs.dmi.govcloud.dk/en/Authentication) provides an illustrated guide to getting an account and subscribing to the desired APIs.

## Usage

Once you have installed the `daisy_tools` package, you can import the `DMIOpenDataClient` as follows:

```python
from daisy_tools.dmi import DMIOpenDataClient
```

### Initialization

To start using the client, you need to initialize it with your API key and the correct API identifier:

```python
climate_api_key = "your_climate_api_key_here"
climate_data_client = DMIOpenDataClient(api_key=climate_api_key, api_name="climateData")
met_obs_api_key = "your_metobs_api_key_here"
met_obs_client = DMIOpenDataClient(api_key=met_obs_api_key, api_name="metObs")
```

The module currently supports two DMI APIs: `climateData` and `MetObs`.

We will also need timezone data and the datetime class to construct correct datetime strings
```python
from datetime import datetime, timedelta, timezone
tz = timezone(timedelta(hours=2), "CEST") # Central European Summer Time
```

### Fetch Stations

Retrieve metadata about weather stations using either client:

```python
stations = climate_data_client.get_stations(limit=100)
print(stations)
```

The optional parameter `limit` determines how many stations are fetched, default for the function is `10000`.

### Fetch Observations

Get meteorological observations for a specific parameter and station using the `met_obs_client`:

```python
from_time = datetime(2022,1,1,0,0,0,tzinfo=tz)
to_time = datetime(2022,1,2,0,0,0,tzinfo=tz)
observations = met_obs_client.get_observations(parameter="temp_mean_past1h", station_id="06181", from_time=from_time, to_time=to_time)
print(observations)
```
Notice that timestamps are returned in UTC.

### Fetch Climate Data

Fetch climate data for a specific parameter and station using the `climata_data_client`:

```python
climate_data = climate_data_client.get_climate_data(parameter="mean_temp", station_id="06181", from_time=from_time, to_time=to_time, time_resolution="hour")
print(climate_data)
```
Again, notice that timestamps are returned in UTC.

### Get Closest Station

Find the closest weather station to a given geographic coordinate, which has recorded data for the given list of `pars`:

```python
latitude, longitude = 55.6761, 12.5683
closest_station = met_obs_client.get_closest_station(latitude=latitude, longitude=longitude, pars=["temp_mean_past1h"])
print(closest_station)
```

### Get Data Series

Get time series data for a specific parameter and station (only implemented for `climateData` API):

```python
series = climate_data_client.get_series(par="mean_temp", station_id="06181", timeres="hour")
print(series)
```

### Get Data for Multiple Parameters

Retrieve data for multiple parameters, from the stations closest to a given location (only implemented for `climateData` API):

```python
latitude, longitude = 55.6761, 12.5683
data, metadata = climate_data_client.get_data(latitude=latitude, longitude=longitude, timeres="hour", pars=["mean_temp", "acc_precip"])
print(data)
print(metadata)
```

### Grid Cell Identifier

Convert geographic coordinates to a DMI grid cell identifier:

```python
cell_id = climate_data_client.grid_name(latitude=55.6761, longitude=12.5683, size="10km")
print(cell_id)
```

## Error Handling

The client uses the `tenacity` library to implement retry logic for HTTP requests. If a request fails, it will retry up to 10 times with a random wait time between 0.1 and 1 second.

## Dependencies

This library uses the following third-party packages:

- `requests`: For making HTTP requests.
- `tenacity`: For retrying failed requests.
- `numpy`: For numerical operations.
- `pandas`: For data manipulation and analysis.
- `pyproj`: For coordinate transformations.
- `datetime`: For date operations.

---

This README provides a comprehensive guide to using the `DMIOpenDataClient` library. For more detailed examples and advanced usage, refer to the documentation within the code and the provided docstrings.
