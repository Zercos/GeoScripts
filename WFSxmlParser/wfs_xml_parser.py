# -*- coding: utf-8 -*-
import copy
import requests
import sqlite3
import time
import bs4
from bs4 import BeautifulSoup

# Get the user input;
url_address = str(input('Enter the url address: '))
typeName = '&' + 'typeName=' + str(input('Enter the typeName: '))
url_filter = str(input('Enter your filter with {} in place of coordinates: '))
limit = int(input('Enter limit: '))
mod_spatialite = input('Enter the path to mod_spatialite.dll file: ')
create_new_db = int(input('0-modify exist, 1-create new database: '))
db_file = input('Enter the destination of database: ')
table_name = str(input('Enter the name of table you wish exists in your database: '))
coordinates = input('Enter coordinates like <(x1,y1 x2,y2)>: ')
to_revert = int(input("0-not revert coordinates, 1-revert: "))
revert_bbox = int(input('0-not revert bbox, 1-revert: '))

# Start time of execution;
start_time = time.time()

COLUMN_TYPE = ''
GEOM_TYPE = ''

# Tuple of all possible geometries types;
geom = ('Point', 'LineString', 'Polygon', 'GeometryCollection',
        'MultiPoint', 'MultiLineString', 'MultiPolygon')

# Templates of dictionaries;
json_template = {
    "type": "FeatureCollection",
    "name": "temp_point_layer",
    "crs":
        {
            "type": "name",
            "properties":
                {
                    "name": "urn:ogc:def:crs:EPSG::2180"
                }
        },
    "features": []
}
dic_template = {"type": "Feature",
                "properties":
                    {

                    },
                "geometry":
                    {
                        "type": "0",
                        "coordinates": []
                    }
                }


# Function add prefix MULTI to column type;
def add_column_type_prefix():
    global COLUMN_TYPE
    if COLUMN_TYPE in ('Point', 'Polygon', 'LineString'):
        COLUMN_TYPE = ('Multi' + COLUMN_TYPE).upper()


# Make BeautifulSoup object;
def make_soup(http):
    global COLUMN_TYPE, GEOM_TYPE
    continue_send_request = True
    request_num = 0
    # loop that will iterate while we obtain good response;
    while continue_send_request:
        try:
            response = requests.get(http, timeout=120)
            if response.status_code != 200:
                raise requests.RequestException
            soup = BeautifulSoup(response.content, features="xml")

            for geo_type in geom:
                if soup.find(geo_type):
                    GEOM_TYPE = geo_type
                    COLUMN_TYPE = geo_type
                    break
            add_column_type_prefix()
            continue_send_request = False
        except Exception as e:
            request_num += 1
            print(e)
            # if 5 times fail - wait 10s and ask again;
            if request_num % 5 == 0:
                time.sleep(10)
    return soup


# From string to list;
def make_coordinates_list(input_coordinates):
    coordinates_list = [float(input_coordinates.split()[0].split(',')[0]),
                        float(input_coordinates.split()[0].split(',')[1]),
                        float(input_coordinates.split()[1].split(',')[0]),
                        float(input_coordinates.split()[1].split(',')[1])]
    return coordinates_list


# From list to dictionary;
def make_dict(lst):
    coordinates_dict = {'xmin': float(lst[0]), 'ymin': float(lst[1]), 'xmax': float(lst[2]), 'ymax': float(lst[3])}
    return coordinates_dict


# Parsing and write the data to database, in case if limit is over divide into 4 part;
def divide(lst):
    global url_address, typeName, url_filter, limit, j_file, dic, db_file, table_name, lower_corner, upper_corner, coordinates
    if 'coordinates' in url_filter:
        coordinates = f'{lst[0]},{lst[1]} {lst[2]},{lst[3]}'
        url = url_address + typeName + '&' + url_filter.format(coordinates)
    elif 'lowerCorner' in url_filter:
        lower_corner = f'{lst[0]} {lst[1]}'
        upper_corner = f'{lst[2]} {lst[3]}'
        url = url_address + typeName + '&' + url_filter.format(lower_corner, upper_corner)

    soup = make_soup(url)
    returned_number = soup.find("wfs:FeatureCollection")["numberReturned"]

    if int(returned_number) == 0:
        print("No object returns")
        return 0

    if int(returned_number) >= limit:
        dic_cor = make_dict(lst)
        mean_x = (dic_cor['xmin'] + dic_cor['xmax']) / 2
        mean_y = (dic_cor['ymin'] + dic_cor['ymax']) / 2
        divide([dic_cor['xmin'], dic_cor['ymin'], mean_x, mean_y])
        divide([dic_cor['xmin'], mean_y, mean_x, dic_cor['ymax']])
        divide([mean_x, dic_cor['ymin'], dic_cor['xmax'], mean_y])
        divide([mean_x, mean_y, dic_cor['xmax'], dic_cor['ymax']])
    elif int(returned_number) < limit:
        jk = parse(soup, j_file, dic)
        connR = create_connection(db_file)
        create_table(db_file, table_name, connR, jk)
        add_to_database(jk, table_name, connR)
        connR.close()


