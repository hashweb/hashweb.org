#!/usr/bin/python
import subprocess
import os
import getpass
import sys
import json
import urllib2

if not os.path.exists('config.json'):
	print "First a config file needs to be created......"
	userName = raw_input('Please enter your user name (pref your OS username): ')
	userPass = getpass.getpass('Please enter your password for the Postgresql database (won\'t echo)');
	with open('config.json', 'w') as configFile:
		configText = """
{
	"db": {
		"host": "127.0.0.1",
		"dbname": "logs_stats",
		"user": "%s",
		"password": "%s"
	},
	"vm_config" : {
		"shared_folder": [
			{"name": "logs_stats", "path": "/home/%s/logs_stats", "host_path" : "../logs_stats"}
		]
	}
}
	""" % (userName, userPass, userName)
		configFile.write(configText)
	confirm = raw_input("Are you running this script from the host machine? yes/no: ")
	if (confirm == "yes"):
		print "Run again from guest"
		sys.exit();

# open the config file
with open('config.json', 'r') as configFile:
	data = json.loads(configFile.read());

userName = data['db']['user']
userPass = data['db']['password']

# Postgresql needs to be installed
# libpq-dev and python-dev needs to be installed for psycopg2
# ipython notebook for a better shell
subprocess.call(['apt-get', 'update'])
#'libjpeg8', 'libjpeg-dev', 'libpng', 'libpng-dev' are for Django-wiki (pip) / http://django-wiki.readthedocs.org/en/latest/installation.html
subprocess.call(['apt-get', 'install', '-y', 'postgresql', 'libpq-dev', 'python-dev', 'python-pip', 'git', 'ipython-notebook', 'memcached', 'htop', 'libjpeg8', 'libjpeg-dev', 'libpng12-0', 'libpng12-dev'])
subprocess.call(['pip', 'install', 'psycopg2'])
subprocess.call(['pip', 'install', 'django'])
subprocess.call(['pip', 'install', 'python-memcached'])
subprocess.call(['pip', 'install', 'django-subdomains']) # Seperate logs, wiki and main site
subprocess.call(['pip', 'install', 'Pillow']) # for django-wiki
subprocess.call(['pip', 'install', 'wiki'])


# Get Limnoria & install it
os.chdir('../');
if not os.path.exists('Limnoria'):
	print 'Grabbing dependancy Limnoria...'
	subprocess.call(['git', 'clone', 'git://github.com/ProgVal/Limnoria.git']);
os.chdir('Limnoria');
subprocess.call(['python', 'setup.py', 'install'])
os.chdir('../')

# Get the bootstrapped logbot project
subprocess.call(['wget', 'http://logs.hashweb.org/dev/logbot.tar.gz'])
subprocess.call(['mkdir', 'logbot'])
subprocess.call(['tar', '-zxvf', 'logbot.tar.gz', 'logbot'])


print 'Pulling down latest database dump....'
os.chdir('logbot/plugins/LogsToDB')
os.remove('logs_stats.sql')
subprocess.call(['wget', 'http://logs.hashweb.org/dev/logs_stats.sql'])

#Start up memcached
print 'Starting up Memcached....'
subprocess.call(['memcached', '-d', '-s', '/tmp.memcached.sock'])

# Creating a new user is a pain, so just let sandboxed users use the postgres user
# os.system('echo "CREATE ROLE %s LOGIN ENCRYPTED PASSWORD \'%s\';" | sudo -u postgres psql' % (userName, userPass))
os.system('echo "CREATE DATABASE logs_stats" | sudo -u postgres psql')
os.system('sudo -u postgres psql logs_stats < logs_stats.sql')
os.system('echo "ALTER USER postgres WITH PASSWORD \'%s\'" | sudo -u postgres psql' % userPass)
os.system('echo "CREATE DATABASE hashweb" | sudo -u postgres psql')