import json
import urllib

from django.shortcuts import render
from django.http import HttpResponse

# @cache_page(60 * 5)
def index(request):
	return render(request, 'main/home.html', locals())