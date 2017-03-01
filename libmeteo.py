# -*- coding: utf-8 -*-

import re
import urllib
import urllib2
import sys

from StringIO import StringIO
import gzip 

from bs4 import BeautifulSoup
import simplejson as json

from difflib import SequenceMatcher

import utilities

METEO_URL = 'http://www.meteo.lt/%s/miestas?placeCode=%s'
METEO_CITIES_URL = 'https://pro.meteo.lt/dataweb/places/listAllPlaces'

WEATHER_CODES = { 'ic-giedra'   : 32,
		  'ic-giedra-2' : 31,
		  'ic-mazai-debesuota' : 34,
		  'ic-mazai-debesuota-2': 33,
		  'ic-nepastoviai-debesuota': 30,
		  'ic-nepastoviai-debesuota-2': 29,
		  'ic-debesuota-pragiedruliai': 28,
		  'ic-debesuota-pragiedruliai-2': 27,
		  'ic-debesuota': 26,
		  'ic-debesuota_N': 26,
		  'ic-trumpas-lietus': 11,
		  'ic-trumpas-lietus-2': 45,
		  'ic-protarpiais-nedidelis-lietus': 11,
		  'ic-protarpiais-nedidelis-lietus-2': 45,
		  'ic-protarpiais-lietus': 11,
		  'ic-protarpiais-lietus-2': 45,
		  'ic-nedidelis-lietus': 11,
		  'ic-lietus': 12,
		  'ic-smarkus-lietus': 1,
		  'ic-krusa': 18,
		  'ic-slapdriba': 7,
		  'ic-trumpa-slapdriba': 5,
		  'ic-trumpa-slapdriba-2': 5,
		  'ic-protarpiais-slapdriba': 5,
		  'ic-protarpiais-slapdriba-2': 5,
		  'ic-perkunija': 17,
		  'ic-perkunija2': 47,
		  'ic-trumpas-lietus-perkunija': 17,
		  'ic-trumpas-lietus-perkunija-2': 47,
		  'ic-lietus-perkunija': 38,
		  'ic-trumpas-sniegas': 15,
		  'ic-trumpas-sniegas-2': 15,
		  'ic-protarpiais-nedidelis-sniegas': 14,
		  'ic-protarpiais-nedidelis-sniegas-2': 14,
		  'ic-protarpiais-sniegas': 41,
		  'ic-protarpiais-sniegas-2': 46,
		  'ic-nedidelis-sniegas': 15,
		  'ic-sniegas': 42,
		  'ic-smarkus-sniegas': 42,
		  'ic-rukas': 20,
		  'ic-lijundra': 8,
		  'ic-plikledis': 25,
		  'ic-puga': 43,
		  'ic-skvalas': 38,
		  'ic-apledejimas': 25,
		  'ic-vejas': 24,
		  'ic-auksta-temp': 36,
		  'ic-zema-temp': 25,
		  'ic-gaisringumas': 36,
		  'ic-snygis': 43,
		  'ic-pustymas': 43,
		  'ic-debesuota': 26,
		  'ic-debesuota_N': 26,
		  'ic-debesuota_su_pragiedruliais': 28,
		  'ic-debesuota_su_pragiedruliais_N': 27,
		  'ic-giedra_N': 31,
		  'ic-lietus_N': 1,
		  'ic-mazai_debesuota': 34,
		  'ic-mazai_debesuota_N': 33,
		  'ic-nedidelis_lietus': 11,
		  'ic-nedidelis_lietus_N': 45,
		  'ic-lietus_su_perkunija': 38,
		  'ic-lietus_su_perkunija_N': 47,
		  'ic-lijundra_N': 8,
		  'ic-nedidelis_sniegas': 15,
		  'ic-nedidelis_sniegas_N': 15,
		  'ic-nepastoviai_debesuota': 30,
		  'ic-nepastoviai_debesuota_N': 29,
		  'ic-perkunija_N': 47,
		  'ic-protarpiais_lietus': 11,
		  'ic-protarpiais_lietus_N': 45,
		  'ic-protarpiais_nedidelis_lietus': 11,
		  'ic-protarpiais_nedidelis_lietus_N': 45,
		  'ic-protarpiais_nedidelis_sniegas': 14,
		  'ic-protarpiais_nedidelis_sniegas_N': 14,
		  'ic-protarpiais_slapdriba': 5,
		  'ic-protarpiais_slapdriba_N': 5,
		  'ic-protarpiais_sniegas': 41,
		  'ic-protarpiais_sniegas_N': 46,
		  'ic-puga_N': 43,
		  'ic-rukas_N': 20,
		  'ic-slapdriba_N': 7,
		  'ic-smarkus_lietus': 12,
		  'ic-smarkus_lietus_N': 12,
		  'ic-smarkus_sniegas': 42,
		  'ic-smarkus_sniegas_N': 42,
		  'ic-sniegas_N': 46,
		  'ic-trumpa_slapdriba': 5,
		  'ic-trumpa_slapdriba_N': 5,
		  'ic-trumpas_lietus': 11,
		  'ic-trumpas_lietus_N': 45,
		  'ic-trumpas_lietus_su_perkunija': 17,
		  'ic-trumpas_lietus_su_perkunija_N': 47,
		  'ic-trumpas_sniegas': 41,
		  'ic-trumpas_sniegas_N': 46 
		  }

reload(sys) 
sys.setdefaultencoding('utf8')

def getURL(url):
  
  request = urllib2.Request(url)
  request.add_header('Accept-encoding', 'gzip')
  response = urllib2.urlopen(request)
  if response.info().get('Content-Encoding') == 'gzip':
    buf = StringIO(response.read())
    f = gzip.GzipFile(fileobj=buf)
    return f.read()  
  
  return response.read()

