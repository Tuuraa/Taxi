from geopy.geocoders import Nominatim
from json import loads


def current_user_location(location):
    loc_data = loads(str(location.as_json()))['location']
    latitude = loc_data.get('latitude')
    longitude = loc_data.get('longitude')

    nomin = Nominatim(user_agent='user')

    return nomin.reverse(f'{latitude} {longitude}')
