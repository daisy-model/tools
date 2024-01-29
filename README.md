# Tools for the Daisy project

- Data conversion
   * [hip](daisy_tools/hip) - Tools for working with data from [Hydrologisk Informations- og Prognosesystem](https://hip.dataforsyningen.dk/pages/about.html).

## Installation
These instructions assume that you have a working python installation with pip.

### Linux

Use your package manager to install [netcdf](https://www.unidata.ucar.edu/software/netcdf/) and [udunits](https://www.unidata.ucar.edu/software/udunits/).

On debian use

    apt install libnetcdf19 libudunits2-0

(Optional) Create a virtual environment

    python -m venv ~/.venvs/daisy-tools
    source ~/.venvs/daisy-tools/bin/activate

Install the package with pip

    pip install git+https://github.com/daisy-model/tools.git@hip

### OSX

1. Install homebrew. See https://brew.sh/
2. Install udunits with homebrew. See https://formulae.brew.sh/formula/udunits#default
3. Install netcdf with homebrew. See https://formulae.brew.sh/formula/netcdf#default

(Optional) Create a virtual environment

    python -m venv ~/.venvs/daisy-tools
    source ~/.venvs/daisy-tools/bin/activate

Install the package with pip

    pip install git+https://github.com/daisy-model/tools.git@hip

### Windows
TODO
