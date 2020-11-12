# Parsing-data-from-wfs
This pythonic script obtains data from WFS server, using BBOX get the object that contains only in scope, if it is over than  limit, it will divide the scope into 4 smaller. If it's lower than limit it will parses and writes to SQLite database in Spatialite mode.
## Getting started

### Prerequisites

*Python >=3.6*

This script needs to have mod_sptialite.dll to write data in correct type to database. Please download appropriate file for your system.
Dependencies can be installed using pip:
```
$ pip install -r requirements.txt
```

### Usage

Run script:
```
$ python wfs_xml_parser.py
```

Input parameters:
  - Enter the address of your WFS server with “request=GetFeature”
  - Enter type name of object to parse;
  - Enter url filter that works for your server, Notice: in place of coordinates write “{}”;
  - Enter limit of object that server can return in one request;
  - Enter the path to mod_spatialite.dll file;
  - Enter 0 to modify existed database and 1 to create new one;
  - Enter the whole path to your database and it name; Example (78690,119845 956265,800022) 
  - Enter the name of table you wish to create;
  - Enter coordinates like (x1,y1 x2,y2); Example (78690,119845 956265,800022)
  - Enter 1 to replace x and y at object coordinates (sometimes server replace x and y);
  - Enter 1 to replace coordinates in filter;

### Additional info

Function “make_soup()”:

This function sends request to server obtains the answer and check if it’s correct, if not it sends again, in every third attempt it will wait 10s and next go to ask again and again. If it gets good response it will return BeautifulSoup object.
In case of errors please check your input parameters. If it’s ok, so make a coffee and try again.
