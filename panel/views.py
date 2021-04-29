from django.shortcuts import render
from django.http import JsonResponse
from .models import NetworkClass
from .serializers import NetworkClassSerializers

def get_network_data(request):
    data = NetworkClass.get_all()
    ser = NetworkClassSerializers(data, many=True)
    result = {
        'code': 0,
        'message': 'success',
        'data': ser.data,
    }
    return JsonResponse(result)
