'''DDF representations of HIP data'''
__all__ = [
    'DDFPressure',
]

class DDFPressure():
    '''Represent head elevation as a DDF string

    Parameters
    ----------
    head_elevation : pandas.DataFrame
      Extracted head elevation
    '''
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
        '''Save the DDF string representation to a file

        outpath : str          
        '''
        with open(outpath, 'w', encoding='utf8') as out:
            print(str(self), file=out)
        
