'''DDF file'''
__all__ = [
    'DDF',
    #'save_head_elevation_as_ddf'
]

class DDF():
    def __init__(self, head_elevation):
        self.ddf = [
            ['ddf-0.0 --- pressure table with header'],
            ['---'],
            ['Year', 'Month', 'Day', 'Hour', 'Level'],
            [''    , ''     , ''   , '', head_elevation['unit'][0]],
        ]
        for row in head_elevation.itertuples():
            self.ddf.append([
                row.time.year,
                row.time.month,
                row.time.day,
                row.time.hour,
                row.head_elevation
            ])

    def __str__(self):
        return '\n'.join(['\t'.join(map(str, row)) for row in self.ddf])

    def save(self, outpath):
        with open(outpath, 'w') as out:
            print(str(self), file=out)
        
