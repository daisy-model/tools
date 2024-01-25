'''Entry points for executables'''
import argparse
import os
import xarray as xr
import cfunits
from .extract_head_elevation import extract_head_elevation
from .extract_soil_column import extract_soil_column
from .fix_hip_for_qgis import fix_hip_for_qgis
from .prepare_hip_data_for_daisy import prepare_hip_data_for_daisy
from .ddf import DDFPressure

def run_fix_hip_for_qgis():
    # pylint: disable=missing-function-docstring
    # TODO: Consider getting WKT from https://epsg.io/<EPSG-number>.wkt
    parser = argparse.ArgumentParser('Extract head elevation')
    parser.add_argument('inpath', type=str)
    parser.add_argument('outpath', type=str)
    parser.add_argument('--set-crs-epsg-25832', action='store_true',
                        help='Write CRS info to the dataset. Beware that QGIS cannot read the file '
                        'as a mesh if this is present.')
    args = parser.parse_args()

    # We need to not decode times, so we can easily calculate a new offset
    with xr.open_dataset(args.inpath, decode_times=False) as ds:
        fix_hip_for_qgis(ds, args.set_crs_epsg_25832).to_netcdf(args.outpath)
    return 0


def run_extract_head_elevation():
    # pylint: disable=missing-function-docstring    
    parser = argparse.ArgumentParser('Extract head elevation from HIP head elevation time series')
    parser.add_argument('inpath', type=str)
    parser.add_argument('--outpath', type=str, default=None)
    parser.add_argument('--x', type=float, default=None)
    parser.add_argument('--y', type=float, default=None)
    parser.add_argument('--base-unit', type=str, default=None)
    args = parser.parse_args()

    with xr.open_dataset(args.inpath) as ds:
        params = {}
        if args.base_unit is not None:
            params['base_unit'] = cfunits.Units(args.base_unit)
        head_elevation = extract_head_elevation(ds, args.x, args.y, **params)
        if args.outpath is None:
            print(head_elevation)
        else:
            head_elevation.to_csv(args.outpath)

def run_extract_soil_column():
    # pylint: disable=missing-function-docstring    
    parser = argparse.ArgumentParser('Extract soil column from HIP elevation map')    
    parser.add_argument('inpath', type=str)
    parser.add_argument('--outpath', type=str, default=None)
    parser.add_argument('--x', type=float, default=None)
    parser.add_argument('--y', type=float, default=None)
    parser.add_argument('--base-unit', type=str, default=None)
    args = parser.parse_args()

    with xr.open_dataset(args.inpath) as ds:
        params = {}
        if args.base_unit is not None:
            params['base_unit'] = cfunits.Units(args.base_unit)
        soil_column = extract_soil_column(ds, args.x, args.y, **params)
        if args.outpath is None:
            print(soil_column)
        else:
            soil_column.to_csv(args.outpath)


def run_prepare_hip_data_for_daisy():
    # pylint: disable=missing-function-docstring
    parser = argparse.ArgumentParser('Prepare HIP data for Daisy')
    parser.add_argument('topography', type=str, help='Path to topography file')
    parser.add_argument('head_elevation', type=str, help='Path to head elevation file')
    parser.add_argument('--x', type=float, required=True, help='x coordinate to extract')
    parser.add_argument('--y', type=float, required=True, help='y coordinate to extract')
    parser.add_argument('--dk-model', type=int, choices=(1,2,3,4,5,6,7), default=None,
                        help='Which DK model the data is from. If None, try to guess from '
                        'topography filename')
    parser.add_argument('--outdir', type=str, default=None)
    parser.add_argument('--unit', type=str, default='cm',
                        help='Unit of measurements. Default is cm.')
    parser.add_argument('--truncate', action='store_true',
                        help='If set, truncate measurements to 0 decimals')
    args = parser.parse_args()

    try:
        if args.outdir is not None:
            os.makedirs(args.outdir, exist_ok=True)

        unit = cfunits.Units(args.unit)
        if args.dk_model is None:
            args.dk_model = int(os.path.basename(args.topography)[2])
            assert 1 <= args.dk_model <= 7
        dk_model = f'DK{args.dk_model}'
        with xr.open_dataset(args.topography) as ds_topo, \
             xr.open_dataset(args.head_elevation) as ds_head:
            soil_column, head_elevation = \
                prepare_hip_data_for_daisy(dk_model, ds_topo, ds_head, args.x, args.y, unit)

        if args.truncate:
            head_elevation['head_elevation'] = head_elevation['head_elevation'].round(0).astype(int)
            cols = ['terrain_height', 'elevation', 'thickness']
            soil_column[cols] = soil_column[cols].round(0).astype(int)
        
        if args.outdir is None:
            line = '============================= {0:^20s} ============================='
            print(line.format('Soil column'))
            print(soil_column, '\n')
            print(line.format('Head elevation'))
            print(head_elevation, '\n')
        else:
            soil_column.to_csv(os.path.join(args.outdir, 'soil_column.csv'), index=False)
            head_elevation.to_csv(os.path.join(args.outdir, 'pressure.csv'), index=False)
            DDFPressure(head_elevation).save(os.path.join(args.outdir, 'pressure_table.ddf'))
            top_aquitard = soil_column.loc[soil_column['top_aquitard']]
            top_aquitard[
                ['dk_layer', 'elevation', 'thickness', 'unit', 'conductive_properties']
            ].to_csv(os.path.join(args.outdir, 'top_aquitard.csv'), index=False)
    except Exception as e:
        print(e)
        return 1
    return 0
