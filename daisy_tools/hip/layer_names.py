'''Convert between different names for the same layers'''

__all__ = [
    'hip_elevation_to_hip_pressure',
    'hip_elevation_to_dkm2019',
    'hip_pressure_to_dkm2019',
    'dkm2019_to_aquifer',
    'dkm2019_aquitard',
]

dkm2019_to_aquifer = {
    'ks1' : 'glw1',
    'ks2' : 'glw2',
    'ks3' : 'glw3',
    'ks4' : 'glw4',
    'kalk' : 'glw6',
    'kl1/kl2 + ks1/ks2' : 'glw1',
    'ks5 - ps1' : 'glw4',
    'ps2 - ps6' : 'glw5',
    'blag1' : 'glw1',
    'blag2' : 'glw2',
    'blag3' : 'glw3',
    'blag4' : 'glw4',
    'blag5' : 'glw5',
    'blag6' : 'glw6',
}

dkm2019_aquitard = {
    'kl1',
    'kl2',
    'kl3',
    'kl4',
    'kl5',
}


def hip_elevation_to_dkm2019(model):
    '''Convert layer names from HIP elevation to DKM2019 layer names

    Valid keys in the returned dict are of the form CompLayer_<N> with <N> depending on the model:
        1-11 for DK1, DK2, DK4, DK5, DK6
        1-9 for DK3
        1-7 for DK7

    Parameters
    ----------
    model : str
      Name of DK-model HIP. Valid model names are {
        'DK1', 'DK2', 'DK3', 'DK4', 'DK5', 'DK6', 'DK7'
      }
    
    Returns
    -------
    layer_map : dict of int, str
      Mapping from elevation names to DK-model2019 names
    '''
    p2dk = hip_pressure_to_dkm2019(model)
    return { k : p2dk[v] for k,v in hip_elevation_to_hip_pressure(model).items() }

def hip_elevation_to_hip_pressure(model):
    '''Convert layer names from HIP elevation to layer numbers in HIP pressure
    TODO: Figure out if this is documented anywhere

    Valid keys in the returned dict are of the form CompLayer_<N> with <N> depending on the model:
        1-11 for DK1, DK2, DK4, DK5, DK6
        1-9 for DK3
        1-7 for DK7

    Parameters
    ----------
    model : str
      Name of DK-model HIP. Valid model names are {
        'DK1', 'DK2', 'DK3', 'DK4', 'DK5', 'DK6', 'DK7'
      }
    

    Returns
    -------
    layer_map : dict of str : int
      Mapping from elevation to pressure names
    '''
    if model in ('DK1', 'DK2', 'DK4', 'DK5', 'DK6'):
        layer_map = {
            'CompLayer_1'  : 10,
            'CompLayer_2'  :  9,
            'CompLayer_3'  :  8,
            'CompLayer_4'  :  7,
            'CompLayer_5'  :  6,
            'CompLayer_6'  :  5,
            'CompLayer_7'  :  4,
            'CompLayer_8'  :  3,
            'CompLayer_9'  :  2,
            'CompLayer_10' :  1,
            'CompLayer_11' :  0,
        } 
    elif model == 'DK3':
        layer_map = {
            'CompLayer_1'  :  8,
            'CompLayer_2'  :  7,
            'CompLayer_3'  :  6,
            'CompLayer_4'  :  5,
            'CompLayer_5'  :  4,
            'CompLayer_6'  :  3,
            'CompLayer_7'  :  2,
            'CompLayer_8'  :  1,
            'CompLayer_9'  :  0,
        } 
    elif model == 'DK7':
        layer_map = {
            'CompLayer_1'  :  6,
            'CompLayer_2'  :  5,
            'CompLayer_3'  :  4,
            'CompLayer_4'  :  3,
            'CompLayer_5'  :  2,
            'CompLayer_6'  :  1,
            'CompLayer_7'  :  0,
        } 
    else:
        raise ValueError(f'Unknown model: {model}')
    return layer_map
    


def hip_pressure_to_dkm2019(model):
    '''Convert layer numbers from HIP pressure to DKM2019 layer names
    Based on Tabel 1 at https://hip.dataforsyningen.dk/pages/help.html

    Valid keys in the returned dict are integers and depend on the model:
        0-10 for DK1, DK2, DK4, DK5, DK6
        0-8 for DK3
        0-6 for DK7

    Parameters
    ----------
    model : str
      Name of DK-model HIP. Valid model names are {
        'DK1', 'DK2', 'DK3', 'DK4', 'DK5', 'DK6', 'DK7'
      }
    
    Returns
    -------
    layer_map : dict of int, str
      Mapping from pressure names to DK-model2019 names
    '''
    if model in ('DK1', 'DK2'):
        layer_map = {
            10 : 'top2m',
            9 : 'kl1',
            8 : 'ks1', # glw1
            7 : 'kl2',
            6 : 'ks2', # glw2
            5 : 'kl3',
            4 : 'ks3', # glw3
            3 : 'kl4',
            2 : 'ks4', # glw4
            1 : 'kl5',
            0 : 'kalk', # glw6
        } 
    elif model == 'DK3':
        layer_map = {
            8 : 'top2m',
            7 : 'kl1',
            6 : 'ks1', # glw1
            5 : 'kl2',
            4 : 'ks2', # glw2
            3 : 'kl3',
            2 : 'ks3', # glw3
            1 : 'kl4',
            0 : 'kalk', # glw6
        } 
    elif model in ('DK4', 'DK5', 'DK6'):
        layer_map = {
            10 : 'top2m',
            9 : 'kl1/kl2 + ks1/ks2', # glw1
            8 : 'kl3',
            7 : 'ks3', # glw2
            6 : 'kl4',
            5 : 'ks4', # glw3
            4 : 'kl5',
            3 : 'ks5 - ps1', # glw4
            2 : 'pl2',
            1 : 'ps2 - ps6', # glw5
            0 : 'kalk', # glw6
        }        
    elif model == 'DK7':
        layer_map = {
            6 : 'top2m',
            5 : 'blag1', # glw1
            4 : 'blag2', # glw2
            3 : 'blag3', # glw3
            2 : 'blag4', # glw4
            1 : 'blag5', # glw5
            0 : 'blag6', # glw6
        } 
    else:
        raise ValueError(f'Unknown model: {model}')
    return layer_map
