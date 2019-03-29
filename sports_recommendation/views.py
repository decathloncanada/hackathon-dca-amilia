from django.http import HttpResponse, JsonResponse
import requests
import requests_cache
import json

from .models import Location

requests_cache.install_cache(
    'amilia_cache', backend='sqlite', expire_after=24*60*60
)


def get_activities(self, latitude=45.511, longitude=-73.582, radius=2):
    # exract places at this location
    url = 'https://www.amilia.com/api/v3/fr/locations?type=Radius&coordinates={},{}&radius={}&page=1&perpage=2000'.format(
        latitude, longitude, radius)
    r = requests.get(url)
    data = json.loads(r.text)

    locations = [i['Id'] for i in data['Items']]

    # extract all the activities
    activities = []
    for i in locations:
        url = ("https://www.amilia.com/api/v3/fr/locations/%i/activities?showHidden=false&showCancelled=false&showChildrenActivities=false"
               % i)
        r = requests.get(url)
        activities.append(r.json())

    # extract all the activities with sports
    sport_activities = []

    for a in range(len(activities)):
        for b in activities[a]['Items']:
            if len(b['Keywords']) is not 0:
                sport_activities.append(b)

    return JsonResponse(sport_activities, safe=False)
