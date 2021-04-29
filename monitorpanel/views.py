from django.http import HttpResponse

def index(request):
    with open('front/index.html','rb') as f:
        html = f.read()
    return HttpResponse(html)