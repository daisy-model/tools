'''Handle units parsed from HIP NetCDF files'''
import cfunits

__all__ = [
    'unit_map'
]

unit_map = {
    'EumUnit.eumUmeter' : cfunits.Units('meter')
}
