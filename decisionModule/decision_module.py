from __future__ import division

from flask import Flask, request
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, inspect
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from datetime import datetime

import simplejson as json
import numpy as np
import operator

import credentials as cred


app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = cred.USER
app.config['MYSQL_DATABASE_PASSWORD'] = cred.PASSWORD
app.config['MYSQL_DATABASE_DB'] = cred.DB
app.config['MYSQL_DATABASE_HOST'] = cred.HOST
engine = create_engine(cred.ENGINE, pool_size=5000)
cors = CORS(app)

db = SQLAlchemy(app)
Base = automap_base()


# model:
class WindDirection(Base):
    __tablename__ = 'Wind_Direction'
    __table_args__ = {'extend_existing': True}

    Id = Column(Integer, primary_key=True, autoincrement=True)
    Direction = Column(String)

    def __init__(self, id_dir, direction):
        self.Id = id_dir
        self.Direction = direction

    def __str__(self):
        return self.Direction

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Place(Base):
    __tablename__ = 'Place'
    __table_args__ = {'extend_existing': True}

    Id = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String)
    Latitude = Column(Integer)
    Longitude = Column(Integer)
    Country = Column(String)

    def __init__(self, id_place, name, latitude, longitude, country):
        self.Id = id_place
        self.Name = name
        self.Latitude = latitude
        self.Longitude = longitude
        self.Country = country

    def __init__(self, name, latitude, longitude, country):
        self.Name = name
        self.Latitude = latitude
        self.Longitude = longitude
        self.Country = country

    def __str__(self):
        return self.Id.__str__() + " - " + self.Name

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class WeatherType(Base):
    __tablename__ = 'Weather_Type'
    __table_args__ = {'extend_existing': True}

    Id = Column(Integer, primary_key=True, autoincrement=True)
    Main = Column(String)
    Description = Column(String)

    def __init__(self, main, description):
        self.Main = main
        self.Description = description

    def __init__(self, id_type, main, description):
        self.Id = id_type
        self.Main = main
        self.Description = description

    def __str__(self):
        return self.Id.__str__() + " - " + self.Main

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class WeatherForecast(Base):
    __tablename__ = 'Weather_Forecast'
    __table_args__ = {'extend_existing': True}

    Id = Column(Integer, primary_key=True, autoincrement=True)
    PlaceId = Column(ForeignKey('Place.Id'))
    Weather_TypeId = Column(ForeignKey('Weather_Type.Id'))
    Wind_DirId = Column(ForeignKey('Wind_Direction.Id'))
    Date = Column(BIGINT)
    Temperature = Column(Integer)
    Temperature_Max = Column(Integer)
    Temperature_Min = Column(Integer)
    Cloud_cover = Column(Integer)
    Humidity_percent = Column(Integer)
    Pressure_mb = Column(Integer)
    Wind_speed = Column(Integer)
    IsForecast = Column(Integer)

    def __init__(self, place_id, weather_type_id, wind_dir_id, date, temperature_max, temperature_min, temperature,
                 cloud_cover, humidity_percent, pressure_mb, wind_speed, is_forecast):
        self.PlaceId = place_id
        self.Weather_TypeId = weather_type_id
        self.Wind_DirId = wind_dir_id
        self.Date = date
        self.Temperature_Max = temperature_max
        self.Temperature_Min = temperature_min
        self.Temperature = temperature
        self.Cloud_cover = cloud_cover
        self.Humidity_percent = humidity_percent
        self.Pressure_mb = pressure_mb
        self.Wind_speed = wind_speed
        self.IsForecast = is_forecast

    def __str__(self):
        return self.Id.__str__() + " - " + str(self.PlaceId) + str(self.Weather_TypeId) + str(self.Wind_DirId) + \
               str(self.Date) + str(self.Temperature)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class WeatherAnswer:
    def __init__(self, place_id, name, latitude, longitude, country, wind_dir_id, direction, main, description, date,
                 temperature_max, temperature_min, temperature, cloud_cover, humidity_percent, pressure_mb,
                 wind_speed, is_forecast):
        self.PlaceId = place_id
        self.Name = name
        self.Latitude = latitude
        self.Logitude = longitude
        self.Country = country
        self.Wind_DirId = wind_dir_id
        self.Direction = direction
        self.Main = main
        self.Description = description
        self.Date = date
        self.Temperature_Max = temperature_max
        self.Temperature_Min = temperature_min
        self.Temperature = temperature
        self.Cloud_cover = cloud_cover
        self.Humidity_percent = humidity_percent
        self.Pressure_mb = pressure_mb
        self.Wind_speed = wind_speed
        self.IsForecast = is_forecast

    def __str__(self):
        return "Place " + self.Name.__str__() + " - " + str(self.Main) + " " + str(self.Temperature) + " " + \
               str(self.Date) + " " + str(self.Wind_speed) + " " + str(self.Direction)

    def as_dict(self):
        return self.__dict__


