from django.http.response import HttpResponse
from .models import EPCI

def get_epci_boundary(request):
    boundary = ""
    if request.method == "GET":
        epci_id = request.GET.get('epci_id', None)
        epci = EPCI.objects.get(id=epci_id)
        boundary = epci.get_boundary().geojson
    return HttpResponse(boundary)
    