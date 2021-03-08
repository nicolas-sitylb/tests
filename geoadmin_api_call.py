# -*- coding: utf-8 -*-
"""
Compute Lidar tile coverage from a list of tile IDs
"""
# %%
import os, sys, re, math
import requests
import json
import numpy as np
import pandas as pd
import fiona
import geojson
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely import geometry, wkt
from shapely.geometry import Polygon, shape
# %%

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

def bbox_to_polygon(bbox):
    xmin, ymin, xmax, ymax = bbox
    polygon = Polygon([
        [xmin,ymin],
        [xmax,ymin],
        [xmax,ymax],
        [xmin,ymax],
        [xmin,ymin]]
    )

    return polygon

def get_tile_meta():
    layer = 'ch.swisstopo.swisssurface3d.metadata'
    base_url = 'https://api3.geo.admin.ch/rest/services/api/MapServer'
    find_url = base_url+'/find'
    searchField = 'id'
    searchText = ''
    
    res0 = requests.get(url = base_url,
                    params = {'searchText': layer}
    )
    print(res0.status_code)
    data0 = res0.json()
    columns = set(data0.keys())
    df = pd.DataFrame.from_dict(data0, orient='index').T
    
    return(df)

def get_feature_info(**kw):
    layer = kw.get('layer') if kw.get('layer') is not None else 'ch.swisstopo.images-swissimage-dop10.metadata'
    search_field = kw.get('search_field')
    search_text = kw.get('search_text')
    headers = {
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.7113.93 Safari/537.36',
        'content-type': 'application/json'    
    }
    base_url = 'https://api3.geo.admin.ch/rest/services/api/MapServer'
    find_url = base_url+'/find'
    res = requests.get(url = find_url,
        params = {
            'layer': layer,
            'searchField': search_field,
            'searchText': search_text,
            'sr': 2056,
            'geometryFormat': 'geojson'
       }
    )
    if res.status_code == 200 and False: ## reset after tests
        print("We got a record!")
        data = res.json()['results']
        data_keys = data[0].keys()  
        idx = data[0]['id']
        layerName = data[0]['layerName']
        bbox = bbox_to_polygon(data[0]['bbox'])
        attributes = data[0]['attributes'] if data[0]['attributes'] else None
        layerBodId = data[0]['layerBodId']
        tile_geom = data[0]['geometry']['rings']
        srs = int([v for k,v in data[0]['geometry']['spatialReference'].items()][0])
        polygon = geometry.Polygon(tile_geom[0])
        retval = {
            'id': idx,
            'layerName': layerName,
            'bbox': bbox,
            'attributes': attributes,
            'layerBodId': layerBodId,
            'srs': srs,
            'geometry': polygon
        }
    else:
        print(f"Error in response, status code is: {res.status_code}")
        retval = None
    
    return (res)

def convert_list_of_tiles_to_gdf(tiles_list):
    results = []
    for tile_id in tiles_list:
        print("Processing tile {}".format(tile_id))
        results.append(get_feature_info(**{
                'search_field': 'id',
                'search_text': tile_id,
                'layer': 'ch.swisstopo.swisssurface3d.metadata'
            })
        )
    
    #df = pd.DataFrame(results)
    gdf = gpd.GeoDataFrame(results)
    gdf.drop(columns=['data'], inplace=True)
    gdf['const'] = 0
    print("Processing finished successfully.")

    return(gdf)

def get_all_tiles_district_nord_vaudois():
    col_min = 2498
    col_max = 2551
    row_min = 1153
    row_max = 1198
    width = col_max - col_min
    height = row_max - row_min
    cells = width * height
    blocks = int(math.ceil(cells/(4*height)))
    data = []
    for row in range(height):
        for col in range(width):
            st = str(col_min+col)+'_'+str(row_min+row)
            print(f"Tile: {st}")
            res = (get_feature_info(**{
                    'search_field': 'id',
                    'search_text': st,
                    'layer': 'ch.swisstopo.images-swissimage-dop10.metadata',
                    'sr': 2056
                })
            )
            if len(res.json()['results']) == 1:
                data.append(res.json()['results'][0])

    gdf = gpd.GeoDataFrame(data)
    gdf['geometry'] = gdf.apply(lambda x: shape(x['geometry']), axis=1)
    print("Processing finished successfully.")

    return (gdf)

def get_district(inname='vaudois'):
    res = get_feature_info(**{
        'search_field': 'name',
        'search_text': inname,
        'layer': 'ch.swisstopo.swissboundaries3d-bezirk-flaeche.fill'
    })
    data = res.json()['results'][0]
    gdf = gpd.GeoDataFrame(pd.DataFrame.from_dict(data, orient='index').T)

    return (gdf)

def get_district_tile_coverage(gdf_district):

    return None
# %%

# %%

# %%

tiles_list_file = "./INPUT/LIDAR/list_of_lidar_tiles.txt"
with open(tiles_list_file, 'r') as f:
    tiles_list = f.readlines();

tiles_list = [re.sub('\r?\n', '', t) for t in tiles_list]

gdf = convert_list_of_tiles_to_gdf(tiles_list)
gdf.to_file(
    filename = os.path.join('OUTPUT','lidar_tiles_coverage_new.gpkg'),
    driver ='GPKG'
)
# %%