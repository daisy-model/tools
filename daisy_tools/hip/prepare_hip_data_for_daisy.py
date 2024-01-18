'''Extract Daisy relevant data from HIP data'''
from .util import find_topmost_aquifer
from .extract_head_elevation import extract_head_elevation
from .extract_soil_column import extract_soil_column

def prepare_hip_data_for_daisy(dk_model, topography, head_elevation, x, y, unit):
    # pylint: disable=too-many-arguments
    '''
    Parameters
    ----------
    dk_model : str
      Name of DK-model HIP. Valid model names are {
        'DK1', 'DK2', 'DK3', 'DK4', 'DK5', 'DK6', 'DK7'
      }

    topography : xarray.Dataset
      A HIP elevation map. It is assumed that layers are stored in order of elevation, with the
      first layer being the topmost layer, e.g.
      list(ds.data_vars.keys()) == ['Topography', 'CompLayer_1', 'CompLayer_2', ..., 'CompLayer_N']

    head_elevation : xarray.Dataset
      A HIP head elevation time series. Should contain the following layers
        <N>
      where <N> in [0,10]

    x, y : int
      Values along X and Y dimension.

    unit : cfunits.Units
      Express values in this unit

    Returns
    -------
    soil_column, terrain_height, top_aquifer, head_elevation

    soil_column : pandas.DataFrame
    terrain_height : float
    top_aquifer : dict of str
    head_elevation : pandas.DataFrame  
    
    See also
    --------
    extract_head_elevation, extract_soil_column, layer_names, util
    '''
    soil_column, terrain_height = extract_soil_column(topography, x=x, y=y,
                                                      return_terrain_height=True,
                                                      base_unit=unit)
    top_aquifer = find_topmost_aquifer(dk_model, soil_column)
    soil_column['dk_model'] = dk_model
    soil_column['aquifer'] = soil_column['layer'] == top_aquifer['elevation']
    soil_column['terrain_height'] = terrain_height
    soil_column = soil_column[
        ['dk_model', 'X', 'Y', 'terrain_height', 'layer', 'aquifer', 'elevation', 'thickness',
         'unit']
    ]
    head_elevation = extract_head_elevation(head_elevation, x=x, y=y,
                                            layers=top_aquifer['head_elevation'],
                                            base_unit=unit)
    head_elevation['pressure'] = terrain_height - head_elevation['head_elevation']
    head_elevation = head_elevation[['time', 'pressure', 'unit']]
    return soil_column, terrain_height, top_aquifer, head_elevation
