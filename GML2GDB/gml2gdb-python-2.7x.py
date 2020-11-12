#!/usr/bin/env python
# -*- coding=utf-8 -*-
from __future__ import print_function
import arcpy
import os
import shutil
import urllib


# download zip-folders and unzip them to folder TEMP;
def download_unzip():
    pwd = os.getcwd()
    os.makedirs(pwd + "\\TEMP")
    urllib.urlretrieve("ftp://91.223.135.109/prg/punkty_adresowe.zip", "TEMP\\puntky_adresowe.zip")
    urllib.urlcleanup()
    urllib.urlretrieve("ftp://91.223.135.109/prg/jednostki_administracyjne.zip", "TEMP\\jednostki_administracyjne.zip")
    os.makedirs(pwd + "\\TEMP\\punkty_xml")
    os.makedirs(pwd + "\\TEMP\\jednostki")

    zip_punkty = pwd + "\\TEMP\\puntky_adresowe.zip"
    xml_punkty = pwd + "\\TEMP\\punkty_xml"
    zip_jedn = pwd + "\\TEMP\\jednostki_administracyjne.zip"
    jednostki = pwd + "\\TEMP\\jednostki"

    with zipfile.ZipFile(zip_punkty, 'r') as zip_ref:
        zip_ref.extractall(xml_punkty)
    with zipfile.ZipFile(zip_jedn, 'r') as zip_ref:
        zip_ref.extractall(jednostki)


def get_databases_dictionary(input_list, source_dir):
    base_dic = {}

    for base in input_list:

        arcpy.env.workspace = source_dir + "\\" + base
        elemOfBase = arcpy.ListFeatureClasses()
        elemOfBase += arcpy.ListDatasets()
        elemOfBase += arcpy.ListTables()

        for element in elemOfBase:
            base_dic.setdefault(element.decode('unicode_escape').encode('utf-8'), []).append(
                base + "\\" + element.decode('unicode_escape').encode('utf-8'))

    print(base_dic)
    return base_dic


# Location of new GeoDataBase;
outputDir = 'C:\\gml2gdb\\dane'
# sys.argv[1]

download_unzip()

# My script location;
cwd = os.getcwd()
puntky_xml_dir = cwd + "\\TEMP\\punkty_xml"
schemaXSD = cwd + r"\\TEMP\\punkty_xml\\PRG_Adresy_schemat.xsd"
inputList = []

# Create list of xml files;
for file in os.listdir(puntky_xml_dir):
    if file.endswith('.xml'):
        inputList.append(file)

