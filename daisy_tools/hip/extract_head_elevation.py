'''See extract_head_elevation'''
import pandas as pd
import cfunits
import xarray as xr
from .units import unit_map
from .util import get_idx_and_coord

__all__ = [
    'extract_head_elevation'
]

HEAD_ELEVATION_LAYER = 'head elevation in saturated zone'

def extract_head_elevation(ds, *, i=None, j=None, x=None, y=None, layers=None, base_unit=None):
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

    layers : int or sequence of int
      Extract these layers. If None extract all layers

    base_unit : cfunits.Units
      Convert head_elevation to `base_unit`.
      If None keep the original unit

    Returns
    -------
    head_elevation : pandas.DataFrame
      Dataframe with columns
        X : x coordinate of grid cell
        Y : y coordinate of grid cell
        layer : Name of layer using HIP pressure naming style
        time : Time coordinate of grid cell
        unit : Unit of head_elevation
        head_elevation : Head elevation in grid cell
    '''
    # pylint: disable=duplicate-code, too-many-arguments
    i, j, x, y = get_idx_and_coord(ds, i, j, x, y) # We need i,j for .isel() and x,y for .sel()
    if layers is None:
        layers = ds['layer'] # extract all layers
    elif isinstance(layers, int):
        layers = [layers]
    head_elevation = ds.isel(Y=j, X=i, layer=layers).to_array()
    unit = unit_map[ds[HEAD_ELEVATION_LAYER].units]
    if base_unit is not None and base_unit != unit:
        head_elevation = xr.DataArray(
            cfunits.Units.conform(
                head_elevation, unit, base_unit),
            coords=head_elevation.coords
        )
    else:
        base_unit = unit
    # TODO: Change to an xarray
    return pd.concat([
        pd.DataFrame({
            'X' : x,
            'Y' : y,
            'layer' : int(layer),
            'time' : ds['time'],
            'head_elevation' : head_elevation.sel(layer=layer).values.squeeze(),
            'unit' : base_unit,
        }) for layer in layers
    ])
