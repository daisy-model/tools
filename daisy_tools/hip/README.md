# Tools for working with data from [Hydrologisk Informations- og Prognosesystem](https://hip.dataforsyningen.dk/pages/about.html).

We are primarily interested in two types of data from HIP. 

 - Soil layers from [HIP – Randbetingelser – Hydrostratigrafisk model](https://www.geodata-info.dk/srv/eng/catalog.search#/metadata/9a4080f7-c6a0-4598-a36b-cabb33181442) (Boundary conditions for hydrostratigraphic model)
 - Time varying presure from [HIP - Randbetingelser - Historiske data](https://www.geodata-info.dk/srv/eng/catalog.search#/metadata/57bd1f18-97b5-4322-aa7d-6ae18d024c0c) (Boundary conditions)

## Tools
<details>
 <summary>

### `prepare_hip_data_for_daisy`
 </summary>

Extract Daisy relevant data from a single cell

#### Usage

<details>
<summary>Windows</summary>

1. Start Anaconda Powershell prompt
2. Activate the conda environment where you installed daisy tools

        conda activate daisy-tools

3. Verify that you have installed daisy tools

        prepare_hip_data_for_daisy --help

4. Test that it works by extracting data from a point

    Assume we have downloaded the following files to the folder `Daisy\HIP\data`

      - the hydrostratigraphic file `DK6_2020_100m_layers.nc`
      - the pressure potential file `dk6_2020_100m_head_10km_630_54.nc`

    Then we can extract data for the coordinate `X = 547070, Y = 6307670` with the following command

        prepare_hip_data_for_daisy Daisy\HIP\data\DK6_2020_100m_layers.nc Daisy\HIP\data\dk6_2020_100m_head_10km_630_54.nc --x 547070 --y 6307670 --outdir Daisy\HIP\out\x547070_y6307670 --unit cm --truncate

    This will create four files in the folder `Daisy\HIP\out\x547070_y6307670`
</details>
</details>

<details>
 <summary>

### `fix_hip_for_qgis`
</summary>

[QGIS](https://qgis.org) expects NetCDF files to be formatted in a particular way, and NetCDF files from HIP are formatted in a different way. After running this tool it should be possible to import a time series from HIP into QGIS as a mesh.
  - **Note regarding CRS information** (2023-11-30). NetCDF files from HIP do not contain CRS information. It is possible to add CRS to the converted file, but QGIS cannot read the file as a mesh if CRS is present. If the file is read as a scalar, time is not interpreted correctly. The best option for now is to manually add CRS in QGIS if needed. It is not clear from the documentation which CRS to use, but the most likely candidate is [EPSG:25832](https://epsg.io/25832)

#### Usage
TODO
</details>

<details>
 <summary>

### `extract_head_elevation`
</summary>

Extract head elevation from a single cell

#### Usage
TODO
</details>

<details>
 <summary>

### `extract_soil_column`
</summary>

Extract soil column from a single cell

#### Usage
TODO
</details>
