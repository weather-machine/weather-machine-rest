    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy import create_engine
    from sqlalchemy.ext.automap import automap_base
    from sqlalchemy.orm import Session
    import json
    from flask import request
    from sqlalchemy import inspect
    from sqlalchemy.sql import select
    from flask_cors import CORS, cross_origin
    
    app = Flask(__name__)
    app.config['MYSQL_DATABASE_USER'] = 'sql7269522'
    app.config['MYSQL_DATABASE_PASSWORD'] = 'pwxmSWjpqa'
    app.config['MYSQL_DATABASE_DB'] = 'sql7269522'
    app.config['MYSQL_DATABASE_HOST'] = 'sql7.freemysqlhosting.net'
    engine = create_engine('mysql+mysqldb://sql7269522:pwxmSWjpqa@sql7.freemysqlhosting.net/sql7269522')
    
    cors = CORS(app)
    
    db = SQLAlchemy(app)
    Base = automap_base()
    Base.prepare(engine, reflect=True)
    inspector = inspect(engine)
    conn = engine.connect()
            
    class Place():
        def __init__(self, Id, Name, Latitude, Longitude, Country):
            self.Id = Id
            self.Name = Name
            self.Latitude = Latitude
            self.Longitude = Longitude
            self.Country = Country
        
    @app.route('/_get_current_dir')
    @cross_origin()
    def get_current_dir():
        WindDirection = Base.classes.Wind_Direction
        s = select([WindDirection])
        result = conn.execute(s)
        return json.dumps([dict(r) for r in result])
    
    @app.route('/places', methods=['GET'])
    @cross_origin()
    def get_places():
        places = Base.classes.Place
        s = select([places])
        result = conn.execute(s)
        Places=[]
        for r in result:
            Places.append(Place(r["Id"],r["Name"],str(r["Latitude"]),str(r["Longitude"]), r["Country"]))
        return json.dumps([p.__dict__ for p in Places])
    
    @app.route('/places', methods=['POST'])
    @cross_origin()
    def post_place():
        session = Session(engine)
        data =request.get_json()
        place = Base.classes.Place
        session.add(place(Name = data["Name"], Latitude = data["Latitude"], Longitude = data["Longitude"], Country = data["Country"]))
        session.commit()
        session.close()
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    
    @app.route('/forecast', methods=['POST'])
    @cross_origin()
    def post_forecast():
        session = Session(engine)
        data =request.get_json()
        forecast = Base.classes.Weather_Forecast
        wtId = calculateTypeId(data["Main"], data["Desc"])
        
        session.add(forecast(PlaceId = data["PlaceId"], Weather_TypeId= wtId, Wind_DirId = data["Wind_DirId"], Date = data["Date"], Temperature = data["Temperature"], Temperature_Max = data["Temperature_Max"], Temperature_Min = data["Temperature_Min"], Cloud_cover = data["Cloud_cover"], Humidity_percent = data["Humidity_percent"], Pressure_mb = data["Pressure_mb"], Wind_speed = data["Wind_speed"], IsForecast = data["IsForecast"]))
        session.commit()
        session.close()
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    
    def calculateTypeId(main, desc):
        wtId = get_type(main, desc)
        if(wtId is None):
            insert_type(main, desc)
            wtId=get_type(main, desc)
        return wtId
    
    def get_type(main, desc):
        session = Session(engine)
        Weather_Type = Base.classes.Weather_Type
        session.close()
        for wt in session.query(Weather_Type).filter_by(Main=main, Description=desc):
            return wt.Id
    
    def insert_type(main, desc):
        session = Session(engine)
        WT = Base.classes.Weather_Type
        session.add(WT(Main=main,Description=desc))
        session.commit()
        session.close()
        
    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=1339, debug=True)
        session.close_all()
