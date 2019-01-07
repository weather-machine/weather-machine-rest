from __future__ import division

from flask import Flask, request
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, inspect
from sqlalchemy.dialects.mysql import BIGINT, DOUBLE
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from datetime import datetime

import simplejson as json
import time
import numpy as np
import decisionModule.credentials as cred


app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = cred.USER
app.config['MYSQL_DATABASE_PASSWORD'] = cred.PASSWORD
app.config['MYSQL_DATABASE_DB'] = cred.DB
app.config['MYSQL_DATABASE_HOST'] = cred.HOST
engine = create_engine(cred.ENGINE, pool_size=5000)
cors = CORS(app)

db = SQLAlchemy(app)
Base = automap_base()


class WindDirection(Base):
    __tablename__ = 'Wind_Direction'
    __table_args__ = {'extend_existing': True}

    Id = Column(Integer, primary_key=True, autoincrement=True)
    Direction = Column(String)

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

    def __init__(self, Id, Name, Latitude, Longitude, Country):
        self.Id = Id
        self.Name = Name
        self.Latitude = Latitude
        self.Longitude = Longitude
        self.Country = Country

    def __init__(self, Name, Latitude, Longitude, Country):
        self.Name = Name
        self.Latitude = Latitude
        self.Longitude = Longitude
        self.Country = Country

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

    def __init__(self, PlaceId, Weather_TypeId, Wind_DirId, Date, Temperature_Max, Temperature_Min, Temperature,
                 Cloud_cover, Humidity_percent, Pressure_mb, Wind_speed, IsForecast):
        self.PlaceId = PlaceId
        self.Weather_TypeId = Weather_TypeId
        self.Wind_DirId = Wind_DirId
        self.Date = Date
        self.Temperature_Max = Temperature_Max
        self.Temperature_Min = Temperature_Min
        self.Temperature = Temperature
        self.Cloud_cover = Cloud_cover
        self.Humidity_percent = Humidity_percent
        self.Pressure_mb = Pressure_mb
        self.Wind_speed = Wind_speed
        self.IsForecast = IsForecast

    def __str__(self):
        return self.Id.__str__() + " - " + str(self.PlaceId) + str(self.Weather_TypeId) + str(self.Wind_DirId) + \
               str(self.Date) + str(self.Temperature)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class WeatherAnswer:

    def __init__(self, PlaceId, Name, Latitude, Longitude, Country, Wind_DirId, Direction, Main, Description, Date,
                 Temperature_Max, Temperature_Min, Temperature, Cloud_cover, Humidity_percent, Pressure_mb,
                 Wind_speed, IsForecast):
        self.PlaceId = PlaceId
        self.Name = Name
        self.Latitude = Latitude
        self.Logitude = Longitude
        self.Country = Country
        self.Wind_DirId = Wind_DirId
        self.Direction = Direction
        self.Main = Main
        self.Description = Description
        self.Date = Date
        self.Temperature_Max = Temperature_Max
        self.Temperature_Min = Temperature_Min
        self.Temperature = Temperature
        self.Cloud_cover = Cloud_cover
        self.Humidity_percent = Humidity_percent
        self.Pressure_mb = Pressure_mb
        self.Wind_speed = Wind_speed
        self.IsForecast = IsForecast

    def __str__(self):
        return "Place " + self.Name.__str__() + " - " + str(self.Main) + " " + str(self.Temperature) + " " + \
               str(self.Date) + " " + str(self.Wind_speed) + " " + str(self.Direction)

    def as_dict(self):
        return self.__dict__


Base.prepare(engine, reflect=True) # deklaracja klas koniecznie przed ta linijka
inspector = inspect(engine)
conn = engine.connect()
print("Polaczenie nawiazane")


@app.route('/directions', methods=['GET'])
@cross_origin()
def get_current_dir():
    result = get_all(WindDirection)
    return change_to_json(result)


@app.route('/places', methods=['GET'])
@cross_origin()
def get_places():
    result = get_all(Place)
    return change_to_json(result)


@app.route('/forecasts', methods=['GET'])
@cross_origin()
def get_forecasts():
    result = get_all(WeatherForecast)
    return change_to_json(result)


@app.route('/types', methods=['GET'])
@cross_origin()
def get_types():
    result = get_all(WeatherType)
    return change_to_json(result)


@app.route('/place', methods=['POST'])
@cross_origin()
def post_place():
    data = request.get_json()
    insert_place(data["Name"], data["Latitude"], data["Longitude"], data["Country"])
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


@app.route('/forecast', methods=['POST'])
@cross_origin()
def post_forecast():
    data = request.get_json()
    wt_id = get_type_or_calculate(data["Main"], data["Desc"])
    insert_forecast(data["PlaceId"], wt_id, data["Wind_DirId"], data["Date"], data["Temperature"],
                    data["Temperature_Max"], data["Temperature_Min"], data["Cloud_cover"], data["Humidity_percent"],
                    data["Pressure_mb"], data["Wind_speed"], data["IsForecast"])
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


