from django.http import HttpResponse, JsonResponse
import requests
import requests_cache

def test(request):
    # Example call to the Amilia API
    r = requests.get('https://www.amilia.com/api/v3/fr/locations?type=Radius&coordinates=45.0,-73.5&radius=50&page=1&perpage=250&keywordId=2')
    requests_cache.install_cache('amilia_cache', backend='sqlite', expire_after=60)

    return JsonResponse(r.json(), safe=False)
