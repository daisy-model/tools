'''Example script for querying the database created with `make_sql_queries`
It is assumed that the created table is named top_aquifer_potential'''
import argparse
import psycopg
import cfunits
import numpy as np
import matplotlib.pyplot as plt

def main():
    # pylint: disable=missing-function-docstring
    parser = argparse.ArgumentParser()
    parser.add_argument('longitude', type=float)
    parser.add_argument('latitude', type=float)    
    parser.add_argument('--unit', type=str, default='cm', help='Display potential in this unit')
    parser.add_argument('--outpath', type=str,
                        help='If provided write the potential to this file, otherwise plot it')
    parser.add_argument('--db-host', type=str, default='localhost')
    parser.add_argument('--db-name', type=str, default='hip')
    parser.add_argument('--db-user', type=str, default='postgres')
    parser.add_argument('--db-password', type=str, default='postgres')
    args = parser.parse_args()

    connection_string = f"host={args.db_host} dbname={args.db_name} user={args.db_user} " \
        f"password={args.db_password}"
    
    with psycopg.connect(connection_string) as conn:
        # pylint complains about this, but it is correct according to the docs...
        time, potential = _get_potential(conn, args.longitude, args.latitude, args.unit)
        conn.commit()
    if args.outpath is None:
        plt.plot(time, potential)
        plt.ylabel(str(args.unit))
        plt.show()
    else:
        ddf = _format_as_ddf(time, potential, args.unit)
        with open(args.outpath, 'w', encoding='utrf-8') as out:
            print('\n'.join(['\t'.join(map(str, row)) for row in ddf]), file=out)
        
def _format_as_ddf(time, potential, unit):
    ddf = [
        ['ddf-0.0 --- pressure table with header'],
        ['---'],
        ['Year', 'Month', 'Day', 'Hour', 'Level'],
        [''    , ''     , ''   , '', unit],
    ]
    for t, p, in zip(time, potential):
        ddf.append([
            t.year,
            t.month,
            t.day,
            t.hour,
            p
        ])
    return ddf
        

def _get_potential(conn, longitude, latitude, unit):
    with conn.cursor() as cur:
        q = """SELECT time, units, ST_Value(rast, p)
        FROM top_aquifer_potential
        JOIN ST_Transform(ST_Point(%(longitude)s, %(latitude)s, 4326), ST_SRID(rast)) as p
        ON ST_Intersects(p, ST_ConvexHull(rast))
        WHERE ST_Value(rast, p) IS NOT NULL"""
        params = {
            'longitude' : longitude,
            'latitude' : latitude
        }
        cur.execute(q, params)
        result = cur.fetchall()        
    if len(result) == 0:
        return [], []
    result = list(zip(*result))
    time = np.array(result[0])
    units = result[1]
    potential = np.array(result[2])
    unit_change = units != unit
    if np.any(unit_change):
        to_unit = cfunits.Units(unit)
        if len(np.unique(units)) == 1:
            from_unit = cfunits.Units(units[0])
            potential = cfunits.Units.conform(potential, from_unit, to_unit)
    return time, potential
                    
if __name__ == '__main__':
    main()

# Hit two tiles at boundary. Only one should be returned. Note that values are very low
# python3 ../tools/daisy_tools/hip/db_con_test.py 12.313354034302591 55.36133764132123

# Only hit one tile. Note that values here are more sensible
# python3 ../tools/daisy_tools/hip/db_con_test.py 12.31335403430259 55.36133764132123
