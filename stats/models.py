# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines for those models you wish to give write DB access
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

import datetime
from datetime import timedelta, date
import json
import re
import hashlib

from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.db import connections
from django.utils.encoding import python_2_unicode_compatible
from django.core.cache import cache

@python_2_unicode_compatible
class Channels(models.Model):
    id = models.IntegerField(primary_key=True)
    channel_name = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'channels'

    def __str__(self):
        return self.channel_name

class Messages(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey('Users', db_column='user')
    content = models.TextField(blank=True)
    action = models.TextField(blank=True) # This field type is a guess.
    timestamp = models.DateTimeField(blank=True, null=True)
    channel_id = models.ForeignKey('Channels', db_column='channel_id')

    class Meta:
        managed = False
        db_table = 'messages'

@python_2_unicode_compatible
class UserCount(models.Model):
    id = models.IntegerField(primary_key=True)
    count = models.IntegerField()
    timestamp = models.DateTimeField(blank=True, null=True)
    channel_id = models.IntegerField(blank=True, null=True)
    topic = models.CharField(max_length=100, blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'user_count'

    def __str__(self):
        return self.count

@python_2_unicode_compatible
class Users(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    user = models.TextField(blank=True)
    host = models.CharField(max_length=100, blank=True)
    in_use = models.NullBooleanField()
    karma = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'users'

    def __str__(self):
        return self.user


class Bans(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    banmask = models.CharField(max_length=200)
    timestamp = models.DateTimeField(blank=True, null=True)
    reminder_time = models.CharField(max_length=100, blank=True)
    reason = models.CharField(max_length=500, blank=True)
    userid = models.ForeignKey('Users', related_name='+', db_column='userid')
    banned_by = models.CharField(max_length=200, blank=True)
    user_name = models.CharField(max_length=200, blank=True)
    channel = models.ForeignKey('Channels', related_name='+', db_column='channel')
    still_banned = models.NullBooleanField()
    banned_by_id = models.ForeignKey('Users', related_name='+', db_column='banned_by_id')
    row_processed = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'bans'


def _getChannelID(channelName):
    """
    Returns the correct ID for the channelName provided
    """
    if cache.get('getChannelID_' + channelName):
        channelID = cache.get('getChannelID_' + channelName)
        return channelID
    else:
        if len(Channels.objects.using('stats').filter(channel_name=channelName)):
            channelID = Channels.objects.using('stats').filter(channel_name=channelName)[0].id
            # ChannelIDs are never going to change, so give them a long cache time, 1 day should do
            cache.set('getChannelID_' + channelName, channelID, 86400)
            return channelID
        else:
            return False


def getFullUserCount(channelName, timefrom=False, timeto=False):
    """
    Returns the full user count table, including userCount and timestamp
    """

    channel = _getChannelID(channelName)
    results = []
    if (channel):
        if (timefrom):
            for i in UserCount.objects.using('stats').filter(channel_id=channel, timestamp__gte=timefrom).order_by('-timestamp'):
                results.append({"count": i.count, "timestamp": i.timestamp.strftime('%a, %d %b %Y %H:%M:%S +0000')})
        else:
            # Full user count, look in the cache
            if cache.get('getFullUserCount'):
                results = cache.get('getFullUserCount')
            else:
                for i in UserCount.objects.using('stats').filter(channel_id=channel).order_by('-timestamp')[::100]: #iterate over every 100 to bring the data payload down
                    results.append({"count": i.count, "timestamp": i.timestamp.strftime('%a, %d %b %Y %H:%M:%S +0000')})
                #cache the result because its heavy
                cache.set('getFullUserCount', results, 3600)
        return results
    return False

def getFullUserCountToday(channelName):
    yesterday = datetime.datetime.now() - datetime.timedelta(days = 1)
    yesterday = timezone.make_aware(yesterday, timezone.get_current_timezone())
    return getFullUserCount(channelName, yesterday)

def getFullUserCountWeek(channelName):
    week = datetime.datetime.now() - datetime.timedelta(days = 7)
    week = timezone.make_aware(week, timezone.get_current_timezone())
    return getFullUserCount(channelName, week)

def getKarmaUsers(channelName):
    if (cache.get('getKarmaUsers') is None):
        result = Users.objects.using('stats').filter(karma__gt=0).values('user').annotate(karma=Sum('karma')).order_by('-karma')[:60];
        result = list(result)
        resultSet = []
        for i in result:
            resultSet.append({'user': i['user'], 'noOfKarma': i['karma']})
        cache.set('getKarmaUsers', resultSet, 600)
    else:
        resultSet = cache.get('getKarmaUsers')
    return resultSet


def getChattyUsers(channelName):
    # Warning, this does not filter by channel, default #web
    if (cache.get('getChattyUsers') is None):
        result = Users.objects.using('stats').values('user').annotate(noOfMessages=models.Count('messages')).values_list('user', 'noOfMessages').order_by('-noOfMessages')[:60]
        result = list(result)
        resultSet = []
        for i in result:
            resultSet.append({'user': i[0], 'noOfMessages': i[1]})
        cache.set('getChattyUsers', resultSet, 86400)
    else:
        resultSet = cache.get('getChattyUsers')
    return resultSet

def getUserProfanity(channelName):
    #warning this does not filter by channel, default #web
    # select users.user, count(users.user) as userCount from messages inner join users on (messages.user = users.id) where to_tsvector('english', content) @@ to_tsquery('english', 'fuck') group by  users.user order by userCount desc;

    resultSet = []
    for i in Users.objects.using('stats').raw("select users.user, users.id, count(users.user) as userCount from messages inner join users on (messages.user = users.id) where to_tsvector('english', content) @@ to_tsquery('english', 'fuck') group by  users.user, users.id order by userCount desc LIMIT 20;"):
        resultSet.append({'user': i.user, 'noOfMessages': i.usercount})
    return resultSet

# def getLatestFiddles(channelName, userName = None):
#     """
#     Second argument is optional, if only first option is passed, then it will check fiddles across the whole channel
#     """

#     # Messages.objects.filter(channel_id=1, content__contains='http://jsfiddle.net/').order_by('-timestamp')

#     channel = _getChannelID(channelName)
#     if userName is None:
#         query = "select *, regexp_matches(content, '(http://jsfiddle.net/[^\s]*)') from messages inner join users on (messages.user = users.id) WHERE channel_id = %s order by messages.timestamp desc LIMIT 5"
#         arguments = [channel]
#     else:
#         query = "select *, regexp_matches(content, '(http://jsfiddle.net/[^\s]*)') from messages inner join users on (messages.user = users.id) WHERE channel_id = %s AND users.user = %s order by messages.timestamp desc LIMIT 5"
#         arguments = [channel, userName]

#     collection = []
#     for i in Messages.objects.raw(query, arguments).using('stats'):
#         collection.append({'fiddleLink': i.regexp_matches[0], 'user': i.user_id, 'timestamp': i.timestamp})
#     return collection



def getLatestFiddles(channelName, userName = None):
    """
    This is a large query which needs to cached
    Second argument is optional, if only first option is passed, then it will check fiddles across the whole channel
    """
    channel = _getChannelID(channelName)
    collection = []
    if userName is None:
        if (cache.get('latestFiddles') is None):
            for i in Messages.objects.filter(channel_id=1, content__contains='http://jsfiddle.net/').order_by('-timestamp')[:5]:
                if re.search('http://jsfiddle.net/[^\s]*', i.content):
                    fiddleLink = re.search('http://jsfiddle.net/[^\s]*', i.content).group(0)
                    collection.append({'fiddleLink': fiddleLink, 'user': i.user, 'timestamp': i.timestamp, 'id': i.id})

            cache.set('latestFiddles', collection, 300)
        else:
            collection = cache.get('latestFiddles')

    else:
        if cache.get('latestFiddles_' + userName) is None:
            for i in Messages.objects.filter(channel_id=1, content__contains='http://jsfiddle.net/', user__user=userName).order_by('-timestamp')[:5]:
                if re.search('http://jsfiddle.net/[^\s]*', i.content):
                    fiddleLink = re.search('http://jsfiddle.net/[^\s]*', i.content).group(0)
                    collection.append({'fiddleLink': fiddleLink, 'user': i.user, 'timestamp': i.timestamp, 'id': i.id})
            cache.set('latestFiddles_' + userName, collection, 300)
        else:
            collection = cache.get('latestFiddles_' + userName)

    return collection


def getKarma(userName):
    if doesUserExist(userName):
        return Users.objects.using('stats').filter(user=userName).aggregate(models.Sum('karma'))
    return False

def addKarma(username, points):
    username = getNormalizedUserName(username)
    userObj = getUserLastSeen('#web', username).user
    userObj.karma = userObj.karma + points
    userObj.save()


def getMostFullTime(channelName):
    # select count, timestamp from user_count WHERE channel_id = 1 order by count desc LIMIT 1;
    channel = _getChannelID(channelName)
    result = {}
    mostFullTime = UserCount.objects.using('stats').filter(channel_id=channel).order_by('-count').values_list('count', 'timestamp')[0]
    result['count'] = mostFullTime[0]
    result['timestamp'] = mostFullTime[1]
    result['timeSince'] = timezone.now() - mostFullTime[1]

    return result

def getUserLastSeen(channelName, username):
    if (cache.get('getUserLastSeen' + channelName + username)):
        return cache.get('getUserLastSeen' + channelName + username)
    else:
        # select * from users inner join messages on (users.id = messages.user) where users.user = 'Jayflux' AND action = 'message' AND channel_id = 1 order by timestamp asc LIMIT 1;
        channel = _getChannelID(channelName)
        lastSeenObj = Messages.objects.using('stats').filter(user__user__iexact=username).filter(action='message').filter(channel_id=channel).order_by('-timestamp')[0]
        cache.set('getUserLastSeen' + channelName + username, lastSeenObj, 300)
        return lastSeenObj

def getUserFirstSeen(channelName, username):
    if (cache.get('getUserFirstSeen' + channelName + username)):
        return cache.get('getUserFirstSeen' + channelName + username)
    else:

        # reverse of last see
        # TODO: First seen could be cached for a long time as its data that won't change
        channel = _getChannelID(channelName)
        firstSeenObj = Messages.objects.using('stats').filter(user__user__iexact=username).filter(action='message').filter(channel_id=channel).order_by('timestamp')[0]
        cache.set('getUserFirstSeen' + channelName + username, firstSeenObj, 604800) # < this data will never change, cache for a week
        return firstSeenObj

def lastSeenDelta(channelName, userName):
    lastSeen = getUserLastSeen(channelName, userName)
    notSeenFor = timezone.now() - lastSeen.timestamp
    return notSeenFor


def getConvoPartialFromID(channelName, message_ID, length):
    channel = _getChannelID(channelName)
    message_ID_end =  message_ID + length;
    return Messages.objects.using('stats').filter(id__gte=message_ID).filter(id__lt=message_ID_end).filter(channel_id=channel).filter(action='message').select_related('user')

def doesUserExist(username=None):
    if Users.objects.using('stats').filter(user=username):
        return True
    else:
        return False

def hasUserSpoken(username=None):
    if Messages.objects.using('stats').filter(user__user__iexact=username):
        return True
    else:
        return False


def getFirstAndLastSeen(channelName, username=None):

    firstSeen = getUserFirstSeen(channelName, username)
    lastSeen = getUserLastSeen(channelName, username)
    username = firstSeen.user.user

    # Get the last 3 messages including the last seen
    firstSeen.id = firstSeen.id - 2
    lastSeen.id = lastSeen.id - 2
    firstSeenConvo = getConvoPartialFromID(channelName, firstSeen.id, 5)
    for item in firstSeenConvo:
        if item.user.user == username:
            item.isUser = 'user'
        else:
            item.isUser = ''
    lastSeenConvo  = getConvoPartialFromID(channelName, lastSeen.id, 5)
    for item in lastSeenConvo:
        if item.user.user == username:
            item.isUser = 'user'
        else:
            item.isUser = ''

    return (firstSeenConvo, lastSeenConvo)


def getChannelTopic(channelName):
    # select topic from user_count WHERE channel_id = 1 order by timestamp desc LIMIT 1;
    channel = _getChannelID(channelName)
    return UserCount.objects.using('stats').filter(channel_id=channel).order_by('-timestamp')[0].topic

def isUserOnline(username):
    # select action from messages inner join users on (messages.user = users.id) where users.user = 'Jayflux' order by timestamp desc LIMIT 1;
    result = Messages.objects.using('stats').select_related('user').filter(user__user__iexact=username).order_by('-timestamp').values_list('action')[0]
    if result[0] == 'quit' or result[0] == 'part':
        return False 
    else:
        return True

# This method provides a good way of knowing if a user has spoken or not, if the returned result is 0, we have an existing user, who has never spoken, (lurker)
def userMessageCountOverall(channelName, username):
    if (cache.get('userMessageCountOverall__' + channelName + username)):
        return cache.get('userMessageCountOverall__' + channelName + username)
    else:
        channel = _getChannelID(channelName)
        return len(Messages.objects.using('stats').filter(user__user=username, channel_id=channel, action='message'))

# Bring back capital letters
# This can be cached
def getNormalizedUserName(username):
    if (cache.get('getNormalizedUserName_' + username)):
        return cache.get('getNormalizedUserName_' + username)
    else:
        usersObj = Users.objects.using('stats').filter(user__iexact=username) # This call will return multiple objects for every combination of hostname (we only care about the first one)
        if usersObj:
            normalizedName = usersObj[0].user
            cache.set('getNormalizedUserName_' + username, normalizedName, 86400)
            return normalizedName
    return False

def getUserTimeOnline(channelName, username):
    # Django 1.6 cannot aggregate by date or extract hours from timestamps easily (coming in 1.7), so until then I need to do a raw query
    # TODO: not namespaced by channel
    if (cache.get('getUserTimeOnline__' + username)):
        return cache.get('getUserTimeOnline__' + username)
    else:
        overallCount = userMessageCountOverall(channelName, username)
        results = []
        cursor = connections['stats'].cursor()
        cursor.execute("select date_part, count(date_part) from (select extract(hour from timestamp) AS date_part, content from messages inner join users on (users.id = messages.user) WHERE users.user = %s AND action = 'message') as foo group by date_part order by date_part;", [username])
        for i in cursor.fetchall():
            # Get percentage
            perc = (float(i[1]) / overallCount) * 100
            perc = round(perc, 2)
            results.append({'time': int(i[0]), 'hours': i[1], 'perc': perc})

        cache.set('getUserTimeOnline__' + username, results, 300)
        return results
        

# This is a slow query, so will need caching, start off with 1 hour
def getTotalMessagesFromChannel(channelName):
    if (cache.get('getTotalMessagesFromChannel_' + channelName)):
        return cache.get('getTotalMessagesFromChannel_' + channelName)
    else:
        result = Messages.objects.filter(action='message').using('stats').count()
        cache.set('getTotalMessagesFromChannel_' + channelName, result, 60)
        return result

def search(channelName, query):
    # Cache keys cannot have spaces in them, hash them up, as we never know what people will type in
    key = hashlib.sha256(b'search_' + query.encode('utf-8')).hexdigest()
    channel = _getChannelID(channelName)
    results = []
    if cache.get(key):
        return cache.get(key)
    else:
        # scope by user
        userRegex = r'user\:\s?(\w+)\s?'
        # If someone is searching by user, scope by user
        if re.search(userRegex, query) and len(re.search(userRegex, query).groups()) > 0:
            user = re.search(userRegex, query).group(1)
            query = re.sub(userRegex, '', query)
            # If there's a search query, scope that query by user
            if query:
                for i in Messages.objects.filter(channel_id=1, action="message", content__icontains=query, user__user__iexact=user).order_by('-timestamp')[:60]:
                    results.append({'user': i.user.user, 'content': i.content, 'id': i.id, 'timestamp': i.timestamp})
            else:
                for i in Messages.objects.filter(channel_id=1, action="message", user__user__iexact=user).order_by('-timestamp')[:60]:
                    results.append({'user': i.user.user, 'content': i.content, 'id': i.id, 'timestamp': i.timestamp})
        else:
            for i in Messages.objects.filter(channel_id=1, action="message", content__icontains=query).order_by('-timestamp')[:60]:
                results.append({'user': i.user.user, 'content': i.content, 'id': i.id, 'timestamp': i.timestamp})

        cache.set(key, results, 600)
        return results

def avgPerDay(channelName, userName):
    if cache.get('avgPerDay_' + channelName + userName):
        return cache.get('avgPerDay_' + channelName + userName)
    else:
        channel = _getChannelID(channelName)
        userName = getNormalizedUserName(userName)
        totalMessages = userMessageCountOverall(channelName, userName)
        lastSeen = getUserLastSeen(channelName, userName)
        firstSeen = getUserFirstSeen(channelName, userName)
        daysSinceRegistered = (lastSeen.timestamp - firstSeen.timestamp).days
        # User may not have any posts at all, days since registered also uses posts to work out when a user started talking
        # Both or either of these could be 0, if a user has joined a channel but never spoke
        if totalMessages and daysSinceRegistered:
            # start with how long the user has been in #web
            # then divide the number of posts into those days
            cache.set('avgPerDay_' + channelName + userName, (totalMessages / daysSinceRegistered), 300)
            return totalMessages / daysSinceRegistered
        else:
            cache.set('avgPerDay_' + channelName + userName, 0, 300)
            return 0

def get_recent_user_by_id(username):
    """Very basic model which will return the ID for a given user or false"""
    """It works by finding the most recent message from a user, then returning the ID"""
    """Soon there will be a similar model which will work by most posts, and not the last post"""
    try:
        user = Messages.objects.filter(user__user=username).order_by('-timestamp')[0].user
        return user
    except:
        return False



def convert_banmask_to_userObj(banmask):
    """Using a banmask string, return a userObject or False"""

    # We need to make sure any occurance of * is converted to .* (so its regex compatible)
    banmask = re.sub('\*', '.*', banmask)
    try:
        userObj = Messages.objects.filter(user__host__iregex=banmask).order_by('-timestamp')[0].user
    except:
        return False

    return userObj

#  Fill out the blanks in the Bans table, do some processing to reverse look-up the banmask with an actual user
def process_bans_table():
    # Lets loop through all bans that have not been processed and where the user is still banned
    for banObj in Bans.objects.filter(row_processed=False, still_banned=True):
        # We need to convert the banmask into an actual user name
        banmask = banObj.banmask
        userObj = convert_banmask_to_userObj(banmask)

        if (userObj):
            banObj.user_name = userObj.user
            banObj.userid = userObj
            # now lets get ther banner's infomation
            banned_by_id = get_recent_user_by_id(banObj.banned_by)
            if (banned_by_id):
                banObj.banned_by_id = banned_by_id

            banObj.row_processed = True
            banObj.save()


def get_list_of_bans():
    return Bans.objects.filter(still_banned=True).order_by("-timestamp")

def update_ban_obj(banID, banInput):
    try:
        banObj = Bans.objects.filter(id=banID)[0]
    except:
        return False

    if banObj and banInput:
        if 'reminderTime' in banInput:
            banObj.reminder_time = banInput['reminderTime']

        if 'reason' in banInput:
            banObj.reason = banInput['reason']

        banObj.save()
        return True
    else:
        return False
