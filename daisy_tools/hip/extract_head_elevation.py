'''See extract_head_elevation'''
import pandas as pd
import cfunits
import xarray as xr
from .units import unit_map
from .util import bounds_check

__all__ = [
    'extract_head_elevation'
]

HEAD_ELEVATION_LAYER = 'head elevation in saturated zone'

def extract_head_elevation(gw_potential, x, y, layers=None, base_unit=None):
    '''Extract the head elevation at a single grid cell

    Parameters
    ----------
    gw_potential : xarray.Dataset
      A HIP ground water potential time series. Should contain the following layers
        <N>
      where <N> in [0,10]

    x : float
      Value along X dimension.

    y : float
      Value along Y dimension.

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
    bounds_check(gw_potential, x, y)
    if layers is None:
        layers = gw_potential['layer'] # extract all layers
    elif isinstance(layers, int):
        layers = [layers]
    head_elevation = gw_potential.isel(layer=layers).interp(X=x, Y=y).to_array()
    unit = unit_map[gw_potential[HEAD_ELEVATION_LAYER].units]
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
            'time' : gw_potential['time'],
            'head_elevation' : head_elevation.sel(layer=layer).values.squeeze(),
            'unit' : base_unit,
        }) for layer in layers
    ])
