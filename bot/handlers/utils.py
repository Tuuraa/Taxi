from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from json import loads


changed_data = {
    'ФИО': 'full_name',
    'Телефон': 'number',
    'Баланс': 'balance'
}


def current_user_location(location):
    loc_data = loads(str(location.as_json()))['location']
    latitude = loc_data.get('latitude')
    longitude = loc_data.get('longitude')

    nomin = Nominatim(user_agent='user')

    return nomin.reverse(f'{latitude} {longitude}'), latitude, longitude


def distance_btw_two_points(current_point, order_point):
    distance = geodesic(current_point, order_point)

    return distance
