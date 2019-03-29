from django.http import HttpResponse

def test(request):
    return HttpResponse("<h2>This is a test</h2>")
