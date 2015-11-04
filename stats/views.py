import json
import urllib

from django.shortcuts import render
from django.http import HttpResponse
from stats import models
from django.shortcuts import redirect
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django import forms

# Create your views here.


@cache_page(60 * 5)
def index(request):
	channelNameHash = 'web'
	channelName = '#' + 'web'
	# fullUserCount = models.getFullUserCount(channelName)
	mostFullTime = __getMostFullTime(channelName)
	topic = models.getChannelTopic(channelName)
	fiddles = models.getLatestFiddles(channelName)
	totalMessagesFromChannel = '{0:,}'.format(models.getTotalMessagesFromChannel(channelName))
	return render(request, 'stats/index.html', locals())

@cache_page(60 * 5)
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

	avgPostsPerDay = models.avgPerDay('#web', username)
	return render(request, 'stats/userinfo.html', locals())


def search(request):
	if request.method == 'GET':
		q = request.GET.get('q', None)
		if q:
			results = models.search('web', q)

	return render(request, 'stats/searchLanding.html', locals())

def getConvoPartial(request, id):
	id = int(id)
	id = id - 10;
	results = models.getConvoPartialFromID('#web', id, 100)
	id = id + 10;
	return render(request, 'stats/log_convo.html', locals())

	# ----- Open API stuff ------

def userInfo(request, userName):
	data = {}
	if models.getNormalizedUserName(userName):
		data['username'] = userName = models.getNormalizedUserName(userName)
		data['isUserOnline'] = models.isUserOnline(userName)
		data['karma'] = models.getKarma(userName)['karma__sum']
		# Get the last time the user was seen
		notSeenFor = {}
		notSeenFor['days'] = models.lastSeenDelta('#web', userName).days
		notSeenFor['seconds'] = models.lastSeenDelta('#web', userName).seconds
		notSeenFor['hours'] = notSeenFor['seconds'] // 3600
		notSeenFor['seconds'] = notSeenFor['seconds'] - (notSeenFor['hours'] * 3600)
		notSeenFor['minutes'] = notSeenFor['seconds'] // 60
		notSeenFor['seconds'] = (notSeenFor['minutes'] * 60)
		data['userNotSeenFor'] = notSeenFor

		#  get JS fiddles if user has any
		data['fiddles'] = models.getLatestFiddles('#web', userName)
		if (data['fiddles']):
			for fiddle in data['fiddles']:
				fiddle['timestamp'] = str(fiddle['timestamp'])
				del fiddle['user'] 

		#  Get last seen and first seem
		lastSeen = models.getUserLastSeen('#web', userName)
		data['lastSeen'] = {}
		data['lastSeen']['message'] = lastSeen.content
		data['lastSeen']['timeStamp'] = str(lastSeen.timestamp)
		data['lastSeen']['messageID'] = lastSeen.id

		firstSeen = models.getUserFirstSeen('#web', userName)
		data['firstSeen'] = {}
		data['firstSeen']['message'] = firstSeen.content
		data['firstSeen']['timestamp'] = str(firstSeen.timestamp)
		data['firstSeen']['messageID'] = firstSeen.id

		# Message count
		data['messageCount'] = models.userMessageCountOverall('#web', userName)
		data['avgPostsPerDay'] = models.avgPerDay('#web', userName)

		return HttpResponse(json.dumps(data), content_type="application/json")

	else:
		return HttpResponse(json.dumps({'statusCode': '404', 'response':'Sorry no available user: ' + userName}), status=404)

@csrf_exempt
def addKarma(request, userName):
	userName = models.getNormalizedUserName(userName)
	if userName:
		if request.method == 'POST':
			points = int(request.POST['points'])
			models.addKarma(userName, points)
			return HttpResponse(json.dumps({'statusCode': '200', 'response':'karma updated for ' + userName}), status=200)
		else:
			return HttpResponse(json.dumps({'statusCode': '405', 'response':'Sorry this api is only for POST'}), status=405)
	else:
		return HttpResponse(json.dumps({'statusCode': '404', 'response':'Sorry no available user'}), status=404)

	# ------Private API stuff -----


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



	# ----- Bans -------
def showBansPage(request):
	bansList = models.get_list_of_bans()
	return render(request, 'stats/bans.html', locals())

@csrf_exempt
def reIndexBans(request):
	if (request.method == "POST"):
		models.process_bans_table()
		return HttpResponse(json.dumps({"message": "Table Updated"}), content_type="application/json")
	else:
		return redirect('stats.views.showBansPage')


@csrf_exempt
def adjustBan(request, ID):
	if (request.method == "POST"):
		req = request.POST
		banInput = {}

		if 'reminderTime' in req:
			banInput['reminderTime'] = req.get('reminderTime')

		if 'reason' in req:
			banInput['reason'] = req.get('reason')

		if models.update_ban_obj(ID, banInput) == False:
			return HttpResponse(json.dumps({"message": "Unable to find that ID or Wrong input"}), content_type="application/json")
		else:
			return HttpResponse(json.dumps({"message": "Added!"}), content_type="application/json")
	else:
		return redirect('stats.views.showBansPage')