@app.route('/forecastForPlace', methods=['GET'])
@cross_origin()
def get_forecasts_for_place():
    # data = request.get_json()
    # id_place = get_place_id(latitude=data["Latitude"], longitude=data["Longitude"], name=data["Name"], country=data["Country"])
    #TO TEST:
    latitude = 51.107883
    longitude = 17.038538
    name = 'Wroclaw'
    country = 'Poland'
    id_place = get_place_id(latitude=latitude, longitude=longitude, name=name, country=country)
    # END TO TEST
    all_forecasts = get_all_forecasts_for(id_place=id_place)
    actual_weather = get_actual_weather(id_place)
    done_forecast = decide(actual_weather, all_forecasts)

    result = change_all_record_to_wa(done_forecast, id_place, name, latitude, longitude, country)
    return change_to_json(result), 200, {'ContentType':'application/json'}


# UTILS:
def get_most_common(list):
    return max(set(list), key=list.count)


def get_all(class_name):
    session = Session(engine)
    result = session.query(class_name).all()
    session.close()
    return result


def change_to_json(values):
    dict = change_to_dict(values)
    return json.dumps(dict)


def change_to_dict(table_result):
    result = []
    for t in table_result:
        result.append(t.as_dict())
    return result


def get_type_or_calculate(main, desc):
    id_wt = get_type(main, desc)
    if id_wt is None:
        id_wt = insert_type(main, desc)
    return id_wt


def change_all_record_to_wa(records, id_place, name, latitude, longitude, country):
    result = []
    for forecast in records:
        result.append(change_record_to_weather_answer(id_place, name, latitude, longitude, country, forecast))
    return result


def change_record_to_weather_answer(id_place, name, latitude, longitude, country, forecast):
    weather_type = get_type_by_id(forecast.Weather_TypeId)
    wind_dir = get_dir_by_id(forecast.Wind_DirId)
    answer = WeatherAnswer(id_place, name, latitude, longitude, country, wind_dir.Id, wind_dir.Direction,
                           weather_type.Main, weather_type.Description, forecast.Date, forecast.Temperature_Max,
                           forecast.Temperature_Min, forecast.Temperature, forecast.Cloud_cover,
                           forecast.Humidity_percent, forecast.Pressure_mb, forecast.Wind_speed, forecast.IsForecast)
    return answer


def get_all_forecast_for_timestamp(timestamp, all_forecasts):
    result = []
    for forecast in all_forecasts:
        if forecast.Date == timestamp:
            result.append(forecast)
    return result


# DATABASE OPERATIONS:
def insert_place(name, latitude, longitude, country):
    session = Session(engine)
    place = Place(name, latitude, longitude, country)
    session.add(place)
    session.commit()
    id = place.Id
    session.close()
    return id


def insert_type(main, desc):
    session = Session(engine)
    type = WeatherType(main, desc)
    session.add(type)
    session.commit()
    id = type.Id
    session.close()
    return id


def insert_forecast(place_id, weather_type_id, wind_dir_id, date, temperature, temperature_max, temperature_min,
                    cloud_cover, humidity_percent, pressure, wind_speed, is_forecast):
    session = Session(engine)
    session.add(WeatherForecast(place_id, weather_type_id, wind_dir_id, date, temperature_max, temperature_min,
                                temperature, cloud_cover, humidity_percent, pressure, wind_speed, is_forecast))
    session.commit()
    session.close()


def get_type(main, desc):
    session = Session(engine)
    session.close()
    for wt in session.query(WeatherType).filter_by(Main=main, Description=desc):
        return wt.Id


def get_type_by_id(id):
    session = Session(engine)
    session.close()
    return session.query(WeatherType).filter_by(Id=id).first()


def get_dir_by_id(id):
    session = Session(engine)
    session.close()
    return session.query(WindDirection).filter_by(Id=id).first()


def get_all_forecasts_for(id_place):
    session = Session(engine)
    session.close()
    result = []
    for wf in session.query(WeatherForecast).filter_by(PlaceId=id_place, IsForecast=1):
        result.append(wf)
    return result


def get_actual_weather(id_place):
    actual_time = 1546012049000  # TODO change to time.time()
    all_weathers = get_all_actual_weathers(id_place, actual_time)
    not_null_weathers = []
    for weather in all_weathers:
        if (weather.Weather_TypeId is not None) & (weather.Wind_DirId is not None) & (weather.Temperature is not None):
            not_null_weathers.append(weather)
    return not_null_weathers[0]


def get_all_actual_weathers(id_place, date):
    session = Session(engine)
    session.close()
    result = []
    for wf in session.query(WeatherForecast).filter_by(PlaceId=id_place, Date=date, IsForecast=0):
        result.append(wf)
    return result


