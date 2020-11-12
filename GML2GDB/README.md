# GML2GDB
Script that downloads the folders zip, extract them and from xml files create the GeoDataBase

## Main purpose:
This script will download zip archives of xml files that contain the addresses points of each region. After it will unzip it to temporary folder TEMP, and creating one big AllData.gdb GeoDataBase. In this database using arcpy update rows and delete not needed columns.

### Prerequisites

*Python >=3.6 or ==2.7*

Dependencies can be installed using pip:
```
pip install -r requirements.txt
```

### Parameters: 
  - outputDir - the destination of your GeoDataBase;

### Usage

Run script:
```
python gml2gdb-python-3.6.py <outputDir>
```