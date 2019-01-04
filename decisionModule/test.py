from decisionModule.rest import get_place_by_name, get_place_by_all_data, get_place_id, get_place_by_coordinates, \
    is_acceptable_distance, get_all_forecasts_for, get_actual_weather, get_all_actual_weathers


print(is_acceptable_distance(51.10001, 51.10001-0.004, 'latitude'))
print(is_acceptable_distance(51.10001, 51.10001+0.004, 'latitude'))
print(is_acceptable_distance(51.10001-0.004, 51.10001, 'latitude'))
print(is_acceptable_distance(51.10001+0.004, 51.10001, 'latitude'))

print(is_acceptable_distance(17.038538, 17.038538-0.09, 'longitude'))
print(is_acceptable_distance(17.038538, 17.038538+0.09, 'longitude'))
print(is_acceptable_distance(17.038538-0.09, 17.038538, 'longitude'))
print(is_acceptable_distance(17.038538+0.09, 17.038538, 'longitude'))


# test get_place_id
latitude = 51.107883
longitude = 17.038538
name = 'Wroclaw'
country = 'Poland'
print(get_place_by_coordinates(latitude, longitude))  # 5
print(get_place_by_name(name, country))  # 1
print(get_place_by_all_data(latitude, longitude, name, country))  # 5
# 5 - Wroclaw:
print(get_place_id(latitude, longitude, name, country))
print(get_place_id(latitude, longitude, name, None))
print(get_place_id(latitude, longitude, None, None))
# 1 - Wroclaw:
print(get_place_id(51.1, 17.03333, name, country))
print(get_place_id(51.1, 17.03333, name, None))
print(get_place_id(51.1, 17.03333, None, None))
# nie ma w bazie takiego punktu, ale jest name, country
# znajduje się w dopuszczalnym przedziale, więc powinien zwrócić 1:
print("Powinno byc 1 i jest: " + str(get_place_id(51.10001, 17.03333, name, country)))
print("Powinno byc 1 i jest: " + str(get_place_id(51.10001, 17.03933, name, country)))
print("Powinno byc 5 i jest: " + str(get_place_id(latitude-0.004, longitude-0.09, name, country)))
#
print("Powinno byc dodac nowy, wiec id== " + str(get_place_id(latitude+0.0004, longitude+0.009, name, country)))


#
# TEST get_all_forecasts_for
result = get_all_forecasts_for(1)
print(len(result))
# for i in result:
#     print(i.PlaceId)


# TEST get_actual_weather
result = get_all_actual_weathers(1, 1546012049000)
print(len(result))

result = get_actual_weather(1)
print(result)



latitude = 51.1
longitude = 17.03333
name = 'Wroclaw'
country = 'Poland'
id = get_place_id(latitude=latitude, longitude=longitude, name=name, country=country)
print(id)
result = get_all_forecasts_for(id_place=id)
print(len(result))