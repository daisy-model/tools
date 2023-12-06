'''Entry points for executables'''
import argparse
import xarray as xr
import cfunits
from .extract_head_elevation import extract_head_elevation
from .extract_soil_column import extract_soil_column

def xy_ij_params(args, ds):
    '''Handle xy/ix params for the runners'''
    params = {}
    if args.x is None:
        params['i'] = len(ds['X'])//2
    else:
        params['x'] = args.x
    if args.y is None:
        params['j'] = len(ds['Y'])//2
    else:
        params['y'] = args.y
    return params

def run_extract_head_elevation():
    # pylint: disable=missing-function-docstring    
    parser = argparse.ArgumentParser('Extract head elevation from HIP head elevation time series')
    parser.add_argument('inpath', type=str)
    parser.add_argument('--outpath', type=str, default=None)
    parser.add_argument('--x', type=int, default=None)
    parser.add_argument('--y', type=int, default=None)
    parser.add_argument('--base-unit', type=str, default=None)
    args = parser.parse_args()

    with xr.open_dataset(args.inpath) as ds:
        params = xy_ij_params(args, ds)
        if args.base_unit is not None:
            params['base_unit'] = cfunits.Units(args.base_unit)
        head_elevation = extract_head_elevation(ds, **params)
        if args.outpath is None:
            print(head_elevation)
        else:
            head_elevation.to_csv(args.outpath)

def run_extract_soil_column():
    # pylint: disable=missing-function-docstring    
    parser = argparse.ArgumentParser('Extract soil column from HIP elevation map')    
    parser.add_argument('inpath', type=str)
    parser.add_argument('--outpath', type=str, default=None)
    parser.add_argument('--x', type=int, default=None)
    parser.add_argument('--y', type=int, default=None)
    parser.add_argument('--base-unit', type=str, default=None)
    args = parser.parse_args()

    with xr.open_dataset(args.inpath) as ds:
        params = xy_ij_params(args, ds)
        if args.base_unit is not None:
            params['base_unit'] = cfunits.Units(args.base_unit)
        soil_column = extract_soil_column(ds, **params)
        if args.outpath is None:
            print(soil_column)
        else:
            soil_column.to_csv(args.outpath)

            
            
