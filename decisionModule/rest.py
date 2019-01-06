from flask import Flask, request
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, inspect
from sqlalchemy.dialects.mysql import BIGINT, DOUBLE
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

import simplejson as json
import time
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
    forecasts = get_all_forecasts_for(id_place=id_place)
    resul = []
    resul.append(get_actual_weather(id_place))
    # TODO remove
    for i in range(0, 24):
        resul.append(forecasts[i])
    #end todo

    result = change_all_record_to_wa(resul, id_place, name, latitude, longitude, country)
    return change_to_json(result), 200, {'ContentType':'application/json'}


# UTILS:
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1339, debug=True)

# TEST (with classes declaration):
# session = Session(engine)
# u1 = session.query(WindDirection).first()
# print(str(u1))
