'''See extract_top_aquifer_potential'''
import numpy as np
import xarray as xr
import cfunits
from .units import unit_map
from .layer_names import hip_elevation_to_hip_pressure, hip_pressure_to_dkm2019, \
    dkm2019_to_aquifer

__all__ = [
    'extract_top_aquifer_potential'
]

HEAD_ELEVATION_LAYER = 'head elevation in saturated zone'

def extract_top_aquifer_potential(hs_model, gw_potential, dk_model, base_unit=None,
                                  missing_layer_unit=cfunits.Units('0.5m')):
    '''Extract the potential at the topmost aquifer for all grid points

    Parameters
    ----------
    hs_model : xarray.Dataset
      A HIP hydrostratigraphic model. It is assumed that layers are stored in order of elevation,
      with the first layer being the topmost layer, e.g.
      list(hs_model.data_vars.keys()) == \
          ['Topography', 'CompLayer_1', 'CompLayer_2', ..., 'CompLayer_N']
    
    gw_potential : xarray.Dataset
      A HIP ground water potential time series. Should contain the following layers
        <N>
      where <N> in [0,10]

    dk_model : str
      Name of DK-model HIP. Valid model names are {
        'DK1', 'DK2', 'DK3', 'DK4', 'DK5', 'DK6', 'DK7'
      }

    base_unit : cfunits.Units
      Convert potential to `base_unit`. If None keep the original unit

    missing_layer_unit : cfunits.Units
      Thickness of layers that should be ignored expressed as a unit.

    Returns
    -------
    top_aquifer_potential : xarray.DataArray
    '''
    # Figure out which layer to use in each pixel.
    # We first find all the aquifer layers in the specific DK model
    # Then we find which layers are present in each pixel 
    # Then we select the values from each of the relevant layers

    # Find possible aquifers
    aq_layers_he = _get_possible_aquifers(hs_model, dk_model)

    # Find layers that are present in each pixel
    use_for_pixel = _find_layers_to_use_for_each_pixel(hs_model, gw_potential, missing_layer_unit,
                                                       aq_layers_he)

    # Get the potential
    potential = _get_potential_from_selected_layers(gw_potential, use_for_pixel, dk_model,
                                                    aq_layers_he, base_unit)

    # We need some tweaking to get raster2pgsql to work well
    # - rename X/Y to x/y
    # - transpose the dimensions so we get time, y, x
    potential = xr.DataArray(potential, 
                                dims=['time', 'x', 'y'],
                                coords={
                                    'x' : gw_potential.X.values,
                                    'y' : gw_potential.Y.values,
                                    'time' : gw_potential.time,
                                },
                                attrs={
                                    'units' : str(base_unit),
                                }).transpose('time', 'y', 'x')
    potential['x'].attrs['axis'] = 'x'
    potential['x'].attrs['long_name'] = 'Easting'
    potential['x'].attrs['standard_name'] = 'projection_x_coordinates'
    potential['y'].attrs['axis'] = 'y'
    potential['y'].attrs['long_name'] = 'Northing'
    potential['y'].attrs['standard_name'] = 'projection_y_coordinates'

    return potential


def _get_possible_aquifers(hs_model, dk_model):
    he_to_hp = hip_elevation_to_hip_pressure(dk_model)
    hp_to_dk = hip_pressure_to_dkm2019(dk_model)
    layer_names = np.array(list(hs_model.data_vars.keys()))
    aq_layers = [name for name in layer_names[1:] if hp_to_dk[he_to_hp[name]] in dkm2019_to_aquifer]
    return aq_layers

def _get_elevation(hs_model, gw_potential):
    layer_names = np.array(list(hs_model.data_vars.keys()))
    units = [unit_map[hs_model[layer].units] for layer in layer_names]
    elevation = hs_model.isel(time=0).sel(X=gw_potential.X, Y=gw_potential.Y).to_array().values
    base_unit = units[0]
    # Check that all values are in the same unit. If not try to convert to the same unit
    for idx, (unit, layer) in enumerate(zip(units[1:], layer_names[1:])):
        if base_unit != unit:
            # Units are not the same, but if they are equivalent we can make them conform.
            # If they are not equivalent we dont know what to do.
            # Raising our own ValueError is more informative than letting cfunits.Units.conform
            # raise the error, because we can specify which layer is wrong.
            if not base_unit.equivalent(unit):
                raise ValueError(f'{layer_names[0]} and {layer} does not have equivalent units'
                                 f'{base_unit}, {unit}')
            elevation[idx+1] = cfunits.Units.conform(elevation[idx+1], unit, base_unit)
    return elevation, base_unit


def _find_layers_to_use_for_each_pixel(hs_model, gw_potential, missing_layer_unit, aq_layers_he):
    elevation, elevation_unit = _get_elevation(hs_model, gw_potential)
    missing_layer_thickness = cfunits.Units.conform(1, missing_layer_unit, elevation_unit)
    layer_present = elevation[:-1] - elevation[1:] != missing_layer_thickness
    layer_names = np.array(list(hs_model.data_vars.keys()))
    use_for_pixel = {
        name : layer_present[i] for i, name in enumerate(layer_names[1:]) if name in aq_layers_he
    }
    not_selected = ~use_for_pixel[aq_layers_he[0]]
    for i, aq in enumerate(aq_layers_he[1:]):
        # Only select from this layer, if it has not already been selected in a layer above
        use_for_pixel[aq] = np.logical_and(use_for_pixel[aq], not_selected)
        not_selected = np.logical_xor(not_selected, use_for_pixel[aq])
    return use_for_pixel

def _get_potential_from_selected_layers(gw_potential, use_for_pixel, dk_model, aq_layers_he,
                                        base_unit):
    he_to_hp = hip_elevation_to_hip_pressure(dk_model)
    potential = gw_potential.sel(layer=he_to_hp[aq_layers_he[0]]).to_array().values.squeeze()
    for aq, use in use_for_pixel.items():
        if aq == aq_layers_he[0]:
            continue
        potential[:,use] = gw_potential.sel(layer=he_to_hp[aq]).to_array().squeeze().values[:,use]
    # Maybe change the unit
    gw_unit = unit_map[gw_potential[HEAD_ELEVATION_LAYER].units]
    if gw_unit != base_unit:
        potential = cfunits.Units.conform(potential, gw_unit, base_unit)        
    return potential
