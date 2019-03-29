import os
import io
import sys
import inspect
import numpy as np
import pandas as pd
import urllib.request
import json

from pprint import pprint

# Path
currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
resourcedir = currentdir + str("/")

# Variables
ORIGIN = "45.523050,-73.581428"
ORIGIN = [float(i) for i in ORIGIN.split(',')]
RADIUS = 10000


def get_coords(origin, radius):
    url_isoapi = str('http://www.iso4app.net/rest/1.3/isoline.geojson?licKey=87B7FB96-83DA-4FBD-A312-7822B96BB143&type=isodistance&value='+str(radius)+'&lat='+str(origin[0]) +
                     '&lng='+str(origin[1])+'&approx=1000&mobility=motor_vehicle&speedType=normal&reduceQueue=false&avoidTolls=true&restrictedAreas=false&fastestRouting=true&concavity=6&buffering=3&reqId=A57X')

    with urllib.request.urlopen(url_isoapi) as url:
        data = json.loads(url.read().decode())
        # print(data)

    def swapCoords(x):
        out = []
        for iter in x:
            if isinstance(iter, list):
                out.append(swapCoords(iter))
            else:
                return [x[1], x[0]]
        return out

    for feature in data['features']:
        feature['geometry']['coordinates'] = swapCoords(
            feature['geometry']['coordinates'])

    features = data['features']
    origin_point = features[1]['geometry']['coordinates']
    pprint('Origin: ' + str(origin_point))
    geoloc = (features[2]['geometry']['coordinates'])[0][0]

    geoloc_lat = []
    geoloc_lng = []
    for i in range(len(geoloc)):
        geoloc_lng.append(round(geoloc[i][1], 4))
        geoloc_lat.append(round(geoloc[i][0], 4))

    return geoloc_lat, geoloc_lng


def prepare_data(origin, radius):
    geoloc_sport = pd.read_csv(
        resourcedir + 'geoloc_groups_id.csv', encoding='latin-1')
    geoloc_sport = geoloc_sport[['latitude',
                                 'longitude', 'groups_id', 'sum_sports']]
    geoloc_sport = geoloc_sport.loc[pd.isnull(
        geoloc_sport.groups_id) == False].reset_index(drop=True)  # Remove missing groups
    geoloc_sport['groups_id'] = geoloc_sport['groups_id'].astype(int)
    #print (geoloc_sport.head())
    #grouped_data = geoloc_sport.groupby(['latitude','longitude','groups_id']).sum().reset_index()

    geoloc_lat, geoloc_lng = get_coords(origin, radius)
    geoloc_sport_radius = geoloc_sport.loc[geoloc_sport['latitude'].isin(
        geoloc_lat) | geoloc_sport['longitude'].isin(geoloc_lng)]
    geoloc_sport_radius = geoloc_sport_radius[['groups_id', 'sum_sports']]
    grouped_data = geoloc_sport_radius.groupby(['groups_id']).sum(
    ).reset_index().sort_values(by='sum_sports', ascending=False)

    print(grouped_data.head())
    return grouped_data


if __name__ == "__main__":
    prepare_data(ORIGIN, RADIUS)
