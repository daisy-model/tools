from math import cos, asin, sqrt, pi
from datetime import datetime

def construct_datetime_argument(
    from_time = None, to_time = None
) -> str:
    if from_time is None and to_time is None:
        return None
    if from_time is not None and to_time is None:
        return f"{from_time.isoformat()}Z"
    if from_time is None and to_time is not None:
        return f"{to_time.isoformat()}Z"
    return f"{from_time.isoformat()}Z/{to_time.isoformat()}Z"

# Constants
CONST_EARTH_RADIUS = 6371       # km
CONST_EARTH_DIAMETER = 12742    # km

# From Stackoverflow answer
# https://stackoverflow.com/a/21623206/2538589
def distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km between two geographical points.

    Args:
        lat1 (float): Latitude of point 1.
        lon1 (float): Longitude of point 1.
        lat2 (float): Latitude of point 2.
        lon2 (float): Longitude of point 2.

    Returns:
        float: Haversine distance in km between point 1 and 2.
    """
    p = pi / 180.0
    a = 0.5 - cos((lat2 - lat1) * p) / 2.0 + cos(lat1 * p) * cos(lat2 * p) * (1.0 - cos((lon2 - lon1) * p)) / 2
    return CONST_EARTH_DIAMETER * asin(sqrt(a))  # 2*R*asin...
