import json
import urllib

import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.cache import cache_page

# @cache_page(60 * 5)
def index(request):
	return render(request, 'main/home.html', locals())

@cache_page(60 * 5)
def euro_stats(request):
	r = requests.get('http://www.bbc.co.uk/sport/football/european-championship/euro-2016/schedule/group-stage')
	payload = r.text.encode('utf-8')
	euroObj = {}

	soup = BeautifulSoup(payload, 'html.parser')
	for table in soup.select('tbody .table__cell--left'):
		countryCode = table.select('abbr span')[0].contents[0].lower()
		euroObj[countryCode] = {}
		euroObj[countryCode]['name'] = table.select('abbr')[0]['title']
		wins = table.next_sibling.next_sibling
		euroObj[countryCode]['w'] = int(wins.contents[0])
		draws = wins.next_sibling.next_sibling
		euroObj[countryCode]['d'] = int(draws.contents[0])
		loses = draws.next_sibling.next_sibling
		euroObj[countryCode]['l'] = int(loses.contents[0])
		gd = loses.next_sibling.next_sibling
		euroObj[countryCode]['gd'] = int(gd.contents[0])
		pts = gd.next_sibling.next_sibling
		euroObj[countryCode]['pts'] = int(pts.contents[0])

		
	return HttpResponse(json.dumps(euroObj), content_type="application/json")