from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import json
from flask import request
from sqlalchemy import inspect
from sqlalchemy.sql import select

app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'sql7264364'
app.config['MYSQL_DATABASE_PASSWORD'] = 'vQcYAx9aes'
app.config['MYSQL_DATABASE_DB'] = 'sql7264364'
app.config['MYSQL_DATABASE_HOST'] = 'sql7.freemysqlhosting.net'
engine = create_engine('mysql+mysqldb://sql7264364:vQcYAx9aes@sql7.freemysqlhosting.net/sql7264364')

db = SQLAlchemy(app)
Base = automap_base()
Base.prepare(engine, reflect=True)
inspector = inspect(engine)
conn = engine.connect()
        
session = Session(engine)
class Place():
    def __init__(self, Id, Name, Latitude, Longitude, Country):
        self.Id = Id
        self.Name = Name
        self.Latitude = Latitude
        self.Longitude = Longitude
        self.Country = Country
    
@app.route('/_get_current_dir')
def get_current_dir():
    WindDirection = Base.classes.Wind_Direction
    s = select([WindDirection])
    result = conn.execute(s)
    return json.dumps([dict(r) for r in result])

@app.route('/places', methods=['GET'])
def get_places():
    places = Base.classes.Place
    s = select([places])
    result = conn.execute(s)
    Places=[]
    for r in result:
        Places.append(Place(r["Id"],r["Name"],str(r["Latitude"]),str(r["Longitude"]), r["Country"]))
    return json.dumps([p.__dict__ for p in Places])

@app.route('/places', methods=['POST'])
def post_place():
    data =request.get_json()
    place = Base.classes.Place
    session.add(place(Name = data["Name"], Latitude = data["Latitude"], Longitude = data["Longitude"], Country = data["Country"]))
    session.commit()
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@app.route('/forecast', methods=['POST'])
def post_forecast():
    data =request.get_json()
    forecast = Base.classes.Weather_Forecast
    wtId = calculateTypeId(data["Main"], data["Desc"])
    
    session.add(forecast(PlaceId = data["PlaceId"], Weather_TypeId= wtId, Wind_DirId = data["Wind_DirId"], Date = data["Date"], Temperature = data["Temperature"], Temperature_Max = data["Temperature_Max"], Temperature_Min = data["Temperature_Min"], Cloud_cover = data["Cloud_cover"], Humidity_percent = data["Humidity_percent"], Pressure_mb = data["Pressure_mb"], Wind_speed = data["Wind_speed"], IsForecast = data["IsForecast"]))
    session.commit()
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

def calculateTypeId(main, desc):
    wtId = get_type(main, desc)
    if(wtId<0):
        insert_type(main, desc)
        wtId=get_type(main, desc)
    return wtId

def get_type(main, desc):
    Weather_Type = Base.classes.Weather_Type
    for wt in session.query(Weather_Type).filter_by(Main=main, Description=desc):
        return wt.Id

def insert_type(main, desc):
    WT = Base.classes.Weather_Type
    session.add(WT(Main=main,Description=desc))
    session.commit()

if __name__ == '__main__':
    app.run(debug=True)
    print ("closing session")
    session.close_all()