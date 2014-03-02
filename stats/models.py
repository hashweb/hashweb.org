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

from django.db import models
from django.utils import timezone

class Channels(models.Model):
    id = models.IntegerField(primary_key=True)
    channel_name = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'channels'

class Messages(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.IntegerField()
    content = models.TextField(blank=True)
    action = models.TextField(blank=True) # This field type is a guess.
    timestamp = models.DateTimeField(blank=True, null=True)
    channel_id = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'messages'

class UserCount(models.Model):
    id = models.IntegerField(primary_key=True)
    count = models.IntegerField()
    timestamp = models.DateTimeField(blank=True, null=True)
    channel_id = models.IntegerField(blank=True, null=True)
    topic = models.CharField(max_length=100, blank=True)
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

def GetMostChattyUsers():
    cursor = connection.cursor()
    cursor.execute('select max(users.user), count(messages.user) as occurrence from messages INNER JOIN users ON (messages.user = users.id) group by messages.user order by occurrence DESC')
    row = cursor.fetchall()

    return row


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
            for i in UserCount.objects.filter(channel_id=channel, timestamp__gte=timefrom):
                results.append({"count": i.count, "timestamp": i.timestamp.strftime('%a, %d %b %Y %H:%M:%S +0000')})
        else:
            for i in UserCount.objects.filter(channel_id=channel):
                results.append({"count": i.count, "timestamp": i.timestamp.strftime('%a, %d %b %Y %H:%M:%S +0000')})

        return results
    return False

def getFullUserCountToday(channelName):
    yesterday = datetime.datetime.now() - datetime.timedelta(days = 1)
    yesterday = timezone.make_aware(yesterday, timezone.get_current_timezone())
    return getFullUserCount(channelName, yesterday)