Base.prepare(engine, reflect=True)  # deklaracja klas koniecznie przed ta linijka
inspector = inspect(engine)
conn = engine.connect()
print("Polaczenie nawiazane")


@app.route('/forecastForPlace', methods=['GET', 'POST'])
@cross_origin()
def get_forecasts_for_place():
    data = request.get_json()
    latitude = data["Latitude"]
    longitude = data["Longitude"]
    name = data["Name"]
    country = data["Country"]
    id_place, added = get_place_id(latitude=latitude, longitude=longitude, name=name, country=country)
    # TO TEST:
    # latitude = 51.107883
    # longitude = 17.038538
    # name = 'Wroclaw'
    # country = 'Poland'
    # actual_time = '1546013126000'
    # id_place, added = get_place_id(latitude=latitude, longitude=longitude, name=name, country=country)
    # END TO TEST
    if added:
        return json.dumps({'status': 'place added'}), 200, {'ContentType': 'application/json'}
    all_forecasts = get_all_forecasts_for(id_place=id_place)
    actual_time = datetime.utcnow().timestamp()
    actual_time = "%.0f" % actual_time
    actual_time = actual_time + "000"
    actual_time = int(actual_time)
    actual_weather = get_actual_weather(id_place, actual_time)
    done_forecast = decide(actual_weather, all_forecasts, actual_time, id_place)

    result = change_all_record_to_wa(done_forecast, id_place, name, latitude, longitude, country)
    return change_to_json(result), 200, {'ContentType': 'application/json'}


# DECISION MODULE:
def create_one_forecast(list_of_forecasts, date):
    weather_type_id = []
    wind_dir_id = []
    date = date
    temperature = []
    temperature_max = []
    temperature_min = []
    cloud_cover = []
    humidity_percent = []
    pressure_mb = []
    wind_speed = []
    is_forecast = 1
    for i in list_of_forecasts:
        weather_type_id.append(i.Weather_TypeId)
        wind_dir_id.append(i.Wind_DirId)
        temperature.append(i.Temperature)
        temperature_max.append(i.Temperature_Max)
        temperature_min.append(i.Temperature_Min)
        cloud_cover.append(i.Cloud_cover)
        humidity_percent.append(i.Humidity_percent)
        pressure_mb.append(i.Pressure_mb)
        wind_speed.append(i.Wind_speed)
    weather_type_id = get_most_common(remove_index(weather_type_id, 1))
    wind_dir_id = get_most_common(wind_dir_id)
    temperature = list(filter(None.__ne__, temperature))
    if not temperature:
        temperature = None
    else:
        temperature = np.mean(temperature)
    temperature_max = list(filter(None.__ne__, temperature_max))
    if not temperature_max:
        temperature_max = None
    else:
        temperature_max = np.mean(temperature_max)
    temperature_min = list(filter(None.__ne__, temperature_min))
    if not temperature_min:
        temperature_min = None
    else:
        temperature_min = np.mean(temperature_min)
    cloud_cover = list(filter(None.__ne__, cloud_cover))
    if not cloud_cover:
        cloud_cover = None
    else:
        cloud_cover = np.mean(cloud_cover)
    humidity_percent = list(filter(None.__ne__, humidity_percent))
    humidity_percent = np.mean(humidity_percent)
    pressure_mb = list(filter(None.__ne__, pressure_mb))
    if not cloud_cover:
        pressure_mb = None
    else:
        pressure_mb = np.mean(pressure_mb)
    wind_speed = list(filter(None.__ne__, wind_speed))
    wind_speed = np.mean(wind_speed)
    return WeatherForecast(0, weather_type_id, wind_dir_id, date, temperature_max, temperature_min, temperature,
                           cloud_cover, humidity_percent, pressure_mb, wind_speed, is_forecast)


