# Tools for the Daisy project

- Data conversion
   * [hip](daisy_tools/hip) - Tools for working with data from [Hydrologisk Informations- og Prognosesystem](https://hip.dataforsyningen.dk/pages/about.html).

## Installation
<details>
<summary>

### Linux
</summary>
These instructions assume you have a working python installation with pip.

1. Use your package manager to install
    - [netcdf](https://www.unidata.ucar.edu/software/netcdf/)
    - [udunits](https://www.unidata.ucar.edu/software/udunits/)
    - [git](https://git-scm.com/download/linux)

    On debian use

        apt install libnetcdf19 libudunits2-0 git

2. (Optional) Create a virtual environment

        python -m venv ~/.venvs/daisy-tools
        source ~/.venvs/daisy-tools/bin/activate

3. Use pip to install daisy tools

        pip install git+https://github.com/daisy-model/tools.git@hip

</details>

<details>
<summary>

### OSX
</summary>
These instructions assume you have a working python installation with pip.

1. Install homebrew. See https://brew.sh/
2. Use homebrew to install
    - [netcdf](https://www.unidata.ucar.edu/software/netcdf/). See https://formulae.brew.sh/formula/netcdf#default
    - [udunits](https://www.unidata.ucar.edu/software/udunits/). See https://formulae.brew.sh/formula/udunits#default
    - [git](https://git-scm.com/download/linux). See https://formulae.brew.sh/formula/git#default

    . <!-- We need a printable character to indicate that the list is done and we are now adding text under point 2. -->

        brew install netcdf udunits git

3. (Optional) Create a virtual environment

        python -m venv ~/.venvs/daisy-tools
        source ~/.venvs/daisy-tools/bin/activate

4. Use pip to install daisy tools

        pip install git+https://github.com/daisy-model/tools.git@hip

</details>

<details>
<summary>

### Windows
</summary>

1. Install [Miniconda](https://docs.conda.io/projects/miniconda/en/latest/miniconda-install.html) or [Anaconda](https://www.anaconda.com/download). Install Miniconda unless you want all the extra stuff in Anaconda.
2. Start the Miniconda/Anaconda Powershell prompt.
3. Download the conda environment file [`environment.yml`](https://github.com/daisy-model/tools/blob/hip/environment.yml) and create a new environment from it using the following commands. This will install all dependencies.

        curl.exe -o daisy-tools-environment.yml https://github.com/daisy-model/tools/blob/hip/environment.yml
        conda env create -f daisy-tools-environment.yml
        rm daisy-tools-environment.yml
        conda activate daisy-tools

4. Set the path to `udunits2.xml` and reactivate the environment

        conda env config vars set UDUNITS2_XML_PATH="$env:CONDA_PREFIX\Library\share\udunits\uduints2.xsml"
        conda activate daisy-tools

5. Download and install daisy tools

        curl.exe -LJO https://github.com/daisy-model/tools/releases/latest/download/daisy_tools.tar.gz
        pip install daisy_tools.tar.gz

</details>

## Usage
See the README in each tool directory.
