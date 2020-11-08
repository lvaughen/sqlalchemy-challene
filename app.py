#################################################
# Dependencies
#################################################

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, desc
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
inspector = inspect(engine)
table_names = inspector.get_table_names()

# check db connection with engine
# print(table_names)

#################################################
# Reflect tables in ORM class (Measurement, Station)
#################################################

Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement

Base = automap_base()
Base.prepare(engine, reflect=True)
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"""Available Routes:<br/>
        /api/v1.0/precipitation<br/>
        /api/v1.0/stations<br/>
        /api/v1.0/tobs<br/>
        /api/v1.0/<start><br/>
        /api/v1.0/<start>/<end>"""
    )
#################################################
# Define query for percipitation route
#################################################

@app.route("/api/v1.0/precipitation")
def precip():
# start a session to query to support the percipitation route
    session = Session(engine)
    results = session.query(Measurement.station, Measurement.date, Measurement.prcp, Measurement.tobs).all()
    session.close()

    precip_data = list(np.ravel(results))
    
    # Create a dictionary from the row data and append to a list of measurement data
    measurement_data = []
    for stat, date, precip, temp in results:
        measurement_dict = {}
        measurement_dict["Station"] = stat
        measurement_dict["Date"] = date
        measurement_dict["Precipitation"] = precip
        measurement_dict["Temperature"] = temp
        measurement_data.append(measurement_dict)
    
    return jsonify(measurement_data)


#################################################
# Define query for stations
#################################################

@app.route("/api/v1.0/stations")
def stations():
# start a session to query to support the percipitation route
    session = Session(engine)
    results = session.query(Measurement.station).group_by(Measurement.station).all()
    session.close()

    # Get the data from the session query and append to a list of station list
    station_data = []
    for stat in results:
        station_data.append(stat)
    
    return jsonify(station_data)

#################################################
# Define query for temp (tobs)
#################################################

@app.route("/api/v1.0/tobs")
def tobs():
# start a session to query to support the percipitation route
    session = Session(engine)
    
    # calculate year date: date 1 week ago from today
    query_date = dt.date(2017,8,23) - dt.timedelta(days=365)
    # print(query_date)
    
    results = session.query(Measurement.station, Measurement.date, Measurement.tobs)\
    .filter(Measurement.station == 'USC00519281').filter(Measurement.date > query_date).all()
    session.close()

    # Get the data from the session query and append to a list of station tobs list
    station_tobs = []
    for stat in results:
        station_tobs.append(stat)
    
    return jsonify(station_tobs)

#################################################
# Define query for station data given start 
#################################################

@app.route("/api/v1.0/<start>")
def stat_data_start(start):

# start a session to query to support the station data from a start date
# provided by the user

    # determine start date from user input
    query_date = start 
    #return(query_date)

    # dev session query to get data from user input
    session = Session(engine)
      
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
    .filter(Measurement.date >= query_date).all()
    session.close()

       
    # Create a dictionary from the row data and append to a list of measurement data
    station_start_data = []
    for min_t, ave_t, max_t in results:
        stat_start_dict = {}
        stat_start_dict["Min temp"] = min_t
        stat_start_dict["Average temp"] = ave_t
        stat_start_dict["Max temp"] = max_t
        station_start_data.append(stat_start_dict)
    
    
    return jsonify(station_start_data)

#################################################
# Define query for station data given start and stop date
#################################################

@app.route("/api/v1.0/<start>/<end>")
def stat_str_end(start, end):

# start a session to query to support the station data from a start date
# provided by the user

    # determine start date from user input
    query_start = start 
    query_stop = end
    #return(query_date)

    # dev session query to get data from user input
    session = Session(engine)
      
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
    .filter(Measurement.date >= query_start).filter(Measurement.date <= query_stop).all()
    session.close()

       
    # Create a dictionary from the row data and append to a list of measurement data
    station_st_end_data = []
    for min_t, ave_t, max_t in results:
        stat_st_end_dict = {}
        stat_st_end_dict["Min temp"] = min_t
        stat_st_end_dict["Average temp"] = ave_t
        stat_st_end_dict["Max temp"] = max_t
        station_st_end_data.append(stat_st_end_dict)
    
    
    return jsonify(station_st_end_data)


if __name__ == '__main__':
    app.run(debug=True)