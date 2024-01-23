'''Utility functions for HIP data extraction and transformation'''
import warnings
from .layer_names import hip_elevation_to_hip_pressure, hip_pressure_to_dkm2019, dkm2019_to_aquifer

__all__ = [
    'find_topmost_aquifer',
    'get_idx_and_coord'
]

def find_topmost_aquifer(dk_model, soil_column):
    '''Find the topmost aquifer layer in a soil column

    Parameters
    ----------
    model : str
      Name of DK-model HIP. Valid model names are {
        'DK1', 'DK2', 'DK3', 'DK4', 'DK5', 'DK6', 'DK7'
      }

    soil_column: pandas.DataFrame
      Soil column as extracted by `daisy_tools.hip.extract_soil_column`.
      The only required column is 'layer'. It is assumed that soil_column['layer'] contains the
      layers ordered from top to bottom.

    Returns
    -------
    aquifer_layer_name : dict
      A dict with the name of the topmost aquifer layer using different naming conventions.
      Contains the following keys
      {
        'elevation', # HIP elevation name style, e.g. 'CompLayer_11'
        'head_elevation', # HIP pressure name style, e.g. 0
        'dk2019', # DKM2019 name style, e.g. 'kalk'
        'aquifer', # Aquifer name, e.g. 'glw6'
      }
    '''
    he_to_hp = hip_elevation_to_hip_pressure(dk_model)
    hp_to_dk = hip_pressure_to_dkm2019(dk_model)
    for he in soil_column['layer']:
        hp = he_to_hp[he]
        dk = hp_to_dk[hp]
        if dk in dkm2019_to_aquifer:
            return { 'elevation' : he,
                     'head_elevation' : hp,
                     'dk2019' : dk,
                     'aquifer' : dkm2019_to_aquifer[dk] }
    raise RuntimeError('No aquifer in soil column')


def get_idx_and_coord(ds, i=None, j=None, x=None, y=None):
    '''Extract the head elevation at a single grid cell

    Parameters
    ----------
    ds : xarray.Dataset
      A HIP head elevation time series. Should contain the following layers
        <N>
      where <N> in [0,10]

    i : int
      Index along X dimension. One of `i` and `x` must be provided.

    j : int
      Index along Y dimension. One of `j` and `y` must be provided.

    x : int
      Value along X dimension. One of `i` and `x` must be provided.
      Ignored if `i` is not None

    y : int
      Value along Y dimension. One of `j` and `y` must be provided.
      Ignored if `j` is not None

    Returns
    -------
    i,j,x,y
    '''
    # TODO: Implement interpolation.
    if i is None and x is None:
        raise ValueError('One of i and x must be set')
    if j is None and y is None:
        raise ValueError('One of j and y must be set')

    if i is None:
        if x > ds['X'].max() or x < ds['X'].min():
            raise ValueError(f'x={x} is outside the bounds {ds["X"].min()}, {ds["X"].max()}')
        diff = (ds['X'] - x)**2
        i = diff.argmin()
        actual_x = int(ds['X'][i])
        if diff[i] > 0:
            warnings.warn(f'Requested x coordinate "{x}" is not grid aligned. '\
                          f'Using {actual_x} instead', UserWarning)
        x = actual_x
    else:
        if x is not None:
            warnings.warn('Ignoring parameter x because i is set', UserWarning)
        x = int(ds['X'][i])

    if j is None:
        if y > ds['Y'].max() or y < ds['Y'].min():
            raise ValueError(f'y={y} is outside the bounds {ds["Y"].min()}, {ds["Y"].max()}')
        diff = (ds['Y'] - y)**2
        j = diff.argmin()
        actual_y = int(ds['Y'][j])
        if diff[j] > 0:
            warnings.warn(f'Requested y coordinate "{y}" is not grid aligned. '\
                          f'Using {actual_y} instead', UserWarning)
        y = actual_y
    else:
        if y is not None:
            warnings.warn('Ignoring parameter y because j is set', UserWarning)
        y = int(ds['Y'][j])

    return i,j,x,y
