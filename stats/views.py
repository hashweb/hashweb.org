import json
from django.shortcuts import render
from django.http import HttpResponse
from stats import models

# Create your views here.
def index(request, channelName):
	channelName = '#' + channelName
	# fullUserCount = models.getFullUserCount(channelName)
	mostFullTime = __getMostFullTime(channelName)
	topic = models.getChannelTopic(channelName)
	fiddles = models.getLatestFiddles(channelName)
	return render(request, 'stats/index.html', locals())

def getUserInfo(request, channelName, username):
	channelName = '#' + channelName
	username = models.getNormalizedUserName(username)
	mostFullTime = __getMostFullTime(channelName)
	firstAndLastSeenConvo = models.getFirstAndLastSeen(channelName, username)
	firstSeen = firstAndLastSeenConvo[0]
	lastSeen = firstAndLastSeenConvo[1]
	isUserOnline = models.isUserOnline(username)
	userMessageCountOverall = models.userMessageCountOverall(channelName, username)
	
	# Get the last time the user was seen
	notSeenFor = {}
	notSeenFor['days'] = models.lastSeenDelta(channelName, username).days
	notSeenFor['seconds'] = models.lastSeenDelta(channelName, username).seconds
	notSeenFor['hours'] = notSeenFor['seconds'] // 3600
	notSeenFor['seconds'] = notSeenFor['seconds'] - (notSeenFor['hours'] * 3600)
	notSeenFor['minutes'] = notSeenFor['seconds'] // 60
	notSeenFor['seconds'] = (notSeenFor['minutes'] * 60)
	return render(request, 'stats/userinfo.html', locals())


def getFullUserCount(request, channelName):
	channelName = '#' + channelName
	fullUserCount = models.getFullUserCount(channelName)
	return HttpResponse(json.dumps(fullUserCount), content_type="application/json")

def getFullUserCountToday(request, channelName):
	channelName = '#' + channelName
	fullUserCount = models.getFullUserCountToday(channelName)
	return HttpResponse(json.dumps(fullUserCount), content_type="application/json")

def getFullUserCountWeek(request, channelName):
	channelName = '#' + channelName
	fullUserCount = models.getFullUserCountWeek(channelName)
	return HttpResponse(json.dumps(fullUserCount), content_type="application/json")

def getChattyUsers(request, channelName):
	channelName = '#' + channelName
	chattyUsers = models.getChattyUsers(channelName)
	return HttpResponse(json.dumps(chattyUsers), content_type="application/json")

def __getMostFullTime(channelName):
	mostFullTime = models.getMostFullTime(channelName)
	return mostFullTime
