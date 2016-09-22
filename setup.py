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
subprocess.call(['apt-get', 'install', '-y', 'postgresql', 'libpq-dev', 'python3-pip', 'git', 'ipython-notebook', 'memcached', 'htop'])
subprocess.call(['pip3', 'install', '-r', 'requirements.txt'])


print('Pulling down latest database dump....')
subprocess.call(['wget', 'http://logs.hashweb.org/dev/hashweb_all.gz'])

#Start up memcached
print('Starting up Memcached....')
os.system('memcached -d -s /tmp/memcached.sock')

# Creating a new user is a pain, so just let sandboxed users use the postgres user
# os.system('echo "CREATE ROLE %s LOGIN ENCRYPTED PASSWORD \'%s\';" | sudo -u postgres psql' % (userName, userPass))
os.system('gunzip -c hashweb_all.gz > hashweb_all.sql')
os.system('sudo -u postgres psql -f hashweb_all.sql postgres')