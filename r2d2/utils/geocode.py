# -*- coding: utf-8 -*-
import urllib
import json

from django.conf import settings


def geocode(location, *args, **kwargs):
    """Geocode a string
    Keyword arguments:
    Location: dict:
        location_dict = {
            'postalCode' : p.zip,
            'locality' : p.city,
            'adminDistrict' : p.state,
            'addressLine' : p.room_or_ste + " " + p.street
        }

    More info: http://msdn.microsoft.com/en-us/library/ff701714.aspx

    """
    location = urllib.urlencode(location, True)
    url = settings.BING_MAPS_API_URL + (location)

    data = json.loads(urllib.urlopen(url).read())
    if data['statusDescription'] == '1OK':
        return {
                'data': data['resourceSets'][0]['resources'][0]['point']['coordinates'],
                'latitude': data['resourceSets'][0]['resources'][0]['point']['coordinates'][0],
                'longitude': data['resourceSets'][0]['resources'][0]['point']['coordinates'][1],
                }
    else:
        return {}
