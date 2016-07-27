#!/usr/bin/python3
import subprocess
import os
import getpass
import sys
import json

if not os.path.exists('config.json'):
	print("First a config file needs to be created......")
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
subprocess.call(['apt-get', 'install', '-y', 'postgresql', 'libpq-dev', 'python3-dev', 'python3-pip', 'git', 'ipython-notebook', 'memcached', 'htop'])
subprocess.call(['pip3', 'install', 'psycopg2'])
subprocess.call(['pip3', 'install', 'Django'])
subprocess.call(['pip3', 'install', 'python-memcached'])
subprocess.call(['pip3', 'install', 'uwsgitop']) # Useful for monitering uwsgi processes
subprocess.call(['pip3', 'install', 'django-debug-toolbar'])
subprocess.call(['pip3', 'install', 'django_notify'])


# Get Limnoria & install it
os.chdir('../');
if not os.path.exists('Limnoria'):
	print('Grabbing dependancy Limnoria...')
	subprocess.call(['git', 'clone', 'git://github.com/ProgVal/Limnoria.git']);
os.chdir('Limnoria');
subprocess.call(['python3', 'setup.py', 'install'])
os.chdir('../')

# # Get the bootstrapped logbot project
# subprocess.call(['wget', 'http://logs.hashweb.org/dev/logbot.tar.gz'])
# subprocess.call(['mkdir', 'logbot'])
# subprocess.call(['tar', '-zxvf', 'logbot.tar.gz', 'logbot'])


print('Pulling down latest database dump....')
# os.chdir('logbot/plugins/LogsToDB')
# os.remove('logs_stats.sql')
subprocess.call(['wget', 'http://logs.hashweb.org/dev/hashweb_all.sql'])

#Start up memcached
print('Starting up Memcached....')
os.system('memcached -d -s /tmp/memcached.sock')

# Creating a new user is a pain, so just let sandboxed users use the postgres user
# os.system('echo "CREATE ROLE %s LOGIN ENCRYPTED PASSWORD \'%s\';" | sudo -u postgres psql' % (userName, userPass))
os.system('sudo -u postgres psql -f hashweb_all.sql postgres')