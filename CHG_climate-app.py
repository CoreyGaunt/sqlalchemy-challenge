# Bring in dependecies needed to create Flask app

import pandas as pd
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# create an engine

engine = create_engine("sqlite:///Resources/hawaii.sqlite",connect_args={'check_same_thread': False})

# reflect onto new model

Base = automap_base()

# reflect tables

Base.prepare(engine, reflect=True)

# Save references to tables

Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session link from Python to DB

session = Session(engine)

# Bring in needed code from notebook

date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
date = list(np.ravel(date))[0]

date_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

most_active_stations = session.query(Measurement.station,func.count(Measurement.station)).\
    group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).\
            all()

most_activeID = most_active_stations[0][0]

most_activeName = session.query(Station.name).\
    filter_by(station = most_activeID)[0][0]

# Flask setup

app = Flask(__name__)

# Flask Routes

@app.route("/")
def home():
    return

@app.route("/api/v1.0/precipitation")
def precip():
    results = (session.query(Measurement.date,Measurement.prcp,Measurement.station).\
        filter(Measurement.date >= date_year_ago).order_by(Measurement.date).all())

    precip_data = []
    for r in results:
        precip1 = {r.date: r.prcp,'Station':r.station}
        precip_data.append(precip1)

    return jsonify(precip_data)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()
    station_names = list(np.ravel(results))
    return jsonify(station_names)

@app.route("/api/v1.0/tobs")
def temp():
    results = session.query(Measurement.tobs,Measurement.date).\
    filter(Measurement.date >= date_year_ago).\
        filter(Measurement.station == most_activeID).\
            order_by(Measurement.date.asc()).\
                all()

    temp_data = []
    for r in results:
        temp_data.append(r.tobs)
    return jsonify(temp_data)

@app.route("/api/v1.0/<start>")
def start_date(start):
    sel = [Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    results = session.query(*sel).\
    filter(func.strftime("%Y-%m-%d",Measurement.date) >= start).\
        filter(Measurement.date).\
            all()
    dates = []
    for r in results:
        date_dict = {}
        date_dict['Date'] = r[0]
        date_dict['Lowest Temp (F)'] = r[1]
        date_dict['Highest Temp (F)'] = r[2]
        date_dict['Average Temp (F)'] = r[3]
        dates.append(date_dict)
    return jsonify(dates)

@app.route('/api/v1.0/<start>/<end>')
def start_end(start,end):
    sel = [Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    results = session.query(*sel).\
    filter(func.strftime("%Y-%m-%d",Measurement.date) >= start).\
        filter(func.strftime("%Y-%m-%d",Measurement.date) <= end).\
            filter(Measurement.date).\
                all()

    dates = []
    for r in results:
        date_dict = {}
        date_dict['Date'] = r[0]
        date_dict['Lowest Temp (F)'] = r[1]
        date_dict['Highest Temp (F)'] = r[2]
        date_dict['Average Temp (F)'] = r[3]
        dates.append(date_dict)
    return jsonify(dates)

if __name__ == "__main__":
    app.run(debug=True)

