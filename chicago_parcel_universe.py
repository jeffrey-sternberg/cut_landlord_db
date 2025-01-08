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