# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines for those models you wish to give write DB access
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals
import datetime
import json

from django.db import models
from django.utils import timezone
from django.core.cache import cache

class Channels(models.Model):
    id = models.IntegerField(primary_key=True)
    channel_name = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'channels'


class Messages(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey('Users', db_column='user')
    content = models.TextField(blank=True)
    action = models.TextField(blank=True) # This field type is a guess.
    timestamp = models.DateTimeField(blank=True, null=True)
    channel_id = models.ForeignKey('Channels')
    class Meta:
        managed = False
        db_table = 'messages'

class UserCount(models.Model):
    id = models.IntegerField(primary_key=True)
    count = models.IntegerField()
    timestamp = models.DateTimeField(blank=True, null=True)
    channel_id = models.IntegerField(blank=True, null=True)
    topic = models.CharField(max_length=100, blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'user_count'

class Users(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    user = models.TextField(blank=True)
    host = models.CharField(max_length=100, blank=True)
    in_use = models.NullBooleanField()
    class Meta:
        managed = False
        db_table = 'users'


def _getChannelID(channelName):
    """
    Returns the correct ID for the channelName provided
    """
    if len(Channels.objects.filter(channel_name=channelName)):
        return Channels.objects.filter(channel_name=channelName)[0].id
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
            for i in UserCount.objects.filter(channel_id=channel, timestamp__gte=timefrom).order_by('-timestamp'):
                results.append({"count": i.count, "timestamp": i.timestamp.strftime('%a, %d %b %Y %H:%M:%S +0000')})
        else:
            # Full user count, look in the cache
            if cache.get('getFullUserCount'):
                results = cache.get('getFullUserCount')
            else:
                for i in UserCount.objects.filter(channel_id=channel).order_by('-timestamp'):
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

def getChattyUsers(channelName):
    # Warning, this does not filter by channel, default #web
    result = Users.objects.annotate(totalCount=models.Count('messages')).values_list('user', 'totalCount').order_by('-totalCount')[:60]
    resultSet = {}
    newResultSet = []
    for item in result:
        if resultSet.has_key(item[0]):
            resultSet[item[0]] += item[1]
        else:
            resultSet[item[0]] = item[1]

    for i in resultSet:
        newResultSet.append({'user': i, 'noOfMessages': resultSet[i]})

    return newResultSet

# get all users
# select userName, sum(countName) as counting from (
#   select users.user as userName, count(messages.user) as countName from messages INNER JOIN users ON (messages.user = users.id) group by messages.user, users.user, users.host order by countName DESC
# ) AS foo GROUP BY foo.username ORDER BY counting DESC;


# select users.user as userName, count(messages.user) as totalCount from messages INNER JOIN users ON (messages.user = users.id) GROUP BY users.user ORDER BY totalCount desc;