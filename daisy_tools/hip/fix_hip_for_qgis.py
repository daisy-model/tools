'''Make netCDF files from HIP (https://hip.dataforsyningen.dk/) readable by QGIS (https://qgis.org)

We need to fix coordinates and dates.
 - QGIS assumes the date reference is no earlier than 1753 and HIP use 0001.
 - QGIS needs to be explicitly told that coords X and Y are coordinates

By default we do not add CRS info, because if a CRS data variable is present, then QGIS cannot load
the data as a mesh. And if it is not loaded as a mesh, time will be interpreted as layers instead of
as time.
According to

  https://www.geodata-info.dk/srv/eng/catalog.search#/metadata/57bd1f18-97b5-4322-aa7d-6ae18d024c0c
  https://www.geodata-info.dk/srv/eng/catalog.search#/metadata/9a4080f7-c6a0-4598-a36b-cabb33181442

the CRS should be EPSG:4326 (https://epsg.io/4326). But the text in

 https://www.geodata-info.dk/srv/eng/catalog.search#/metadata/57bd1f18-97b5-4322-aa7d-6ae18d024c0cs

states that coordinates X and Y follow the UTM coordinate system with Y positive to north, and x
positive to east. And the coordinates are stored as meters with values that appear correct for UTM
zone 32N.
According to

  https://www.sdfe.dk/media/2917583/001-etrs89-utm.pdf

the primary projection used in Denmark is UTM/ETRS89 and Denmark is covered by zones 32 and 33. But
it seems to be common to just use zone 32. So in summary, the CRS should be

ETRS89 / UTM zone 32N (EPSG:25832) (https://epsg.io/25832)

'''
import argparse
import numpy as np
import xarray as xr
import cftime

__all__ = [
    'fix_hip_for_qgis'
]

def main():
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

def fix_hip_for_qgis(ds, set_crs_epsg_25832):
    '''Fix a dataset from HIP such that it can be read nicely into QGIS.
    The dataset is updated in place
    
    Parameters
    ----------
    ds : xarray.Dataset
      A HIP Dataset containing 'time', 'X', and 'Y'

    set_crs : Bool
      If True set CRS info

    Returns
    --------
    xarray.Dataset with corrections
    '''
    new_reference_time = cftime.datetime(1900, 1, 1)
    # Fix time
    offset = cftime.date2num(
        new_reference_time,
        units=ds['time'].units,
        calendar=ds['time'].calendar,
    )
    new_time = ds['time'] - offset
    new_time.attrs['units'] = f'hours since {new_reference_time}'
    new_time.attrs['calendar'] = ds['time'].calendar
    ds['time'] = new_time

    # Fix coords
    ds['X'].attrs['axis'] = 'X'
    ds['X'].attrs['long_name'] = 'Easting'
    ds['X'].attrs['standard_name'] = 'projection_x_coordinates'
    ds['Y'].attrs['axis'] = 'Y'
    ds['Y'].attrs['long_name'] = 'Northing'
    ds['Y'].attrs['standard_name'] = 'projection_y_coordinates'

    if set_crs_epsg_25832:
        # Each data var must reference a CRS variable in a 'grid_mapping' attribute
        for var in ds.data_vars:
            ds[var].attrs['grid_mapping'] = 'crs' # Does not need to be 'crs'
        # I *think* QGIS uses gdal to read netCDF files. From
        #   https://gdal.org/drivers/raster/netcdf.html#georeference
        # we have that gdal supports the `crs_wkt` attribute from version 3.4. Earlier versions can
        # use the attribute `spatial_ref`.
        ds['crs'] = xr.DataArray(
            np.zeros(0, dtype='|S1'), # Empty zero-terminated string
            attrs = {
                'spatial_ref' : EPSG_25832_WKT,
                'grid_mapping_name' : 'transverse_mercator',
                'crs_wkt' : EPSG_25832_WKT,
            }
        )
    return ds

EPSG_25832_WKT = '''
PROJCS["ETRS89 / UTM zone 32N",
    GEOGCS["ETRS89",
        DATUM["European_Terrestrial_Reference_System_1989",
            SPHEROID["GRS 1980",6378137,298.257222101,
                AUTHORITY["EPSG","7019"]],
            TOWGS84[0,0,0,0,0,0,0],
            AUTHORITY["EPSG","6258"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.0174532925199433,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4258"]],
    PROJECTION["Transverse_Mercator"],
    PARAMETER["latitude_of_origin",0],
    PARAMETER["central_meridian",9],
    PARAMETER["scale_factor",0.9996],
    PARAMETER["false_easting",500000],
    PARAMETER["false_northing",0],
    UNIT["metre",1,
        AUTHORITY["EPSG","9001"]],
    AXIS["Easting",EAST],
    AXIS["Northing",NORTH],
    AUTHORITY["EPSG","25832"]]
'''


if __name__ == '__main__':
    main()