def get_night_forecast(forecasts):
    result = forecasts[0]
    for i in forecasts:
        if i.Temperature < result.Temperature:
            result = i
    return result


def filter_result_to_format(forecasts):
    if len(forecasts) <= 25:
        return forecasts
    else:
        hours_forecasts = []
        current_date_day = datetime.fromtimestamp(forecasts[0].Date/1000).day
        first_day = []
        second_day = []
        third_day = []
        fourth_day = []
        fifth_day = []
        for i in range(0, 25):
            hours_forecasts.append(forecasts[i])
            if datetime.fromtimestamp(forecasts[i].Date/1000).day != current_date_day:
                first_day.append(forecasts[i])
        temp = 50-len(first_day)
        if len(forecasts) >= temp:
            for i in range(26, temp):
                first_day.append(forecasts[i])
            temp = temp + 1

            # 2 day
            if len(forecasts) >= temp + 24:
                for i in range(temp, temp + 24):
                    second_day.append(forecasts[i])
                temp = temp + 25

                # 3 day
                if len(forecasts) >= temp + 24:
                    for i in range(temp, temp + 24):
                        third_day.append(forecasts[i])
                    temp = temp + 25

                    # 4 day
                    if len(forecasts) >= temp + 24:
                        for i in range(temp, temp + 24):
                            fourth_day.append(forecasts[i])
                        temp = temp + 25

                        # 5 day
                        if len(forecasts) >= temp + 24:
                            for i in range(temp, temp + 24):
                                fifth_day.append(forecasts[i])
                        else:
                            for i in range(temp, len(forecasts)):
                                fifth_day.append(forecasts[i])
                    else:
                        for i in range(temp, len(forecasts)):
                            fourth_day.append(forecasts[i])
                else:
                    for i in range(temp, len(forecasts)):
                        third_day.append(forecasts[i])
            else:
                for i in range(temp, len(forecasts)):
                    second_day.append(forecasts[i])
        else:
            for i in range(25, len(forecasts)):
                first_day.append(forecasts[i])
        if len(first_day) > 0:
            hours_forecasts.append(get_night_forecast(first_day))
            print(datetime.utcfromtimestamp(get_night_forecast(first_day).Date/1000))
            hours_forecasts.append(create_one_forecast(first_day, first_day[0].Date))
        if len(second_day) > 0:
            hours_forecasts.append(create_one_forecast(second_day, second_day[0].Date))
        if len(third_day) > 0:
            hours_forecasts.append(create_one_forecast(third_day, third_day[0].Date))
        if len(fourth_day) > 0:
            hours_forecasts.append(create_one_forecast(fourth_day, fourth_day[0].Date))
        if len(fifth_day) > 0:
            hours_forecasts.append(create_one_forecast(fifth_day, fifth_day[0].Date))
        print(len(hours_forecasts))
        return hours_forecasts


# RETURNS LIST OF FORECAST FOR PLACE
def decide(actual_weather, all_forecasts, actual_time, id_place):
    if actual_weather is None:
        the_most_actual = get_the_most_actual_weather(id_place)
        if the_most_actual is None:
            done_forecast = []
        else:
            done_forecast = [the_most_actual]
    else:
        # first forecast - actual weather
        done_forecast = [actual_weather]
    # creating set of date >= actual
    date_set = set()
    for elem in all_forecasts:
        if actual_time <= elem.Date:
            date_set.add(elem.Date)
    date_set = sorted(date_set)
    # creating one forecast for datetime
    for x in date_set:
        forecast = get_all_forecast_for_timestamp(x, all_forecasts)
        result = create_one_forecast(forecast, x)
        done_forecast.append(result)
    done_forecast = filter_result_to_format(done_forecast)
    return done_forecast


# DB:
def insert_place(name, latitude, longitude, country):
    session = Session(engine)
    place = Place(name, latitude, longitude, country)
    session.add(place)
    session.commit()
    id_place = place.Id
    session.close()
    return id_place


def get_type_by_id(id_type):
    session = Session(engine)
    session.close()
    # for result in session.query(WeatherType).filter_by(Id=id_type):
    #     return result
    return session.query(WeatherType).filter_by(Id=id_type).first()


