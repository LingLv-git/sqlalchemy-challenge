# import dependency
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct
import numpy as np

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
climate = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>" 
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(climate.date, climate.prcp).all()
    session.close()
    date = []
    prcp = []
    for ddate, dprcp in results:
        date.append(ddate)
        prcp.append(dprcp)
    precipitation = dict(zip(date, prcp))    
    
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(distinct(climate.station)).all()
    station = list(np.ravel(results))
    
    return jsonify(station)

@app.route("/api/v1.0/tobs")
def temperature():
    session = Session(engine)
    recent_date = session.query(climate.date).\
        order_by(climate.date.desc()).first()[0]
    
    year = str(recent_date).split("-")[0]
    last_year = str(int(year)-1)
    
    active_station = session.query(climate.station, func.count(climate.station)).\
        filter(func.strftime("%Y", climate.date) == last_year).\
        group_by(climate.station).\
        order_by(func.count(climate.station).desc()).first()[0]
    
    temperature = session.query(climate.tobs).\
        filter(func.strftime("%Y", climate.date) == last_year).\
        filter(climate.station==active_station).all()
    temp = list(np.ravel(temperature))        

    return jsonify(temp)

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    temp = session.query(func.min(climate.tobs),
        func.max(climate.tobs), 
        func.avg(climate.tobs)).\
        filter(climate.date>=start).all()
    
    temperature = list(np.ravel(temp))
    name = ['TMIN', 'TMAX', 'TAVG']
    stats = dict(zip(name, temperature))
    return jsonify(stats)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)
    temp = session.query(func.min(climate.tobs),
        func.max(climate.tobs), 
        func.avg(climate.tobs)).\
        filter(climate.date.between(start, end)).all()
    
    temperature = list(np.ravel(temp))
    name = ['TMIN', 'TMAX', 'TAVG']
    stats = dict(zip(name, temperature))
    
    return jsonify(stats)           

if __name__ == "__main__":
    app.run(debug=True)

