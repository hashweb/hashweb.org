import json
import urllib

from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'main/home.html', locals())