# GET PLACE --3 versions
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


def is_acceptable_distance(first, second, param):
    if (first is None) | (second is None):
        return False
    diff = abs(first - second)
    if (param == 'latitude') & (diff < 0.005):
        return True
    if (param == 'longitude') & (diff < 0.1):
        return True
    return False


# official - TO USE:
def get_place_id(latitude, longitude, name, country):
    place = get_place_by_all_data(latitude, longitude, name, country)
    if place is not None:
        return place.Id
    place = get_place_by_coordinates(latitude, longitude)
    if place is not None:
        return place.Id
    place = get_place_by_name(name, country)
    lat_dist = is_acceptable_distance(latitude, place.Latitude, 'latitude')
    long_dist = is_acceptable_distance(longitude, place.Longitude, 'longitude')
    if lat_dist & long_dist:
        return place.Id
    return insert_place(name, latitude, longitude, country)


# DECISION MODULE:
def create_one_forecast(list_of_forecasts, date):
    Weather_TypeId = []
    Wind_DirId = []
    Date = date
    Temperature = []
    Temperature_Max = []
    Temperature_Min = []
    Cloud_cover = []
    Humidity_percent = []
    Pressure_mb = []
    Wind_speed = []
    IsForecast = 1
    for i in list_of_forecasts:
        Weather_TypeId.append(i.Weather_TypeId)
        Wind_DirId.append(i.Wind_DirId)
        Temperature.append(i.Temperature)
        Temperature_Max.append(i.Temperature_Max)
        Temperature_Min.append(i.Temperature_Min)
        Cloud_cover.append(i.Cloud_cover)
        Humidity_percent.append(i.Humidity_percent)
        Pressure_mb.append(i.Pressure_mb)
        Wind_speed.append(i.Wind_speed)
    Weather_TypeId = get_most_common(Weather_TypeId)
    Wind_DirId = get_most_common(Wind_DirId)
    Temperature = list(filter(None.__ne__, Temperature))
    if not Temperature:
        Temperature = None
    else:
        Temperature = np.mean(Temperature)
    Temperature_Max = list(filter(None.__ne__, Temperature_Max))
    if not Temperature_Max:
        Temperature_Max = None
    else:
        Temperature_Max = np.mean(Temperature_Max)
    Temperature_Min = list(filter(None.__ne__, Temperature_Min))
    if not Temperature_Min:
        Temperature_Min = None
    else:
        Temperature_Min = np.mean(Temperature_Min)
    Cloud_cover = list(filter(None.__ne__, Cloud_cover))
    if not Cloud_cover:
        Cloud_cover = None
    else:
        Cloud_cover = np.mean(Cloud_cover)
    Humidity_percent = list(filter(None.__ne__, Humidity_percent))
    Humidity_percent = np.mean(Humidity_percent)
    Pressure_mb = list(filter(None.__ne__, Pressure_mb))
    if not Cloud_cover:
        Pressure_mb = None
    else:
        Pressure_mb = np.mean(Pressure_mb)
    Wind_speed = list(filter(None.__ne__, Wind_speed))
    Wind_speed = np.mean(Wind_speed)
    return WeatherForecast(0, Weather_TypeId, Wind_DirId, Date, Temperature_Max, Temperature_Min, Temperature,
                 Cloud_cover, Humidity_percent, Pressure_mb, Wind_speed, IsForecast)


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
            hours_forecasts.append(create_one_forecast(first_day, first_day[0].Date))
        if len(second_day) > 0:
            hours_forecasts.append(create_one_forecast(second_day, second_day[0].Date))
        if len(third_day) > 0:
            hours_forecasts.append(create_one_forecast(third_day, third_day[0].Date))
        if len(fourth_day) > 0:
            hours_forecasts.append(create_one_forecast(fourth_day, fourth_day[0].Date))
        if len(fifth_day) > 0:
            hours_forecasts.append(create_one_forecast(fifth_day, fifth_day[0].Date))
        return hours_forecasts


# RETURNS LIST OF FORECAST FOR PLACE
def decide(actual_weather, all_forecasts):
    # creating set of date >= actual
    date_set = set()
    for all in all_forecasts:
        if actual_weather.Date <= all.Date:
            date_set.add(all.Date)
    date_set = sorted(date_set)
    done_forecast = []
    # first forecast - actual weather
    # creating one forecast for datetime
    done_forecast.append(actual_weather)
    for x in date_set:
        forecast = get_all_forecast_for_timestamp(x, all_forecasts)
        result = create_one_forecast(forecast, x)
        done_forecast.append(result)
    done_forecast = filter_result_to_format(done_forecast)
    return done_forecast


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1339, debug=True)

# TEST (with classes declaration):
# session = Session(engine)
# u1 = session.query(WindDirection).first()
# print(str(u1))