def get_dir_by_id(id_wind):
    session = Session(engine)
    session.close()
    # for result in session.query(WindDirection).filter_by(Id=id_wind):
    #     return result
    return session.query(WindDirection).filter_by(Id=id_wind).first()


def get_type_from_enum_list(id_type):
    if id_type is None:
        return None
    else:
        id_type = int(id_type)
    all_types = [
        (1, 'unknown'),
        (2, 'Pogodnie'),
        (3, 'Bezchmurnie'),
        (4, 'Przewaznie pogodnie'),
        (5, 'Przewaznie bezchmurnie'),
        (6, 'Zamglone slonce'),
        (7, 'Mgla'),
        (8, 'Przelotne zachmurzenie'),
        (9, 'Przewaga slonca nad chmurami'),
        (10, 'Rozproszone chmury'),
        (11, 'Polowiczne zachmurzenie'),
        (12, 'Slonce i chmury'),
        (13, 'Wysokie chmury'),
        (14, 'Przewaga chmur nad sloncem'),
        (15, 'Polowicznie slonecznie'),
        (16, 'Rozbite chmury'),
        (17, 'Przewaznie pochmurno'),
        (18, 'Chmury'),
        (19, 'Pochmurno'),
        (20, 'Niskie chmury'),
        (21, 'Lekka mgla'),
        (22, 'Mgla'),
        (23, 'Gesta mgla'),
        (24, 'Mgla lodowa'),
        (25, 'Burza piaskowa'),
        (26, 'Burza pylu'),
        (27, 'Zwiekaszajace sie zachmurzenie'),
        (28, 'Zmniejszajace sie zachmurzenie'),
        (29, 'Rozpogodzenie'),
        (30, 'Przeswity slonca'),
        (31, 'Wczesna mgla, po ktorej nastepuje rozpogodzenie'),
        (32, 'Popoludniowe zachmurzenie'),
        (33, 'Poranne zachmurzenie'),
        (34, 'Upalnie'),
        (35, 'Niski poziom zamglenia'),
        (36, 'Wysokie chmury'),
        (37, 'Jasno'),
        (38, 'Przemijajace chmury'),
        (39, 'Wiecej slonca niz chmur'),
        (40, 'Wiecej chmur niz slonca'),
        (41, 'Przewaznie jasno')
    ]
    for number, value in all_types:
        if number == id_type:
            return WeatherType(number, value, 'unknown')
    return None


def get_dir_from_enum_list(id_dir):
    if id_dir is None:
        return None
    else:
        id_dir = int(id_dir)
    all_directions = [(1, 'N'),
                      (2, 'NNE'),
                      (3, 'NE'),
                      (4, 'ENE'),
                      (5, 'E'),
                      (6, 'ESE'),
                      (7, 'SE'),
                      (8, 'SSE'),
                      (9, 'S'),
                      (10, 'SSW'),
                      (11, 'SW'),
                      (12, 'WSW'),
                      (13, 'W'),
                      (14, 'WNW'),
                      (15, 'NW'),
                      (16, 'NNW')]
    for number, value in all_directions:
        if number == id_dir:
            return WindDirection(number, value)
    return None


# get PLACE --3 versions
def get_place_by_coordinates(latitude, longitude):
    session = Session(engine)
    session.close()
    for result in session.query(Place).filter_by(Latitude=latitude, Longitude=longitude):
        return result


def get_place_by_name(name, country):
    session = Session(engine)
    session.close()
    for result in session.query(Place).filter_by(Name=name, Country=country):
        return result


def get_place_by_all_data(latitude, longitude, name, country):
    session = Session(engine)
    session.close()
    for result in session.query(Place).filter_by(Latitude=latitude, Longitude=longitude, Name=name, Country=country):
        return result


def get_all_forecasts_for(id_place):
    session = Session(engine)
    session.close()
    result = []
    for wf in session.query(WeatherForecast).filter_by(PlaceId=id_place, IsForecast=1):
        result.append(wf)
    return result


