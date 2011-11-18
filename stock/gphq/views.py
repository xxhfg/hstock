# Create your views here.
from django.http import HttpResponse
from stock.gphq import models


def index(request):
    result = ''
    gps = models.GPDM.objects.all()
    for gp in gps:
        result += gp.GPDM + '\n'
    
    return HttpResponse(result)
