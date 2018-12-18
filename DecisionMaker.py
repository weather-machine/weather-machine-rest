from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import json
from flask import request,requests
from sqlalchemy import inspect
from sqlalchemy.sql import select
from flask_cors import CORS, cross_origin

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
Base.prepare(engine, reflect=True)
inspector = inspect(engine)
conn = engine.connect()

@app.route('/forecast', methods=['GET'])
@cross_origin()
def get_forecast():
    session = Session(engine)
    session.close()
    data =request.get()
    Forecasts = Base.classes.Weather_Forecast
    PlaceId = getPlace(data)
    s = select([Forecasts]).where(Forecasts.PlaceId = PlaceId, Forecasts.isForecast=0)
    result = conn.execute(s)
    currentWeather =[]
    for r in result: 
        currentWeather.append()
    s = select([Forecasts]).where(Forecasts.PlaceId = PlaceId, Forecasts.isForecast=1)
    result = conn.execute(s)
    predictions = []
    for r in result: 
        predictions.append()
    FinalResult = make_decision(currentWeather, predictions)


def make_decision(currentWeather, predictions)