# Process: Quick Import
print('\nimporting', end='')
for inputFile in inputList:
    print('.', end='')
    arcpy.QuickImport_interop(
        "GML," + puntky_xml_dir + "/" + inputFile + ",\"RUNTIME_MACROS,\"\"IGNORE_APPLICATON_SCHEMA,no,XSD_DOC,\"\"\"\"" + schemaXSD + "\"\"\"\",VALIDATE_DATASET,no,FEATURE_TYPES_SCHEMA_MODE,XML_SCHEMA,SKIP_SCHEMA_LOCATION_IN_DATASET,No,MAP_FEATURE_COLLECTION,,GML_FEATURE_ELEMENTS,<Unused>,SRS_GEOMETRY_PARAMETERS,,SRS_AXIS_ORDER,,SRS_ANGLE_DIRECTION,,ENFORCE_PATH_CONTINUITY_BY,SNAPPING_END_POINTS,FEATURE_PROPERTIES_READER,,MAP_EMBEDDED_OBJECTS_AS,ATTRIBUTES,MAP_PREDEFINED_GML_PROPERTIES,NO,MAP_GEOMETRY_COLUMNS,YES,MAP_ALL_SUBSTITUTABLE_PROPERTIES,YES,ADD_NAMESPACE_PREFIX_TO_NAMES,,QNAMES_FOR_PROPERTIES_TO_IGNORE,,ATTRIBUTE_HANDLING,,MAP_COMPLEX_PROPERTIES_AS,\"\"\"\"Nested Attributes\"\"\"\",MAX_MULTI_LIST_LEVEL,,ADD_GEOMETRIES_AS_XML_FRAGMENTS,NO,XML_FRAGMENTS_AS_DOCUMENTS,YES,FLATTEN_XML_FRAGMENTS,NO,FLATTEN_XML_FRAGMENTS_OPEN_LIST_BRACE,,FLATTEN_XML_FRAGMENTS_CLOSE_LIST_BRACE,,FLATTEN_XML_FRAGMENTS_SEPARATOR,,GML_READER_GROUP,,USE_OLD_READER,NO,DISABLE_AUTOMATIC_READER_TYPE_SELECTION,NO,DISABLE_XML_NAMESPACE_PROCESSING,NO,EXPOSE_ATTRS_GROUP,,GML_EXPOSE_FORMAT_ATTRS,,USE_SEARCH_ENVELOPE,NO,SEARCH_ENVELOPE_MINX,0,SEARCH_ENVELOPE_MINY,0,SEARCH_ENVELOPE_MAXX,0,SEARCH_ENVELOPE_MAXY,0,CLIP_TO_ENVELOPE,NO,GML_RDR_ADV,,CONTINUE_ON_GEOM_ERROR,yes,SYSTEM_ENCODING,,CACHE_XSD,yes,CACHE_XSD_EXPIRY_TIME,,MULTI_VALUE_SIMPLE_PROPERTIES_AS_CSV,no,NETWORK_AUTHENTICATION,\"\"\"\"AUTH_INFO_GROUP,NO,AUTH_METHOD,<lt>Unused<gt>,NAMED_CONNECTION,<lt>Unused<gt>,AUTH_USERNAME,<lt>Unused<gt>,AUTH_PASSWORD,<Unused>\"\"\"\",_MERGE_SCHEMAS,YES\"\",META_MACROS,\"\"SourceIGNORE_APPLICATON_SCHEMA,no,SourceXSD_DOC,\"\"\"\"" + schemaXSD + "\"\"\"\",SourceVALIDATE_DATASET,no,SourceFEATURE_TYPES_SCHEMA_MODE,XML_SCHEMA,SourceSKIP_SCHEMA_LOCATION_IN_DATASET,No,SourceMAP_FEATURE_COLLECTION,,SourceGML_FEATURE_ELEMENTS,<Unused>,SourceSRS_GEOMETRY_PARAMETERS,,SourceSRS_AXIS_ORDER,,SourceSRS_ANGLE_DIRECTION,,SourceENFORCE_PATH_CONTINUITY_BY,SNAPPING_END_POINTS,SourceFEATURE_PROPERTIES_READER,,SourceMAP_EMBEDDED_OBJECTS_AS,ATTRIBUTES,SourceMAP_PREDEFINED_GML_PROPERTIES,NO,SourceMAP_GEOMETRY_COLUMNS,YES,SourceMAP_ALL_SUBSTITUTABLE_PROPERTIES,YES,SourceADD_NAMESPACE_PREFIX_TO_NAMES,,SourceQNAMES_FOR_PROPERTIES_TO_IGNORE,,SourceATTRIBUTE_HANDLING,,SourceMAP_COMPLEX_PROPERTIES_AS,\"\"\"\"Nested Attributes\"\"\"\",SourceMAX_MULTI_LIST_LEVEL,,SourceADD_GEOMETRIES_AS_XML_FRAGMENTS,NO,SourceXML_FRAGMENTS_AS_DOCUMENTS,YES,SourceFLATTEN_XML_FRAGMENTS,NO,SourceFLATTEN_XML_FRAGMENTS_OPEN_LIST_BRACE,,SourceFLATTEN_XML_FRAGMENTS_CLOSE_LIST_BRACE,,SourceFLATTEN_XML_FRAGMENTS_SEPARATOR,,SourceGML_READER_GROUP,,SourceUSE_OLD_READER,NO,SourceDISABLE_AUTOMATIC_READER_TYPE_SELECTION,NO,SourceDISABLE_XML_NAMESPACE_PROCESSING,NO,SourceEXPOSE_ATTRS_GROUP,,SourceGML_EXPOSE_FORMAT_ATTRS,,SourceUSE_SEARCH_ENVELOPE,NO,SourceSEARCH_ENVELOPE_MINX,0,SourceSEARCH_ENVELOPE_MINY,0,SourceSEARCH_ENVELOPE_MAXX,0,SourceSEARCH_ENVELOPE_MAXY,0,SourceCLIP_TO_ENVELOPE,NO,SourceGML_RDR_ADV,,SourceCONTINUE_ON_GEOM_ERROR,yes,SourceSYSTEM_ENCODING,,SourceCACHE_XSD,yes,SourceCACHE_XSD_EXPIRY_TIME,,SourceMULTI_VALUE_SIMPLE_PROPERTIES_AS_CSV,no,SourceNETWORK_AUTHENTICATION,\"\"\"\"AUTH_INFO_GROUP,NO,AUTH_METHOD,<lt>Unused<gt>,NAMED_CONNECTION,<lt>Unused<gt>,AUTH_USERNAME,<lt>Unused<gt>,AUTH_PASSWORD,<Unused>\"\"\"\"\"\",METAFILE,GML,COORDSYS,\"\"\"\"\"\"ESRIWKT|ETRS_1989_Poland_CS92|PROJCS[\"\"\"\"ETRS_1989_Poland_CS92\"\"\"\",GEOGCS[\"\"\"\"GCS_ETRS_1989\"\"\"\",DATUM[\"\"\"\"D_ETRS_1989\"\"\"\",SPHEROID[\"\"\"\"GRS_1980\"\"\"\",6378137.0,298.257222101]],PRIMEM[\"\"\"\"Greenwich\"\"\"\",0.0],UNIT[\"\"\"\"Degree\"\"\"\",0.0174532925199433]],PROJECTION[\"\"\"\"Transverse_Mercator\"\"\"\"],PARAMETER[\"\"\"\"False_Easting\"\"\"\",500000.0],PARAMETER[\"\"\"\"False_Northing\"\"\"\",-5300000.0],PARAMETER[\"\"\"\"Central_Meridian\"\"\"\",19.0],PARAMETER[\"\"\"\"Scale_Factor\"\"\"\",0.9993],PARAMETER[\"\"\"\"Latitude_Of_Origin\"\"\"\",0.0],UNIT[\"\"\"\"Meter\"\"\"\",1.0]]\"\"\"\"\"\",IDLIST,,__FME_DATASET_IS_SOURCE__,true\"",
        outputDir + "\\" + inputFile + ".gdb")

