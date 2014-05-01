import json
import urllib

from django.shortcuts import render
from django.http import HttpResponse
from stats import models
from django.shortcuts import redirect
from django.views.decorators.cache import cache_page
from django import forms

# Create your views here.


# @cache_page(60 * 5)
def index(request):
	channelNameHash = 'web'
	channelName = '#' + 'web'
	# fullUserCount = models.getFullUserCount(channelName)
	mostFullTime = __getMostFullTime(channelName)
	topic = models.getChannelTopic(channelName)
	fiddles = models.getLatestFiddles(channelName)
	totalMessagesFromChannel = '{0:,}'.format(models.getTotalMessagesFromChannel(channelName))
	return render(request, 'stats/index.html', locals())

# @cache_page(60 * 2)
def getUserInfo(request, username):
	channelName = '#' + 'web'
	# This user does not exist in the database
	if (models.hasUserSpoken(username) == False):
		#render a 'cannot find user' page
		return render(request, 'stats/nouser.html', locals())

	username = models.getNormalizedUserName(username)
	mostFullTime = __getMostFullTime(channelName)
	firstAndLastSeenConvo = models.getFirstAndLastSeen(channelName, username)
	firstSeen = firstAndLastSeenConvo[0]
	lastSeen = firstAndLastSeenConvo[1]
	isUserOnline = models.isUserOnline(username)
	userMessageCountOverall = '{0:,}'.format(models.userMessageCountOverall(channelName, username))
	fiddles = models.getLatestFiddles(channelName, username)
	
	# Get the last time the user was seen
	notSeenFor = {}
	notSeenFor['days'] = models.lastSeenDelta(channelName, username).days
	notSeenFor['seconds'] = models.lastSeenDelta(channelName, username).seconds
	notSeenFor['hours'] = notSeenFor['seconds'] // 3600
	notSeenFor['seconds'] = notSeenFor['seconds'] - (notSeenFor['hours'] * 3600)
	notSeenFor['minutes'] = notSeenFor['seconds'] // 60
	notSeenFor['seconds'] = (notSeenFor['minutes'] * 60)
	return render(request, 'stats/userinfo.html', locals())

def search(request):
	if request.method == 'GET':
		q = request.GET['q']
		results = models.search('web', q)

	return render(request, 'stats/searchLanding.html', locals())

def getConvoPartial(request, id):
	id = int(id)
	id = id - 10;
	results = models.getConvoPartialFromID('#web', id, 100)
	id = id + 10;
	return render(request, 'stats/log_convo.html', locals())


def getFullUserCount(request):
	channelName = '#' + 'web'
	fullUserCount = models.getFullUserCount(channelName)
	return HttpResponse(json.dumps(fullUserCount), content_type="application/json")

def getFullUserCountToday(request):
	channelName = '#' + 'web'
	fullUserCount = models.getFullUserCountToday(channelName)
	return HttpResponse(json.dumps(fullUserCount), content_type="application/json")

def getFullUserCountWeek(request):
	channelName = '#' + 'web'
	fullUserCount = models.getFullUserCountWeek(channelName)
	return HttpResponse(json.dumps(fullUserCount), content_type="application/json")

def getChattyUsers(request):
	channelName = '#' + 'web'
	chattyUsers = models.getChattyUsers(channelName)
	return HttpResponse(json.dumps(chattyUsers), content_type="application/json")

def __getMostFullTime(channelName):
	mostFullTime = models.getMostFullTime(channelName)
	return mostFullTime

def getUserTimeOnline(request, userName):
	channelName = '#' + 'web'
	userName = urllib.unquote(userName)
	return HttpResponse(json.dumps(models.getUserTimeOnline(channelName, userName)), content_type="application/json")