import pandas as pd 
import numpy as np 
from datetime import datetime
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

from flask import Flask, jsonify

# Reading the hawaii.sqlite data base 
engine = create_engine("sqlite:///hawaii.sqlite", connect_args={'check_same_thread': False})

# Reflect database into ORM class
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

# To be able to query the Session(engine) 
session = Session(engine)

# Setting up the "flask = micro web applications to create a web server" 
# __name__ = Current file

app = Flask(__name__)

# To be able to follow a link we route to google, we will running in our 
# local host 127.0.0.1

# @app.route("/") 
# // def home():
#     return <html>
# //  return (
# //    f"/api/v1.0/station<br/>"
# //      f"/api/v1.0/precipitation<br/>"
# //      f"/api/v1.0/temperatures<br/>"
# //      f"/api/v1.0/<start>(start date '%Y-%m-%d')<br/>"
# //      f"/api/v1.0/<start>/<end>(start/end date '%Y-%m-%d')"
# //   )

@app.route("/")
def welcome():
   """Available API routes in the program."""
   return"""<html>
   <h1>Information of the Hawaii stations, precipitation and temperature from the sqlite file</h1>
   <ul>
   <br>
   <li>
   From August 23 2016 to August 23 2017 data:
   <br>
   <a href="/api/v1.0/stations">/api/v1.0/stations</a>
   </li>
   <br>
   <li>
   Dictionary from the accumulated data:
   <br>
  <a href="/api/v1.0/precipitations">/api/v1.0/precipitations</a>
  </li>
   <br>
   <li>
  Dictionary information for temperature:
   <br>
   <a href="/api/v1.0/temperatures">/api/v1.0/temperatures</a>
   </li>
   <br>
   <li>
   For temperature Maximum, Minimum and Average
   <br>Start date.
   <br>
   <a href="/api/v1.0/temp/<start>">/api/v1.0/temp/<start></a>
   </li>
   <br>
   <li>
  Data from vacation time:
   <br>
 Vacation timme
   <br>
   <br>
   <a href="/api/v1.0/temp/<start>/<end>">/api/v1.0/temp/<start>/<end></a>
   </li>
   <br>
   </ul>
   </html>
   """

@app.route('/api/v1.0/stations')
def stations():
    station_list = session.query(Station).all()
# Using the list of stations information to create a dictionary
    stations = []
    for station in station_list:
        stations_dict = {}
        stations_dict['name'] = station.name 
        stations_dict['latitude'] = station.latitude
        stations_dict['longitude'] = station.longitude
        stations_dict['elevation'] = station.elevation
        stations.append(stations_dict)
    return jsonify(stations)

@app.route('/api/v1.0/precipitations')
def precipitations():
    One_year_precipitation = session.query(Measurement.date, func.avg(Measurement.prcp)).\
        filter(Measurement.date >= '2016-08-23').\
            filter(Measurement.date <= '2017-08-23').\
                group_by(Measurement.date).all()
# Using the list of stations information to create a dictionary

    precipitations = []
    for precipitation in One_year_precipitation:
        x = list(np.ravel(precipitation))
        date_realtime = dt.datetime.strptime(x[0], "%Y-%m-%d")
        precipitation_dict = {}
        precipitation_dict[str(date_realtime)] = '{:.3f}'.format(float(x[1]))
        precipitations.append(precipitation_dict)
    return jsonify(precipitations)

@app.route('/api/v1.0/temperatures')
def temperatures():
    One_year_temperature = session.query(Measurement.date, func.avg(Measurement.tobs)).\
        filter(Measurement.date >= '2016-08-23').\
            filter(Measurement.date <= '2017-08-23').\
                group_by(Measurement.date).all()
# Using the list of stations information to create a dictionary
    temperatures= []
    for temperature in One_year_temperature:
        x = list(np.ravel(temperature))
        tobs_realtime = dt.datetime.strptime(x[0], "%Y-%m-%d")
        temperature_dict = {}
        temperature_dict[str(tobs_realtime)] =  '{:.2f}'.format(float(x[1]))
        temperatures.append(temperature_dict)
    return jsonify(temperatures)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)



if __name__ == '__main__':
    app.run(debug=True)
    app.debug=True