# Write to jsn-template;
def parse(soup, jk, dic_uniq):
    jsn_w = copy.deepcopy(jk)
    members = soup.find_all("wfs:member")
    for mem in members:
        mem_dic = copy.deepcopy(dic_uniq)
        dict_to_append = search(mem, mem_dic)
        # if dict_to_append not in jsn_w["features"]:
        jsn_w["features"].append(dict_to_append)
    return jsn_w


# Parse each object and write to dictionary;
def search(obj, my_dict):
    # list of all element in xml that contain info;
    other = [i for i in obj.descendants if (type(i) != bs4.element.NavigableString and bool(i.string)
                                            and not bool(i.findChild(GEOM_TYPE))
                                            and not bool(i.findParent(GEOM_TYPE))
                                            and i.name != GEOM_TYPE)]
    for elm in other:
        my_dict["properties"][elm.name] = elm.string

    # list of all geometries elements;
    tp_l = obj.find_all(GEOM_TYPE)
    for pol in tp_l:
        if my_dict['geometry']["type"] == '0':
            my_dict['geometry']["type"] = pol.name
        if pol.name in ("Polygon", "MultiPolygon"):
            area = []
            ex = str(pol.find('exterior').text.replace('\n', '')).split()
            area.append(double_coord(ex))
            if pol.find("interior"):
                for i in pol.find_all('interior'):
                    it = str(i.text.replace('\n', '')).split()
                    area.append(double_coord(it))
            my_dict['geometry']["coordinates"].append(area)
        else:
            post = str(pol.text.replace('\n', '')).split()
            my_dict['geometry']["coordinates"].append(double_coord(post))

    return my_dict


# Write coordinates like (x,y) as one item;
def double_coord(lst):
    return_lst = []
    h = 1
    for n in range(len(lst)):
        if n % 2 == 0:
            return_lst.append(lst[n])
        else:
            return_lst[n - h] = lst[n - 1] + ' ' + lst[n]
            h += 1
    return return_lst


# Create database;
def create_database(db_file_name):
    """ create a SQLite database """
    try:
        conn = sqlite3.connect(db_file_name)
        print(sqlite3.version)
    except Exception as e:
        print(e)
    finally:
        conn.close()


# Making connection to database;
def create_connection(database_file):
    """ create a database connection to the SQLite database specified by database_file """
    try:
        conn = sqlite3.connect(database_file)
        return conn
    except Exception as e:
        print(e)
    return None


# Make a list of all columns name;
def lst_all_col(file):
    lst_to_return = []
    for num in range(len(file['features'])):
        col_list = list(file['features'][num]['properties'].keys())
        for col in col_list:
            if col not in lst_to_return:
                lst_to_return.append(col)
    return lst_to_return


# Create a table in database and columns in it;
def create_table(db_file_name, table, connR, file):
    global COLUMN_TYPE
    connR.enable_load_extension(True)
    connR.execute(r'SELECT load_extension("{}")'.format(mod_spatialite))
    connR.execute('SELECT InitSpatialMetaData(1);')
    curR = connR.cursor()
    lst = lst_all_col(file)
    create = ' NVARCHAR(100), '.join(i for i in lst) + ' NVARCHAR(100)'
    uniq = ', '.join(i for i in lst)

    curR.execute(
        f'CREATE TABLE IF NOT EXISTS {table}(id INTEGER PRIMARY KEY,{create}, UNIQUE({uniq}))')
    curR.execute(
        f'SELECT AddGeometryColumn("{table}","geom" , 2180, "{COLUMN_TYPE}", 2)')

    connR.commit()


