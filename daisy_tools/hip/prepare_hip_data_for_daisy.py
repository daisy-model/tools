'''Extract Daisy relevant data from HIP data'''
from .util import find_topmost_aquifer, find_topmost_aquitard
from .extract_head_elevation import extract_head_elevation
from .extract_soil_column import extract_soil_column
from .conductive_properties import get_conductive_properties
from .layer_names import hip_elevation_to_dkm2019, hip_pressure_to_dkm2019

__all__ = [
    'prepare_hip_data_for_daisy'
]

def prepare_hip_data_for_daisy(dk_model, hs_model, gw_potential, x, y, unit):
    # pylint: disable=too-many-arguments
    '''
    Parameters
    ----------
    dk_model : str
      Name of DK-model HIP. Valid model names are {
        'DK1', 'DK2', 'DK3', 'DK4', 'DK5', 'DK6', 'DK7'
      }

    hs_model : xarray.Dataset
      A HIP hydrostratigraphic model. It is assumed that layers are stored in order of elevation,
      with the first layer being the topmost layer, e.g.
      list(hs_model.data_vars.keys()) == \
          ['Topography', 'CompLayer_1', 'CompLayer_2', ..., 'CompLayer_N']

    gw_potential : xarray.Dataset
      A HIP ground water potential time series. Should contain the following layers
        <N>
      where <N> in [0,10]

    x, y : int
      Values along X and Y dimension.

    unit : cfunits.Units
      Express values in this unit

    Returns
    -------
    soil_column, head_elevation
      soil_column : pandas.DataFrame
      head_elevation : pandas.DataFrame  
    
    See also
    --------
    extract_head_elevation, extract_soil_column, layer_names, util
    '''
    soil_column, terrain_height = extract_soil_column(hs_model, x=x, y=y,
                                                      return_terrain_height=True,
                                                      base_unit=unit)
    top_aquifer = find_topmost_aquifer(dk_model, soil_column)
    top_aquitard = find_topmost_aquitard(dk_model, soil_column)
    soil_column['dk_model'] = dk_model
    soil_column['top_aquifer'] = soil_column['layer'] == top_aquifer['elevation']
    soil_column['top_aquitard'] = soil_column['layer'] == top_aquitard['elevation']
    soil_column['terrain_height'] = terrain_height
    soil_column = soil_column[
        ['dk_model', 'X', 'Y', 'terrain_height', 'layer', 'top_aquifer', 'top_aquitard',
         'elevation', 'thickness', 'unit']
    ]
    soil_column['dk_layer'] = soil_column['layer'].replace(hip_elevation_to_dkm2019(dk_model))
    soil_column['conductive_properties'] = soil_column['dk_layer'].apply(
        lambda layer: get_conductive_properties(dk_model, layer)
    )
    head_elevation = extract_head_elevation(gw_potential, x=x, y=y,
                                            layers=top_aquifer['head_elevation'],
                                            base_unit=unit)
    head_elevation['dk_layer'] = head_elevation['layer'].replace(hip_pressure_to_dkm2019(dk_model))
    head_elevation['head_elevation'] = head_elevation['head_elevation'] - terrain_height
    return soil_column, head_elevation
