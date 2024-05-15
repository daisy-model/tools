import requests
from tenacity import retry, stop_after_attempt, wait_random
import numpy as np
import pandas as pd
from pyproj import Proj
from math import trunc
from .util import construct_datetime_argument, distance

__all__ = [
    'DMIOpenDataClient',
]

class DMIOpenDataClient():
    BASE_URL = "https://dmigw.govcloud.dk/{version}/{api}"
    SUPPORTED_APIS = {"climateData", "metObs"}
    SUPPORTED_VERSIONS = {"v2"}

    def __init__(self, api_key: str, api_name: str = "metObs", version: str = "v2"):
        if api_key is None:
            raise ValueError(f"Invalid value for `api_key`: {api_key}")

        if api_name not in self.SUPPORTED_APIS:
            raise NotImplementedError(f"Following API is not supported yet: {api_name}")

        if version not in self.SUPPORTED_VERSIONS:
            raise ValueError(f"API version {version} not supported")

        self.api_key = api_key
        self.api_name = api_name
        self.version = version

    def base_url(self, api: str):
        if api not in self.SUPPORTED_APIS:
            raise NotImplementedError(f"Following API is not supported yet: {api}")
        return self.BASE_URL.format(version=self.version, api=api)

    @retry(stop=stop_after_attempt(10), wait=wait_random(min=0.1, max=1.00))
    def _query(self, api: str, service: str, params, **kwargs):
        res = requests.get(
            url=f"{self.base_url(api=api)}/{service}",
            params={"api-key": self.api_key, **params},
            **kwargs,
        )
        data = res.json()
        http_status_code = data.get("http_status_code", 200)
        if http_status_code != 200:
            message = data.get("message")
            raise ValueError(
                f"Failed HTTP request with HTTP status code {http_status_code} and message: {message}"
            )
        return res.json()

    def get_stations(self, limit=10000, offset=0):
        res = self._query(
            api=self.api_name,
            service="collections/station/items",
            params={"limit": limit, "offset": offset},
        )
        return res.get("features", [])

    def get_observations(
        self,
        parameter=None,
        station_id=None,
        from_time=None,
        to_time=None,
        limit=10000,
        offset=0,
    ):
        res = self._query(
            api="metObs",
            service="collections/observation/items",
            params={
                "parameterId": parameter,
                "stationId": station_id,
                "datetime": construct_datetime_argument(from_time=from_time, to_time=to_time),
                "limit": limit,
                "offset": offset,
            },
        )
        return res.get("features", [])

    def get_climate_data(
        self,
        parameter=None,
        station_id=None,
        from_time=None,
        to_time=None,
        time_resolution=None,
        limit=10000,
        offset=0,
    ):
        res = self._query(
            api="climateData",
            service="collections/stationValue/items",
            params={
                "parameterId": parameter,
                "stationId": station_id,
                "datetime": construct_datetime_argument(from_time=from_time, to_time=to_time),
                "timeResolution": time_resolution,
                "limit": limit,
                "offset": offset,
            },
        )
        return res.get("features", [])

    def get_closest_station(
        self, latitude: float, longitude: float, pars=[]
    ):
        stations = self.get_stations()
        closest_station, closest_dist = None, float("inf")
        wanted_pars = set(pars)

        for station in stations:
            coordinates = station.get("geometry", {}).get("coordinates")
            if coordinates is None or len(coordinates) < 2:
                continue

            lat, lon = coordinates[1], coordinates[0]
            if lat is None or lon is None:
                continue

            has_pars = set(station['properties']['parameterId'])
            if not wanted_pars.issubset(has_pars):
                continue

            # Calculate distance
            dist = distance(lat1=latitude, lon1=longitude, lat2=lat, lon2=lon)

            if dist < closest_dist:
                closest_dist, closest_station = dist, station

        return closest_station

    def get_value(self, data):
        return (i['properties']['value'] for i in data)

    def get_index(self, data):
        return (np.datetime64(i['properties']['to']) for i in data)

    def get_series(self, *, par, station_id, timeres):
        print("Looking up parameter ", par)
        data = self.get_climate_data(par, station_id=station_id, time_resolution=timeres, limit=200000)
        if len(data) > 0:
            print("Has ", len(data), "datapoints")
        else:
            print("No data, ignoring")
        return pd.Series(self.get_value(data), index=self.get_index(data))

    def get_data(self, *, latitude, longitude, timeres, pars):
        p = pd.DataFrame()
        m = pd.DataFrame(columns=["par", "id", "dist", "lat", "lon"])

        for par in pars:
            print("Looking for station with", par)
            station = self.get_closest_station(latitude=latitude, longitude=longitude, pars=[par])

            if not station:
                print("None found")
                continue

            coordinates = station.get("geometry", {}).get("coordinates")
            station_lat, station_lon = coordinates[1], coordinates[0]
            station_id = station['properties']['stationId']
            dist = distance(lat1=latitude, lon1=longitude, lat2=station_lat, lon2=station_lon)

            print("Found", par, "in station", station_id, dist, "km away")
            new_row = pd.DataFrame(
                {'par': par, 'id': station_id, 'dist': dist, 'lat': station_lat, 'lon': station_lon}, index=[0])
            m = pd.concat([new_row, m.loc[:]]).reset_index(drop=True)
            s = self.get_series(par=par, station_id=station_id, timeres=timeres)

            if len(s) > 0:
                p[par] = s

        return p, m
    
    def grid_name(self, latitude, longitude, size="10km"):
        # DMI uses "Det Dansk Kvadratnet" which uses ETRS89 / EPSG25832.
        ETRS89 = Proj('epsg:25832')
        east, north = ETRS89(latitude=latitude, longitude=longitude)

        # Grid resolution. DMI supports 10 km and 20 km.
        res = {"10km": 10000, "20km": 20000}
        mul = {"10km": 1, "20km": 2}
        r = res[size]
        m = mul[size]

        n = str(trunc(north / r) * m)
        e = str(trunc(east / r) * m)
        cell_id = f"{size}_{n}_{e}"
        return cell_id

    def get_grid_cell_data_df (client, cell_id, param_name, spatial_res="10km", temporal_res="hour", limit=300000 ):
        #TODO handle 20km grid and optional time span
        json = client._query(api='climateData',
                          service=f'/collections/{spatial_res}GridValue/items',
                          params={'cellId': cell_id,
                                  'limit': limit,
                                  'timeResolution': temporal_res,
                                  'parameterId': param_name })
                
        df = pd.json_normalize(json['features'])

        entry = df[df['properties.parameterId']==param_name][['properties.to','properties.value']]
        entry['Time']=pd.to_datetime(entry['properties.to'])
        entry.index=entry['Time'].values
        print (param_name, ":",
            len (entry), "entries")
        if (len (entry.index.unique()) != len (entry)):
            entry = entry.drop_duplicates (subset='Time', keep="last")
            print (len (entry), "unique")
        return entry['properties.value']