# Create your views here.
from django.shortcuts import render

def index(request):
    return render(request, 'frontpage/index.html')

def robotstxt(request):
    return render(request, 'frontpage/robots.txt', content_type="text/plain")
