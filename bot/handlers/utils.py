from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from aiogram.types import Message
from json import loads


nomin = Nominatim(user_agent='user')


changed_data = {
    'ФИО': 'full_name',
    'Телефон': 'number',
    'Баланс': 'balance'
}


orders_data = {
    'В ожидании': 'WAITING',
    'Выполнено': 'COMPLETED',
    'В процессе': 'PROCESSING'
}


def get_key(value):
    for k, v in orders_data.items():
        if v == value:
            return k


def current_user_location(location: Message):
    if not location.text and loads(str(location.as_json()))['location']:
        loc_data = loads(str(location.as_json()))['location']
        latitude = loc_data.get('latitude')
        longitude = loc_data.get('longitude')

        return nomin.reverse(f'{latitude} {longitude}'), latitude, longitude
    else:
        location = nomin.geocode(location.text)
        if not location:
            return False
        return location, location.latitude, location.longitude


def distance_btw_two_points(current_point, order_point):
    distance = geodesic(current_point, order_point)

    return distance
