class Place:
    def __init__(self, Id, Name, Latitude, Longitude, Country):
        self.Id = Id
        self.Name = Name
        self.Latitude = Latitude
        self.Longitude = Longitude
        self.Country = Country


class WeatherType:
    def __init__(self, id, main, description):
        self.id = id
        self.main = main
        self.description = description


class WeatherForecast:
    def __init__(self, id, weather_type, wind_dir_id, date, temperature, temperature_max, temperature_min, cloud_cover,
                 humidity_percent, pressure, wind_speed, is_forecast):
        self.place_id = id
        self.weather_type = weather_type
        self.wind_dir_id = wind_dir_id
        self.data = date
        self.temperature = temperature
        self.temperature_max = temperature_max
        self.temperature_min = temperature_min
        self.cloud_cover = cloud_cover
        self.humidity = humidity_percent
        self.pressure = pressure
        self.wind_speed = wind_speed
        self.is_forecast = is_forecast
