# Tools for working with data from [https://hip.dataforsyningen.dk/pages/about.html](Hydrologisk Informations- og Prognosesystem).

We are primarily interested in two types of data from HIP. 

 - Soil layers from [HIP – Randbetingelser – Hydrostratigrafisk model](https://www.geodata-info.dk/srv/eng/catalog.search#/metadata/9a4080f7-c6a0-4598-a36b-cabb33181442) (Boundary conditions for hydrostratigraphic model)
 - Time varying presure from [HIP - Randbetingelser - Historiske data](https://www.geodata-info.dk/srv/eng/catalog.search#/metadata/57bd1f18-97b5-4322-aa7d-6ae18d024c0c) (Boundary conditions)

## Tools
* `fix_hip_for_qgis.py` - [QGIS](https://qgis.org) expects NetCDF files to be formatted in a particular way, and NetCDF files from HIP are formatted in a different way. After running this tool it should be possible to import a time series from HIP into QGIS as a mesh.
  - **Note regarding CRS information** (2023-11-30). NetCDF files from HIP do not contain CRS information. It is possible to add CRS to the converted file, but QGIS cannot read the file as a mesh if CRS is present. If the file is read as a scalar, time is not interpreted correctly. The best option for now is to manually add CRS in QGIS if needed. It is not clear from the documentation which CRS to use, but the most likely candidate is [EPSG:25832](https://epsg.io/25832)
