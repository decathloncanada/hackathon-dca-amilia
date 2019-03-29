from django.http import HttpResponse, JsonResponse
import requests
import requests_cache
import json
import operator

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
    popular_sports = {}

    for a in range(len(activities)):
        for b in activities[a]['Items']:
            if len(b['Keywords']) is not 0:
                sport_activities.append(b)
                for c in b['Keywords']:
                    if c['Id'] not in popular_sports:
                        popular_sports[c['Id']] = 1
                    else:
                        popular_sports[c['Id']] += 1

    sorted_dic = sorted(popular_sports.items(),
                        key=lambda kv: kv[1], reverse=True)[:5]

    sorted_list = [i[0] for i in sorted_dic]

    decathlon_id = []
    for sport_id in sorted_list:
        r = requests.get(
            'https://www.amilia.com/api/v3/fr/keywords?partner=Decathlon')
        for i in r.json():
            if i['Id'] == sport_id:
                decathlon_id.append(i['PartnerId'])

    return JsonResponse(decathlon_id, safe=False)