for i in range(len(inputList)):
    inputList[i] = inputList[i] + ".gdb"

dictionary = get_databases_dictionary(inputList, outputDir)
print("Dictionary is ok")
arcpy.env.workspace = outputDir

# Delete old GeoDataBase if exists
if os.path.exists(outputDir + "\\allData.gdb"):
    shutil.rmtree(outputDir + "\\allData.gdb")

# Creating new GeoDataBase
arcpy.CreateFileGDB_management(outputDir, "allData.gdb")

# Process: Merge
print('\nmerging', end='')
for key, val in dictionary.items():
    print('.', end='')
    # val = [i.decode('unicode_escape').encode('utf-8') for i in val]
    arcpy.Merge_management(val, outputDir + "\\allData.gdb\\" + key)

for file in os.listdir(outputDir):
    if file != "allData.gdb":
        os.system("rmdir /S /Q {}\\{}".format(outputDir, file))

arcpy.env.workspace = outputDir + "\\allData.gdb"

gminyDir = cwd + "\\TEMP\\jednostki\\gminy.shp"
print(gminyDir)
fc = 'PRG_PunktAdresowy'
intersectPointPoligon = 'intersectPoint'
newFields = ['nowaUlica', 'nowaMiejscowosc']

cursorAccessFields = ["ulica", "miejscowosc", 'nowaUlica', 'nowaMiejscowosc', 'jpt_nazwa_']
print('start')

# Provide a default value if unspecified
Input_Features = gminyDir + ';' + outputDir + "\\allData.gdb\\PRG_PunktAdresowy #"

# Provide a default value if unspecified
pkt_adr_intersect_gminy = "pkt_adr_intersect_gminy"

# Process: Intersect
arcpy.Intersect_analysis(Input_Features, pkt_adr_intersect_gminy, "ALL", "", "POINT")
arcpy.AddField_management(pkt_adr_intersect_gminy, 'nowaUlica', "TEXT", field_length=2048)
arcpy.AddField_management(pkt_adr_intersect_gminy, 'nowaMiejscowosc', "TEXT", field_length=2048)
arcpy.TableToGeodatabase_conversion(gminyDir, arcpy.env.workspace)
print('start')
# Replace values in database;
updateCursor = arcpy.da.UpdateCursor(pkt_adr_intersect_gminy, cursorAccessFields)
for row in updateCursor:
    if row[0] is None:
        row[2] = row[1]
        row[3] = row[4]
    else:
        row[2] = row[0]
        row[3] = row[1]

    updateCursor.updateRow(row)

field_leave = ['nowaUlica', 'nowaMiejscowosc', 'kodPocztowy', 'numerPorzadkowy', 'OBJECTID', 'Shape']

# List of fields to remove;
field_del = []
desc = arcpy.Describe(pkt_adr_intersect_gminy)
for field in desc.fields:
    if field.name not in field_leave:
        field_del.append(field.name)

# Delete unnecessary fields;
arcpy.DeleteField_management(pkt_adr_intersect_gminy, field_del)

# Remove the Temp folder;
os.system("rmdir /Q /S TEMP")