def create_col(jsn_file, connR, table):
    curR = connR.cursor()
    curR.execute(f"PRAGMA table_info({table});")
    re = curR.fetchall()
    if len(re) <= 2:
        columns_list = lst_all_col(jsn_file)
        for col in columns_list:
            curR.execute(f'ALTER TABLE {table} ADD {col} NVARCHAR(100)')
        connR.commit()


# Make a string of coordinates of polygon type;
def db_polygon(lst):
    s = ''
    for polygon in lst:
        d = ''
        for l in polygon:
            str_pos = ','.join(str(i) for i in l)
            d += f'({str_pos}),'
        s += "(" + d[:-1] + "),"
    return s[:-1]


# Make revert coordinate to write;
def revert_coordinates(lst):
    global COLUMN_TYPE
    if COLUMN_TYPE == 'MULTIPOLYGON':
        for polygon in lst:
            for pol_coordinates in polygon:
                for i in range(len(pol_coordinates)):
                    pol_coordinates[i] = str(pol_coordinates[i].split()[1] + ' ' + pol_coordinates[i].split()[0])
    else:
        for pol_coordinates in lst:
            for i in range(len(pol_coordinates)):
                pol_coordinates[i] = str(pol_coordinates[i].split()[1] + ' ' + pol_coordinates[i].split()[0])


# Make bbox coordinates revert;
def revert(string):
    reverted_coordinates = string.split()[0].split(",")[1] + "," + string.split()[0].split(",")[0] + " " + \
                           string.split()[1].split(",")[1] + "," + string.split()[1].split(",")[0]
    return reverted_coordinates


# Make a string of coordinates of point type;
def db_point(lst):
    s = ''
    for l in lst:
        str_pos = ','.join(str(i) for i in l)
        s += f'({str_pos}),'
    return s[:-1]


# Make a string of coordinates of linestring type;
def db_line(lst):
    s = ''
    for l in lst:
        str_pos = ','.join(str(i) for i in l)
        s += f'{str_pos},'
    return s[:-1]


# Choose the type of geometry type to covert the coordinates;
def choose_func(pos):
    global COLUMN_TYPE
    if COLUMN_TYPE == "MULTIPOLYGON":
        return db_polygon(pos)
    elif COLUMN_TYPE == "MULTIPOINT":
        return db_point(pos)
    elif COLUMN_TYPE == "MULTILINESTRING":
        return db_line(pos)


# Write from jsn_template to database;
def add_to_database(file, table, connR):
    print("Start")
    global COLUMN_TYPE, to_revert
    connR.enable_load_extension(True)
    connR.execute('SELECT load_extension("{}")'.format(mod_spatialite))

    curR = connR.cursor()
    for n in range(len(file["features"])):
        if n % 1000 == 0:
            connR.commit()
        my_d = file["features"][n]['properties']
        lst_keys = list(my_d.keys())
        keys = ','.join(str(i) for i in lst_keys)
        values = ','.join(f"\"{str(i)}\"" for i in list(my_d.values()))
        pos = file["features"][n]["geometry"]['coordinates']
        if to_revert:
            revert_coordinates(pos)
        str_pos = choose_func(pos)

        curR.execute(
            f"INSERT OR IGNORE INTO {table} ({keys},geom) VALUES ({values},(GeomFromText('{COLUMN_TYPE}({str_pos})', 2180)))")
        # curR.execute(f"UPDATE {table} SET geom = (GeomFromText('{col_type}({str_pos})', 2180)) WHERE id = {n+1}")
    connR.commit()


if revert_bbox:
    coordinates = revert(coordinates)

if 'lowerCorner' in url_filter:
    lower_corner = coordinates.split()[0].replace(',', ' ')
    upper_corner = coordinates.split()[1].replace(',', ' ')
    lst_of_coordinates = lower_corner.split() + upper_corner.split()
else:
    lst_of_coordinates = make_coordinates_list(coordinates)

j_file = copy.deepcopy(json_template)
dic = copy.deepcopy(dic_template)

if create_new_db:
    create_database(db_file)

# execute the main function;
divide(lst_of_coordinates)

print(time.time() - start_time)
print("Successfully")
