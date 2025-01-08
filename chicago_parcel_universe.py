import pandas as pd
import geopandas as gpd
import folium
import requests
import json
from shapely.geometry import Polygon
import os

# Cook County Parcel Universe from Asesor's Office, request limits to City of Chicago parcels for 2024
baseurl = 'https://datacatalog.cookcountyil.gov/resource/nj4t-kc8j.json?$limit=50000&year=2024&tax_cook_municipality_name=CITY OF CHICAGO&$offset='

offset = ['0','50000','100000','150000','200000','250000','300000','350000','400000','450000','500000','550000','600000','650000','700000','750000','800000','850000','900000','950000']

parcel_dfs = []

for o in offset:
    print('Offset= '+o)
    r = requests.get(baseurl+o)
    data = r.json()
    df = pd.json_normalize(data).filter(['pin','year','class','lon','lat','chicago_community_area_num','chicago_community_area_name'],axis=1)
    print(len(df))
    parcel_dfs.append(df)
parcel_universe = pd.concat(parcel_dfs)#.drop_duplicates().reset_index(drop=True)

#Gives all parcels with PINs, lat,lon, chicago community area in Chicago for feeding into 
# other scraping script for property tax owner info 
parcel_universe

#Count table by 'class' which is the primary way to filter down to renter classed properties
parcel_universe.groupby(['class'])['pin'].count().to_frame().reset_index()

## Need to spatial join this parcel universe with the parcel shapefiles for mapping to update the geometry from coordinates to polygon for mapping accordingly and buffer merge below. 
offset = ['0','50000','100000','150000','200000','250000','300000','350000','400000','450000','500000','550000','600000']
parcel_list = []

for o in offset:
    r = requests.get('https://datacatalog.cookcountyil.gov/resource/77tz-riq7.json?$limit=50000&MUNICIPALITY=Chicago&$offset='+o)
    data = r.json()
    parcels = pd.json_normalize(data)
    print(o)
    print(len(parcel_list))
    parcel_list.append(parcels)

parcel_shps = pd.concat(parcel_list).filter(['pin10','the_geom.coordinates'],axis=1)
parcel_shps['geometry'] = [Polygon(item[0][0]) for item in parcel_shps['the_geom.coordinates']]
parcel_geo = gpd.GeoDataFrame(parcel_shps, geometry='geometry',crs = 'EPSG:4326')
parcel_geo.plot()

#Join them
parcel_poly = parcel_universe.merge(parcel_geo, how='left', on='pin10')