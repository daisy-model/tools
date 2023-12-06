'''See extract_soil_column'''
import numpy as np
import pandas as pd
import cfunits
from .units import unit_map

__all__ = [
    'extract_soil_column'
]


def extract_soil_column(ds, *, i=None, j=None, x=None, y=None, missing_layer_thickness=0.5,
                        base_unit=None):
    # pylint: disable=too-many-arguments
    '''Extract the soil column at a single grid cell

    Layers with thickness = missing_layer_thickness are excluded.

    Parameters
    ----------
    ds : xarray.Dataset
      A HIP elevation map. It is assumed that layers are stored in order of elevation, with the
      first layer being the topmost layer, e.g.
      list(ds.data_vars.keys()) == ['Topography', 'CompLayer_1', 'CompLayer_2', ..., 'CompLayer_N']

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

    missing_layer_thickness : float
      Thickness of layers that should be ignored

    base_unit : cfunits.Units
      Convert all all layers to `base_unit`.
      If None use the unit of the first layer as base unit.
    
    Returns
    -------
    soil_column : pandas.DataFrame
      Dataframe with columns
        X : x coordinate of grid cell
        Y : y coordinate of grid cell    
        elevation_layer_name : Name of layer using HIP elevation naming style
        unit : Unit of elevation and thickness
        elevation : Elevation of grid cell
        thickness : Thickness of layer in grid cell

    See also
    --------
    units.unit_map
      Conversion of units from HIP files to cfunits.Units
    '''
    # TODO: Improve handling of units. Units are given as a text string, which seems to be always
    #       set to `EumUnit.eumUmeter`. This does not appear to be recognized by cfunits. So for now
    #       we define our own unit mapping. See `units.py`
    # TODO: Maybe return an xarray.Dataset instead?
    # pylint: disable=duplicate-code
    if i is None:
        i = (ds['X'] == x).argmax()
    else:
        x = int(ds['X'][i])
    if j is None:
        j = (ds['Y'] == y).argmax()
    else:
        y = int(ds['Y'][j])
    layer_names = np.array(list(ds.data_vars.keys()))
    units = [unit_map[ds[layer].units] for layer in layer_names]
    elevation = ds.isel(time=0, Y=j, X=i).to_array().values
    
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
    keep = elevation[:-1] - elevation[1:] != missing_layer_thickness
    layer_names = layer_names[np.pad(keep, (1,0), constant_values=0)]
    elevation = elevation[np.pad(keep, (1,0), constant_values=1)]
    return pd.DataFrame({
        'X' : x,
        'Y' : y,
        'elevation_layer_name' : layer_names,
        'unit' : base_unit,
        'elevation' : elevation[1:],
        'thickness' : elevation[:-1] - elevation[1:],
    })
