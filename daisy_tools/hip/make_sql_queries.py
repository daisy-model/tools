'''Create SQL queries from a nc file containing the output from running
`extract_top_aquifer_potential`. Two queries are generated, one for creating the table and one for
inserting the potential in an already created table.
The queries need to be run manually, e.g.
    sudo -u <db-user> psql -d <db-name> -f <outdir>/create.sql
    sudo -u <db-user> psql -d <db-name> -f <outdir>/insert.sql
'''
import argparse
import os
import subprocess
import sys
import xarray as xr

def main():
    # pylint: disable=missing-function-docstring
    parser = argparse.ArgumentParser(
        'Create SQL queries for inserting the contents of a raster file into postgres'
    )
    parser.add_argument('nc_file', type=str, help='Path to pressure file')
    parser.add_argument('outdir', type=str, help='Output directory')
    parser.add_argument('--table', type=str, help='Table name', default="top_aquifer_potential")
    parser.add_argument('--srid', type=int, help='SRID of coordinate system used in nc_file',
                        default=25832)

    args = parser.parse_args()
    try:
        os.makedirs(args.outdir, exist_ok=True)
        # First create the SQL for creating the table
        cmd = ["raster2pgsql", "-I", "-n", "time", "-s", str(args.srid), args.nc_file, args.table]
        result = subprocess.run(cmd + ["-p"], capture_output=True, encoding='utf-8', check=True)
        with open(os.path.join(args.outdir, 'create.sql'), 'w', encoding='utf-8') as out:
            for n, line in enumerate(result.stdout.split('\n')):
                if n == 1:
                    line = line.replace('text', 'timestamptz, "units" text')
                print(line, file=out)

        # Then create insert query.
        cmd += ["-a", "-b"]
        # We need to add the timestamp manually
        with xr.open_dataarray(args.nc_file) as da:
            timepoints = da['time'].values
            units = da.attrs['units']
        with open(os.path.join(args.outdir, 'insert.sql'), 'w', encoding='utf-8') as out:
            print('BEGIN;', file=out)
            for i, timepoint in enumerate(timepoints):
                result = subprocess.run(cmd + [str(i+1)], capture_output=True, encoding='utf-8',
                                        check=True)
                line = result.stdout.split('\n')[1]
                # Add units to first part of insert statement
                idx = line.find('time"') + len('time"')
                line = line[:idx] + ',"units"' + line[idx:]
                idx = line.rfind(",") + 1
                line = line[:idx] + f"'{timepoint}','{units}');"
                print(line, file=out)
            print('CREATE INDEX ON "top_aquifer_potential" USING gist (st_convexhull("rast"));',
                  'ANALYZE "top_aquifer_potential";',
                  'END;', file=out, sep='\n')
    except subprocess.CalledProcessError as e:
        print(e)
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
