from django.http import HttpResponse, JsonResponse
import requests
import requests_cache

from .models import Location

requests_cache.install_cache(
    'amilia_cache', backend='sqlite', expire_after=24*60*60
)


def get_locations(request, lng=45.5035, lat=-73.5685, radius=10):
    r = requests.get(
        'https://www.amilia.com/api/v3/fr/locations?type=Radius&coordinates=%f,%f&radius=%i'
        % (lng, lat, radius))

    for location in r.json()['Items']:
        Location.objects.get_or_create(
            locationId=location['Id'],
            name=location['Name'],
            fullName=location['FullName'],
            description=location['Description'],
            telephone=location['Telephone'],
            telephoneExtension=location['TelephoneExtension'],
            parentId=location['ParentId'],
            topParentId=location['TopParentId'],
            ancestorIds=location['AncestorIds'],
            address=location['Address'],
            keywords=location['Keywords'],
        )

    return JsonResponse(r.json(), safe=False)


    return JsonResponse(r.json(), safe=False)
