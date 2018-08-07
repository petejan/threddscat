from thredds_crawler.crawl import Crawl
from pydap.client import open_url
from pydap.client import open_dods
import pydap.lib
import os
import urllib

import psycopg2

import dateutil.parser
import pprint

def getAttributeOrDefault(name, default):
    try:
        value = dataset.attributes['NC_GLOBAL'][name]
    except (KeyError):
        value = default

    return value

def getDateOrDefault(name, default):
    value_att = getAttributeOrDefault(name, default)
    if value_att is None:
        value = None;
    else:
        value = dateutil.parser.parse(value_att)

    return value

pydap.lib.CACHE = "/tmp/pydap-cache/"

skips = Crawl.SKIPS + [".*FV00", ".*realtime", ".*Real-time", ".*daily", ".*REAL_TIME", ".*regridded"]
#skips = Crawl.SKIPS + [".*realtime", ".*Real-time", ".*daily", ".*REAL_TIME", ".*regridded"]
#skips = Crawl.SKIPS + [".*regridded"]

#c = Crawl('http://thredds.aodn.org.au/thredds/catalog/IMOS/ABOS/DA/catalog.xml', select=['.*'] , skip=skips)
#c = Crawl('http://thredds.aodn.org.au/thredds/catalog/IMOS/ABOS/catalog.xml', select=['.*'] , skip=skips)
#c = Crawl('http://thredds.aodn.org.au/thredds/catalog/IMOS/ABOS/ASFS/catalog.xml', select=['.*'] , skip=skips)
#c = Crawl('http://thredds.aodn.org.au/thredds/catalog/IMOS/ABOS/SOTS/2016/catalog.xml', select=['.*'] , skip=skips)
c = Crawl('http://thredds.aodn.org.au/thredds/catalog/IMOS/ABOS/SOTS/catalog.xml', select=['.*'] , skip=skips)
#c = Crawl('http://thredds.aodn.org.au/thredds/catalog/IMOS/ABOS/catalog.xml', select=['.*FV0[^0]'], skip=skips)
#c = Crawl('http://thredds.aodn.org.au/thredds/catalog/IMOS/ABOS/ASFS/SOFS/Surface_waves/catalog.xml', select=['.*FV0[^0]'], skip=skips)
#c = Crawl('http://thredds.aodn.org.au/thredds/catalog/IMOS/ANMN/NRS/catalog.xml', select=['.*FV0[^0]'], skip=skips)

#c = Crawl('http://dods.ndbc.noaa.gov/thredds/catalog/oceansites/DATA/IMOS-EAC/catalog.xml', select=['.*'])
#c = Crawl('http://dods.ndbc.noaa.gov/thredds/catalog/oceansites/DATA/IMOS-ITF/catalog.xml', select=['.*'])
#c = Crawl('http://dods.ndbc.noaa.gov/thredds/catalog/oceansites/DATA/SOTS/catalog.xml', select=['.*'])

pprint.pprint(c.datasets)

urls = [s.get("url") for d in c.datasets for s in d.services if s.get("service").lower() == "opendap"]

conn = psycopg2.connect("dbname=threddscat user=thredds")
cur = conn.cursor()

for url in urls:
    pprint.pprint(url)

    dataset = open_url(url)

    title = getAttributeOrDefault('title', None)

    site_code = getAttributeOrDefault('site_code', None)
    platform_code = getAttributeOrDefault('platform_code', None)
    deployment_code = getAttributeOrDefault('deployment_code', None)
    featureType = getAttributeOrDefault('featureType', None)

    geospatial_lat_min = getAttributeOrDefault('geospatial_lat_min', None)
    geospatial_lon_min = getAttributeOrDefault('geospatial_lon_min', None)
    geospatial_vertical_min = getAttributeOrDefault('geospatial_vertical_min', None)

    date_created = getDateOrDefault('date_created', None)
    if (date_created is None):
        date_created = getDateOrDefault('date_update', None)

    time_deployment_start = getDateOrDefault('time_deployment_start', None)
    time_deployment_end = getDateOrDefault('time_deployment_end', None)

    principal_investigator = getAttributeOrDefault('principal_investigator', None)
    file_name = os.path.basename(urllib.unquote(dataset.name));
    print 'file_name ', file_name

    try:
        cur.execute("INSERT INTO file (url, file_name, title, site_code, platform_code, deployment_code, featuretype, "
                    "geospatial_lat_min, geospatial_lon_min, geospatial_vertical_min, "
                    "date_created, time_deployment_start, time_deployment_end, principal_investigator) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING file_id",
                    (url, file_name, title, site_code, platform_code, deployment_code, featureType,
                     geospatial_lat_min, geospatial_lon_min, geospatial_vertical_min,
                     date_created, time_deployment_start, time_deployment_end, principal_investigator))
        conn.commit()

        id_of_new_row = cur.fetchone()[0]

        print id_of_new_row

        # detect the TIME variable, the one with time units ?

        # loop through the Variables

        # remove any auxilary variables

        # only include variables with TIME as a dimension

        catVarList = []
        pprint.pprint(catVarList)

        auxList = []
        for variable in dataset.keys():
            var = dataset[variable]

            if var.name != 'TIME':
                try:
                    var.dimensions.index('TIME')
                    catVarList.append(variable)
#                pprint.pprint (variable)
#                print 'dim:', var.name, ':', var.dimensions
                except ValueError:
                    print 'non time variable :', var.name, ValueError
            try:
                aux = var.attributes['ancillary_variables']
                auxList.append(aux)
            except (KeyError):
                aux = None

        print 'aux list :'
#    pprint.pprint(auxList)
        for auxV in auxList:
            try:
                catVarList.remove(auxV)
            except ValueError:
                print 'could not remove ', auxV

#    print 'cat variables'
#    pprint.pprint(catVarList)
        depth = float('NaN')
        try:
            depth = dataset.attributes['NC_GLOBAL']['instrument_nominal_depth']
        except KeyError:
            print 'no instrument_nominal_depth', KeyError

#   print global atts
        glob_atts = dataset.attributes['NC_GLOBAL']
        for att in glob_atts:
            # print att

            cur.execute("INSERT INTO global_attributes (file_id, name, type, value)"
                        "VALUES (%s, %s, %s, %s)",
                        (id_of_new_row, att, "", glob_atts[att]))
            conn.commit()

#   print 'cat variables names'
        for var_name in catVarList:
            var = dataset[var_name]
            name = ''
            try:
                name = var.attributes['standard_name']
            except KeyError:
                print 'no standard_name :', var.name

            if len(name) == 0:
                try:
                    name = var.attributes['long_name']
                except KeyError:
                    print 'no long_name :', var.name

            try:
                aux_vars = var.attributes['ancillary_variables']
            except KeyError:
                print 'no aux_vars', var_name
                aux_vars = ''

            try:
                units = var.attributes['units']
            except KeyError:
                print 'no units', var_name
                units = ''

            dims = var.dimensions;

            # print name, '(', units, ')'

            # add dimensions and depths to paramters table, one line for each depth

            cur.execute("INSERT INTO parameters (file_id, variable, name, units, depth, dimensions, aux_vars)"
                        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (id_of_new_row, var_name, name, units, depth, dims, aux_vars))
            conn.commit()

    except psycopg2.IntegrityError:
        print 'Integrity Error'
        #cur.close()
        conn.rollback()
        cur = conn.cursor()

cur.close()
conn.close()
