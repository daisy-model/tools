'''Utility functions for HIP data extraction and transformation'''
from .layer_names import hip_elevation_to_hip_pressure, hip_pressure_to_dkm2019, dkm2019_to_aquifer

__all__ = [
    'find_topmost_aquifer'
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
