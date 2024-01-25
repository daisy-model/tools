'''Conductive properties of DKM2019 layers'''
import cfunits

def get_conductive_properties(dk_model, layer, unit='cm h-1'):
    '''Get conductive properties of specific layer in specific DK2019 model

    Parameters
    ----------
    dk_model : str
      Name of DK-model HIP. Valid model names are {
        'DK1', 'DK2', 'DK3', 'DK4', 'DK5', 'DK6', 'DK7'
      }

    layer : str
      Layer name using DK2019 naming convention. Valid names depend on model, but should be in {
        'kl1', 'kl2', 'kl3', 'kl4', 'kl5'
      }

    unit : str
      Desired unit of conductive properties. The string must be understood by cfunits.Units

    Returns
    -------
    (conductance, unit) or None
      If the layer has defined conductance in the given model, then conductance will be a float
      and unit will be a string. Otherwise None is returned

    Raises
    ------
    ValueError is model is not known.    
    '''
    org_unit = cfunits.Units('m s-1')
    unit = cfunits.Units(unit)
    if dk_model in ('DK1', 'DK2'):
        conductive_properties = {
            'kl1' : 0.00000673,
            'kl2' : 0.0000000267,
            'kl3' : 0.0000000267,
            'kl4' : 0.0000000267,
        }
    elif dk_model == 'DK3':
        conductive_properties = {
            'kl1' : 0.00000125,
            'kl3' : 0.0000000115,
        }
    elif dk_model in ('DK4', 'DK5', 'DK6'):
        conductive_properties = {
            'kl1' : 0.000000602,
            'kl4' : 0.0000000565,
            'kl5' : 0.000000213,
        }
    elif dk_model == 'DK7':
        conductive_properties = {}
        
    try:
        return (cfunits.Units.conform(conductive_properties[layer], org_unit, unit), str(unit))
    except NameError as exc:
        raise ValueError(f'Unknown model: {dk_model}') from exc
    except KeyError:
        return None
