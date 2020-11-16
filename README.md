# GeoScripts
Common repo for geographic data processing scripts

## Installation
Each subrepo has its own requirements file and can be set up as separate environment.

## Scripts

### [FieldsInterpolation](./FieldsInterpolation)
Script that predict the position of the empty address due to the position information of near address points.

### [GML2GDB](./GML2GDB)
This script will download zip archives of xml files that contain the addresses points of each region. After it will unzip it to temporary folder TEMP, and creating one big AllData.gdb GeoDataBase. In this database using arcpy update rows and delete not needed columns.

### [WFSxmlParser](./WFSxmlParser)
This pythonic script retrives data from WFS server, using BBOX gets the object that contains the scope, if it is over limit, it will divide the scope into 4 smaller. If it's lower limit it will parse and write to SQLite database in Spatialite mode.