def readCondition(tag):
  
  styleCode = ''
  
  for t in tag['class']:
    if t.startswith('ic-'):
      styleCode = t
      break
  
  if not styleCode:
    return 'na'
  
  if styleCode in WEATHER_CODES:
    return WEATHER_CODES[styleCode]
  
  return 'na'

def getData(locid, lang):
  
  result = {}
  
  if not locid:
    locid = 'kaunas'
  
  if not lang:
    lang = 'en_US'
  
  html = getURL(METEO_URL % (lang, locid))  
  soup = BeautifulSoup(html, 'html.parser')
  
  weather_info = soup.find_all('div', class_='weather_info')[0]
  
  left = weather_info.find_all('div', class_='left')[0]
  
  result['location'] = left.find_all('p', class_='large')[0].string
  temperature = int(left.find_all('span', class_='temperature')[0].string)
  result['temperature'] = temperature
  
  condition = left.find_all('span', class_='condition')[0]
  
  result['condition'] = condition['title']
  result['weathercode'] = readCondition(condition)
  
  right = weather_info.find_all('div', class_='right')[0]
  
  result['FeelsLike'] = right.find_all('span', class_='feelLike')[0].string
  result['Humidity'] = right.find_all('span', class_='humidityGround')[0].string
  result['Wind'] = right.find_all('span', class_='windSpeedGround')[0].string
  

  if temperature > 0:
    result['DewPoint'] = utilities.dewpoint(temperature, int(result['Humidity']))
  else:
    result['DewPoint'] = ''
    
  forecast_hours = soup.find_all('tr', class_='forecast-hours')  
  hours = {}
  
  for i, hour in enumerate(forecast_hours):
    data = {}
    
    forecastTime = hour.find_all('span', class_='forecastTime')[0].string
    data['ShortDate'] = forecastTime[0:10].replace('-', '.')
    data['Time'] = forecastTime[11:16].replace('-', ':')
    
    ic = hour.find_all('span', class_='ic')[0]
    data['Outlook'] = ic['title']
    data['weathercode'] = readCondition(ic)
    
    data['Temperature'] = hour.find_all('span', class_='temperature')[0].string
    data['FeelsLike'] = hour.find_all('span', class_='feelLike')[0].string
    data['Humidity'] = hour.find_all('span', class_='humidityGround')[0].string
    data['Precipitation'] = hour.find_all('span', class_='precipitation')[0].string
    data['WindSpeed'] = hour.find_all('span', class_='windSpeedGround')[0].string
    
    windDirectionGroundDegree = int(hour.find_all('span', class_='windDirectionGroundDegree')[0].string)
    windDirectionGroundDegree = (windDirectionGroundDegree + 180 ) % 360
    
    data['windDirectionGroundDegree'] = windDirectionGroundDegree
    data['WindDirection'] = utilities.winddir(windDirectionGroundDegree)
    
    hours[i] = data
    
  result['forecast_hours'] = hours
  result['WindDirection'] = hours[0]['WindDirection']
    
  result['Precipitation'] = soup.find_all('span', class_='precipitation')[0].string
    
    
  days = {}  
  m7days_weather = soup.find_all('div', class_='seven_days_weather')[0]
  forecast_days = m7days_weather.find_all('div', class_='forecast-day')
  
  for i, day in enumerate(forecast_days):
    data = {}
    
    date_key = day.find_all('span', class_='date_key')[0].string
    data['ShortDate'] = date_key[0:4] + '.' + date_key[4:6] + '.' + date_key[6:8]
    
    date = day.find_all('span', class_='date')[0]
    date_br = date.find_all('br')[0]    
    data['ShortDay'] = date_br.previous_sibling.string
    
    col = day.find_all('div', class_='col')
    try:
      ic = col[1].find_all('span', class_='ic')[0]
      data['Outlook'] = ic['title']
      data['weathercode'] = readCondition(ic)
    except:
      data['Outlook'] = ''
      data['weathercode'] = 'na'
    
    try:
      data['LowTemperature'] = col[0].find_all('span', class_='big')[0].string.split(' ')[0]
    except:
      data['LowTemperature'] = ''
    try:  
      data['HighTemperature'] = col[1].find_all('span', class_='big')[0].string.split(' ')[0]
    except:
      data['HighTemperature'] = ''
    
    try:
      small = col[1].find_all('span', class_='small')[0]
      itag = small.find_all('i')[0]
      data['WindSpeed'] = itag.previous_sibling.string.split(' ')[0]
      
      windDirectionGroundDegree = int(re.findall('\((\d+)deg\)', itag['style'])[0])
      windDirectionGroundDegree = (windDirectionGroundDegree + 225 ) % 360
      
      data['windDirectionGroundDegree'] = windDirectionGroundDegree
      data['WindDirection'] = utilities.winddir(windDirectionGroundDegree)
    except:
      data['WindSpeed'] = ''
      data['windDirectionGroundDegree'] = 16
      data['WindDirection'] = ''
    
    days[i] = data
  
  result['forecast_days'] = days
  
  return result  

def isSimilar(a, b):
    return (SequenceMatcher(None, a, b).ratio() > 0.8)
  
def getCities(key = None):
  
  if key:
    key = key.strip().lower()
  
  result = []
  
  data = json.loads(getURL(METEO_CITIES_URL))
  
  for city in data:
    
    city_id = city['id'].split(':')
    
    if city_id[0] == 'lt.lhms.metis':
      
      city['id'] = city_id[1]
      name = city['name'].split('(')[0].strip().lower()
      
      if not key or isSimilar(key, name):
	result.append(city)    
  
  return result

