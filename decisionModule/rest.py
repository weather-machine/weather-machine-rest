from flask import Flask, request
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, Numeric, TIMESTAMP, ForeignKey, inspect
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

import json
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
        return self.direction

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
    Date = Column(TIMESTAMP)
    Temperature = Column(Numeric)
    Temperature_Max = Column(Numeric)
    Temperature_Min = Column(Numeric)
    Cloud_cover = Column(Numeric)
    Humidity_percent = Column(Numeric)
    Pressure_mb = Column(Numeric)
    Wind_speed = Column(Numeric)
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
        return self.Id.__str__() + " - " + self.Main

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


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


# DATABASE OPERATIONS:
def insert_place(name, latitude, longitude, country):
    session = Session(engine)
    session.add(Place(name, latitude, longitude, country))
    session.commit()
    session.close()


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


# TEST (with classes declaration):
# session = Session(engine)
# u1 = session.query(WindDirection).first()
# print(str(u1))
