#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc, xbmcgui, xbmcaddon

import libmeteo as meteo

ADDON        = xbmcaddon.Addon()
ADDONNAME    = ADDON.getAddonInfo('name')
ADDONID      = ADDON.getAddonInfo('id')

WEATHER_WINDOW = xbmcgui.Window(12600)

def set_property(name, value):
  WEATHER_WINDOW.setProperty(name, str(value))

def refresh_locations():
  
  locations = 0
  for count in range(1, 6):
    
    loc_name = ADDON.getSetting('Location%s' % count)
    if loc_name != '':
      locations += 1
    else:
      ADDON.setSetting('Location%sid' % count, '')
    set_property('Location%s' % count, loc_name)
    
  set_property('Locations', str(locations))
  
def clear():
  
  set_property('Forecast.IsFetched' , '')
  set_property('Current.IsFetched'  , '')
  set_property('Today.IsFetched'    , '')
  set_property('Daily.IsFetched'    , '')
  set_property('Weekend.IsFetched'  , '')
  set_property('36Hour.IsFetched'   , '')
  set_property('Hourly.IsFetched'   , '')
  set_property('Alerts.IsFetched'   , '')
  set_property('Map.IsFetched'      , '')
  set_property('WeatherProvider'    , ADDONNAME)  
  
def forecast(loc, locid):

  data = meteo.getData(locid)

  set_property('Current.Location' , loc)
  set_property('Forecast.City' , data['location'])
  set_property('Forecast.Country' , 'lt')
  set_property('Current.Temperature', data['temperature'])
  set_property('Current.Condition', data['condition'])
  set_property('Current.OutlookIcon', '%s.png' % str(data['weathercode']))
  set_property('Current.ConditionIcon', '%s.png' % data['weathercode'])
  set_property('Current.FeelsLike', data['FeelsLike'])
  set_property('Current.Humidity', data['Humidity'])
  set_property('Current.Wind', data['Wind'])
  set_property('Current.WindDirection', data['WindDirection'])
  set_property('Current.DewPoint', data['DewPoint'])
  set_property('Current.Precipitation', data['Precipitation'])

  for i in range(1,25):
    
    if i in data['forecast_hours']:
      
      hour = data['forecast_hours'][i]
      
      set_property('Hourly.%d.ShortDate' % i, hour['ShortDate'])
      set_property('Hourly.%d.Time' % i, hour['Time'])
      set_property('Hourly.%d.Outlook' % i, hour['Outlook'])
      set_property('Hourly.%d.OutlookIcon' % i, '%s.png' % str(hour['weathercode']))
      set_property('Hourly.%d.FanartCode' % i, hour['weathercode'])
      set_property('Hourly.%d.Temperature' % i, hour['Temperature'])
      set_property('Hourly.%d.FeelsLike' % i, hour['FeelsLike'])
      set_property('Hourly.%d.Humidity' % i, hour['Humidity'])
      set_property('Hourly.%d.Precipitation' % i, hour['Precipitation'])
      set_property('Hourly.%d.WindSpeed' % i, hour['WindSpeed'] + ' km/h')
      set_property('Hourly.%d.WindDirection' % i, hour['WindDirection'])
      
  for i in range(1,15):
    
    if i in data['forecast_days']:
      
      day = data['forecast_days'][i]
      set_property('Daily.%d.ShortDate' % i, day['ShortDate'])
      set_property('Daily.%d.ShortDay' % i, day['ShortDay'])
      set_property('Daily.%d.Outlook' % i, day['Outlook'])
      set_property('Daily.%d.OutlookIcon' % i, '%s.png' % str(day['weathercode']))
      set_property('Daily.%d.FanartCode' % i, day['weathercode'])
      set_property('Daily.%d.LowTemperature' % i, day['LowTemperature'])
      set_property('Daily.%d.HighTemperature' % i, day['HighTemperature'])
      set_property('Daily.%d.WindSpeed' % i, day['WindSpeed'])
      set_property('Daily.%d.WindDirection' % i, day['WindDirection'])

  set_property('Current.IsFetched'  , 'true')
  set_property('Hourly.IsFetched'   , 'true')
  set_property('Daily.IsFetched'    , 'true')
  
if sys.argv[1].startswith('Location'):
  
  keyboard = xbmc.Keyboard('', xbmc.getLocalizedString(14024), False)
  keyboard.doModal()
  
  if (keyboard.isConfirmed() and keyboard.getText() != ''):
    
    text = keyboard.getText()
    
    locations = meteo.getCities(text)
    
    names = []
    
    for location in locations:
      names.append(location['name'])
      
    dialog = xbmcgui.Dialog()
    if names:
      selected = dialog.select(xbmc.getLocalizedString(396), names)
      
      if selected != -1:
	ADDON.setSetting(sys.argv[1], names[selected])
	ADDON.setSetting(sys.argv[1]+'id', locations[selected]['id'])
	
    else:
      dialog.ok(ADDONNAME, xbmc.getLocalizedString(284))
  
else:
  
  clear()
  refresh_locations()
  
  location = ADDON.getSetting('Location%s' % sys.argv[1])
  locationid = ADDON.getSetting('Location%sid' % sys.argv[1])  
  
  if locationid:
    forecast(location, locationid)
    