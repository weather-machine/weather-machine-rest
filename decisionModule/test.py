from decisionModule.rest import get_place_by_name, get_place_by_all_data, get_place_id, get_place_by_coordinates, \
    is_acceptable_distance, get_all_forecasts_for, get_actual_weather, get_all_actual_weathers, get_dir_by_id, \
    get_type_by_id, WeatherAnswer, change_to_json, change_record_to_weather_answer
from datetime import datetime

# print(is_acceptable_distance(51.10001, 51.10001-0.004, 'latitude'))
# print(is_acceptable_distance(51.10001, 51.10001+0.004, 'latitude'))
# print(is_acceptable_distance(51.10001-0.004, 51.10001, 'latitude'))
# print(is_acceptable_distance(51.10001+0.004, 51.10001, 'latitude'))
#
# print(is_acceptable_distance(17.038538, 17.038538-0.09, 'longitude'))
# print(is_acceptable_distance(17.038538, 17.038538+0.09, 'longitude'))
# print(is_acceptable_distance(17.038538-0.09, 17.038538, 'longitude'))
# print(is_acceptable_distance(17.038538+0.09, 17.038538, 'longitude'))
#
#
# # test get_place_id
latitude = 51.107883
longitude = 17.038538
name = 'Wroclaw'
country = 'Poland'
# print(get_place_by_coordinates(latitude, longitude))  # 5
# print(get_place_by_name(name, country))  # 1
# print(get_place_by_all_data(latitude, longitude, name, country))  # 5
# # 5 - Wroclaw:
# print(get_place_id(latitude, longitude, name, country))
# print(get_place_id(latitude, longitude, name, None))
# print(get_place_id(latitude, longitude, None, None))
# # 1 - Wroclaw:
# print(get_place_id(51.1, 17.03333, name, country))
# print(get_place_id(51.1, 17.03333, name, None))
# print(get_place_id(51.1, 17.03333, None, None))
# # nie ma w bazie takiego punktu, ale jest name, country
# # znajduje się w dopuszczalnym przedziale, więc powinien zwrócić 1:
# print("Powinno byc 1 i jest: " + str(get_place_id(51.10001, 17.03333, name, country)))
# print("Powinno byc 1 i jest: " + str(get_place_id(51.10001, 17.03933, name, country)))
# print("Powinno byc 5 i jest: " + str(get_place_id(latitude-0.004, longitude-0.09, name, country)))
# #
# print("Powinno byc dodac nowy, wiec id== " + str(get_place_id(latitude+0.0004, longitude+0.009, name, country)))


#
# TEST get_all_forecasts_for
result = get_all_forecasts_for(1)
print(len(result))
# for i in result:
#     print(i.PlaceId)


# TEST get_actual_weather
result = get_all_actual_weathers(1, 1546012049000)
print(len(result))

actual_weather = get_actual_weather(1)
print(str(actual_weather.Id) + " " + str(actual_weather.Temperature))


# TEST get_forecasts_for_place
id_place = get_place_id(latitude=latitude, longitude=longitude, name=name, country=country)
print(id_place)
all_forecasts = get_all_forecasts_for(id_place=id_place)
print(len(all_forecasts))

# # TEST change_record_to_weather_answer
# answer = []
# list = []
# e = change_record_to_weather_answer(result[0])
# print(e)
# print(change_record_to_weather_answer(result[1]))
# print(change_record_to_weather_answer(result[2]))
# print(e.__dict__)
# list.append(e)
# list.append(e)
# print(change_to_json(list))
actual_date = actual_weather.Date/1000
print(actual_date)
date_utc = datetime.utcfromtimestamp(actual_date)
print(date_utc)

date_set = set()
for i in all_forecasts:
    date_set.add(i.Date)
print(len(date_set))
date_set = sorted(date_set)
for i in date_set:
    print(datetime.fromtimestamp(i/1000))


# TEST
def select_our_weather_forecast(actual_date, all_forecasts):
    result = []
    return result



# timestamps
#
# ts = int("1546012049000")/1000
#
# # if you encounter a "year is out of range" error the timestamp
# # may be in milliseconds, try `ts /= 1000` in that case
# print(datetime.utcfromtimestamp(ts))