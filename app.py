import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite", connect_args={'check_same_thread':False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station


# Create our session (link) from Python to the DB
session = Session(engine)

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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f" <br/>"
        f"For below enter a date in format YYYY-MM-DD after v1.0/ to return results<br/>"
        f"/api/v1.0/<start><br/>"
        f" <br/>"
        f"For below enter a range of dates in format YYYY-MM-DD/YYYY-MM-DD after v1.0/ to return results<br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
# Query for the dates and temp observations from the last year.
def precipitation():
    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= "2016-08-23").all()
    
    #Create a dictionary from the row data and append to a list
    all_precipitation = []
    for precipitation in precipitation_data:
        precipitation_dict = {}
        precipitation_dict["date"] = precipitation.date
        precipitation_dict["prcp"] = precipitation.prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
# Query a JSON list of stations from the dataset
def stations():
    station_name_js = session.query(Station.name).group_by(Station.name).all()

    # Conver to a list
    all_stations = list(np.ravel(station_name_js))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
# Return a JSON list of Temp Observations (tobs) for the previous year.
def tobs():
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= "2016-08-23").all()

    # Convert to a list
    all_tobs = list(np.ravel(tobs_data))

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")

def temp_calcs(start):
# Query based on date entered into start
    station_count_stats = session.query(Measurement.date, func.min(Measurement.tobs),func.max(Measurement.tobs),\
    func.avg(Measurement.tobs)).group_by(Measurement.date).filter(Measurement.date == start).all()

# will need to create a list here for all three variables
    all_temp_calc = []
    for tobs in station_count_stats:
        row = {}
        row['Date'] = tobs[0]
        row['Min Temp'] = tobs[1]
        row['Max Temp'] = tobs[2]
        row['Avg Temp'] = tobs[3]
        all_temp_calc.append(row)

    return jsonify(all_temp_calc)


@app.route("/api/v1.0/<start>/<end>")

def temp_calcs_range(start, end):
# Query based on date entered into start
    station_count_stats_range = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),\
    func.avg(Measurement.tobs)).filter(Measurement.date >= start, Measurement.date <= end).all()

# will need to create a list here for all three variables
    all_temp_calc_range = []
    for tobs_range in station_count_stats_range:
        row = {}
        row["Start Date"] = start
        row["End Date"] = end
        row['Min Temp'] = tobs_range[0]
        row['Max Temp'] = tobs_range[1]
        row['Avg Temp'] = tobs_range[2]
        all_temp_calc_range.append(row)

    return jsonify(all_temp_calc_range)




if __name__ == "__main__":
    app.run(debug=True)
