'''See extract_head_elevation'''
import pandas as pd
import cfunits
from .units import unit_map

__all__ = [
    'extract_head_elevation'
]

HEAD_ELEVATION_LAYER = 'head elevation in saturated zone'

def extract_head_elevation(ds, *, i=None, j=None, x=None, y=None, base_unit=None):
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

    base_unit : cfunits.Units
      Convert head_elevation to `base_unit`.
      If None keep the original unit

    Returns
    -------
    head_elevation : pandas.DataFrame
      Dataframe with columns
        X : x coordinate of grid cell
        Y : y coordinate of grid cell
        pressure_layer_name : Name of layer using HIP pressure naming style
        time : Time coordinate of grid cell
        unit : Unit of head_elevation
        head_elevation : Head elevation in grid cell
    '''
    # pylint: disable=duplicate-code, too-many-arguments
    if i is None:
        i = (ds['X'] == x).argmax()
    else:
        x = int(ds['X'][i])
    if j is None:
        j = (ds['Y'] == y).argmax()
    else:
        y = int(ds['Y'][j])
    head_elevation = ds.isel(Y=j, X=i).to_array()
    unit = unit_map[ds[HEAD_ELEVATION_LAYER].units]
    if base_unit is not None and base_unit != unit:
        cfunits.Units.conform(head_elevation, unit, base_unit)
    else:
        base_unit = unit
    
    return pd.concat([
        pd.DataFrame({
            'X' : x,
            'Y' : y,
            'pressure_layer_name' : int(layer),
            'time' : ds['time'],
            'head_elevation' : head_elevation.isel(layer=layer).values.squeeze(),
            'unit' : base_unit,
        }) for layer in ds['layer']
    ])