def get_actual_weather(id_place, actual_time):
    all_weathers = get_all_actual_weathers(id_place, actual_time)
    not_null_weathers = []
    if len(all_weathers) > 0:
        for weather in all_weathers:
            if (weather.Weather_TypeId is not None) & (weather.Wind_DirId is not None) & \
                    (weather.Temperature is not None):
                not_null_weathers.append(weather)
    if len(not_null_weathers) > 0:
        return not_null_weathers[0]
    else:
        return None


def get_all_actual_weathers(id_place, date):
    session = Session(engine)
    session.close()
    result = []
    for wf in session.query(WeatherForecast).filter_by(PlaceId=id_place, Date=date, IsForecast=0):
        result.append(wf)
    return result


def get_the_most_actual_weather(id_place):
    session = Session(engine)
    session.close()
    result = []
    for wf in session.query(WeatherForecast).filter_by(PlaceId=id_place, IsForecast=0):
        result.append(wf)
    if len(result) > 0:
        sorted_x = sorted(result, key=operator.attrgetter('Date'))
        return sorted_x[len(sorted_x)-1]
    else:
        return None


# official - TO USE:
def get_place_id(latitude, longitude, name, country):
    place = get_place_by_all_data(latitude, longitude, name, country)
    if place is not None:
        return place.Id, False
    place = get_place_by_coordinates(latitude, longitude)
    if place is not None:
        return place.Id, False
    place = get_place_by_name(name, country)
    if place is not None:
        lat_dist = is_acceptable_distance(latitude, place.Latitude, 'latitude')
        long_dist = is_acceptable_distance(longitude, place.Longitude, 'longitude')
        if lat_dist & long_dist:
            return place.Id, False
        else:
            return insert_place(name, latitude, longitude, country), True
    else:
        return insert_place(name, latitude, longitude, country), True


# UTILS:
def format_number(number):
    if number is None:
        return None
    else:
        result = "%.1f" % number
        return float(result)


def change_to_json(values):
    dict_list = change_to_dict(values)
    return json.dumps(dict_list)


def change_to_dict(table_result):
    result = []
    for t in table_result:
        result.append(t.as_dict())
    return result


def remove_index(lst, index):
    results = []
    for i in lst:
        if i != index:
            results.append(i)
    return results


def get_most_common(lst):
    if len(lst) == 0:
        return 1
    else:
        return max(set(lst), key=lst.count)


def is_acceptable_distance(first, second, param):
    if (first is None) | (second is None):
        return False
    diff = abs(first - second)
    if (param == 'latitude') & (diff < 0.005):
        return True
    if (param == 'longitude') & (diff < 0.1):
        return True
    return False


# DB UTILS:
def change_all_record_to_wa(records, id_place, name, latitude, longitude, country):
    result = []
    for forecast in records:
        result.append(change_record_to_weather_answer(id_place, name, latitude, longitude, country, forecast))
    return result


def change_record_to_weather_answer(id_place, name, latitude, longitude, country, forecast):
    weather_type = get_type_from_enum_list(forecast.Weather_TypeId)
    if weather_type is None:
        weather_type = get_type_by_id(forecast.Weather_TypeId)
    wind_dir = get_dir_from_enum_list(forecast.Wind_DirId)
    if wind_dir is None:
        wind_dir = get_dir_by_id(forecast.Wind_DirId)
    if weather_type is None:
        weather_type_main = None
        weather_type_description = None
    else:
        weather_type_main = weather_type.Main
        weather_type_description = weather_type.Description
    if wind_dir is None:
        wind_dir_id = None
        wind_dir_direction = None
    else:
        wind_dir_id = wind_dir.Id
        wind_dir_direction = wind_dir.Direction

    answer = WeatherAnswer(id_place, name, latitude, longitude, country, wind_dir_id, wind_dir_direction,
                           weather_type_main, weather_type_description, forecast.Date,
                           format_number(forecast.Temperature_Max), format_number(forecast.Temperature_Min),
                           format_number(forecast.Temperature), format_number(forecast.Cloud_cover),
                           format_number(forecast.Humidity_percent), format_number(forecast.Pressure_mb),
                           format_number(forecast.Wind_speed), forecast.IsForecast)
    return answer


def get_all_forecast_for_timestamp(timestamp, all_forecasts):
    result = []
    for forecast in all_forecasts:
        if forecast.Date == timestamp:
            result.append(forecast)
    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1400, debug=True)
