from rest_framework import routers # type: ignore
from posthog.models import Event, Team
from rest_framework import serializers, viewsets # type: ignore
from django.http import HttpResponse, JsonResponse
import json
import base64
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlparse

class EventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'data', 'timestamp']


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.none()
    serializer_class = EventSerializer

def get_ip_address(request):
    """ use requestobject to fetch client machine's IP Address """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')    ### Real IP address of client Machine
    return ip   

def cors_response(request, response):
    url = urlparse(request.META['HTTP_REFERER'])
    response["Access-Control-Allow-Origin"] = "%s://%s" % (url.scheme, url.netloc)
    response["Access-Control-Allow-Credentials"] = True
    response["Access-Control-Allow-Methods"] = 'GET, POST, OPTIONS'
    response["Access-Control-Allow-Headers"] = 'X-Requested-With'
    return response

@csrf_exempt
def get_event(request):
    data = request.GET.get('data')
    if not data:
        return HttpResponse("1")
    
    data = json.loads(base64.b64decode(data))
    print(data)

    Event.objects.create(
        event=data['event'],
        properties=data['properties'],
        ip=get_ip_address(request),
        team=Team.objects.get(api_token=data['properties']['token'])
    )
    return cors_response(request, HttpResponse("1"))


@csrf_exempt
def get_decide(request):
    return cors_response(request, JsonResponse({"config": {"enable_collect_everything": True}}))