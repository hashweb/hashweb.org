import json
from django.shortcuts import render
from django.http import HttpResponse
from stats import models

# Create your views here.
def index(request, channelName):
	channelName = '#' + channelName
	fullUserCount = models.getFullUserCount(channelName)
	return render(request, 'stats/index.html', {"fullUserCount" : json.dumps(fullUserCount)})

def getFullUserCount(request, channelName):
	channelName = '#' + channelName
	fullUserCount = models.getFullUserCount(channelName)
	return HttpResponse(json.dumps(fullUserCount), content_type="application/json")

def getFullUserCountToday(request, channelName):
	channelName = '#' + channelName
	fullUserCount = models.getFullUserCountToday(channelName)
	return HttpResponse(json.dumps(fullUserCount), content_type="application/json")