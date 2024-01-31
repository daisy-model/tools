'''See extract_soil_column'''
import numpy as np
import pandas as pd
import cfunits
from .units import unit_map
from .util import bounds_check

__all__ = [
    'extract_soil_column'
]


def extract_soil_column(hs_model, x, y,
                        missing_layer_unit=cfunits.Units('0.5m'),
                        base_unit=None,
                        return_terrain_height=False):
    # pylint: disable=too-many-arguments
    '''Extract the soil column at a single grid cell

    Layers with thickness = missing_layer_thickness are excluded.

    Parameters
    ----------
    hs_model : xarray.Dataset
      A HIP hydrostratigraphic model. It is assumed that layers are stored in order of elevation,
      with the first layer being the topmost layer, e.g.
      list(hs_model.data_vars.keys()) == \
          ['Topography', 'CompLayer_1', 'CompLayer_2', ..., 'CompLayer_N']

    x : float
      Value along X dimension.

    y : float
      Value along Y dimension.

    missing_layer_unit : cfunits.Units
      Thickness of layers that should be ignored expressed as a unit.

    base_unit : cfunits.Units
      Convert all all layers to `base_unit`.
      If None use the unit of the first layer as base unit.

    return_terrain_height : bool
      If True also return terrain height

    Returns
    -------
    soil_column or (soil_column, terrain_height)
    soil_column : pandas.DataFrame
      Dataframe with columns
        X : x coordinate of grid cell
        Y : y coordinate of grid cell    
        layer : Name of layer using HIP elevation naming style
        unit : Unit of elevation and thickness
        elevation : Elevation of grid cell
        thickness : Thickness of layer in grid cell

    terrain_height : float

    See also
    --------
    units.unit_map
      Conversion of units from HIP files to cfunits.Units
    '''
    # TODO: Improve handling of units. Units are given as a text string, which seems to be always
    #       set to `EumUnit.eumUmeter`. This does not appear to be recognized by cfunits. So for now
    #       we define our own unit mapping. See `units.py`
    # TODO: Maybe return an xarray.Dataset instead?
    # pylint: disable=duplicate-code, too-many-locals
    bounds_check(hs_model, x, y)
    layer_names = np.array(list(hs_model.data_vars.keys()))
    units = [unit_map[hs_model[layer].units] for layer in layer_names]
    elevation = hs_model.isel(time=0).interp(Y=y, X=x).to_array().values
    
    if base_unit is None:
        base_unit = units[0]
    elif base_unit != units[0]:
        elevation[0] = cfunits.Units.conform(elevation[0], units[0], base_unit)

    # Check that all values are in the same unit. If not try to convert to the same unit
    for idx, (unit, layer) in enumerate(zip(units[1:], layer_names[1:])):
        if base_unit != unit:
            # Units are not the same, but if they are equivalent we can make them conform.
            # If they are not equivalent we dont know what to do.
            # Raising our own ValueError is more informativ than letting cfunits.Units.conform raise
            # the error, because we can specify which layer is wrong.
            if not base_unit.equivalent(unit):
                raise ValueError(f'{layer_names[0]} and {layer} does not have equivalent units'
                                 f'{base_unit}, {unit}')
            elevation[idx+1] = cfunits.Units.conform(elevation[idx+1], unit, base_unit)
    missing_layer_thickness = cfunits.Units.conform(1, missing_layer_unit, base_unit)
    keep = elevation[:-1] - elevation[1:] != missing_layer_thickness
    layer_names = layer_names[np.pad(keep, (1,0), constant_values=0)]
    elevation = elevation[np.pad(keep, (1,0), constant_values=1)]

    # TODO: Change to an xarray
    df = pd.DataFrame({
        'X' : x,
        'Y' : y,
        'layer' : layer_names,
        'unit' : base_unit,
        'elevation' : elevation[1:],
        'thickness' : elevation[:-1] - elevation[1:],
    })
    if return_terrain_height:
        return df, elevation[0]
    return df
