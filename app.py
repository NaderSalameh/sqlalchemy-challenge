#importing dependencies 
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import and_


#setting up Flask
app = Flask(__name__)

#setting up the engine
engine = create_engine("sqlite:///hawaii.sqlite")

# reflecting database
Base = automap_base()

# reflecting the tables
Base.prepare(engine, reflect=True)

# creating the classes
Measurement = Base.classes.measurement
Station = Base.classes.station   


# creating home page
@app.route("/")
def home():
    print("Welcome!")
    return ( 
        f"Here is a list of all available routes:<br/>" 
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


# precipitation route 
@app.route("/api/v1.0/precipitation")
def precipitation():
    # creating session
    session = Session(engine)

    # grabbing the most recent date in the "measurements" table
    most_recent_date = session.query(Measurement.date).order_by((Measurement.date).desc()).first()
    most_recent_date = datetime.strptime(most_recent_date[0], '%Y-%m-%d').date()

    # storing the 12 month offset from the most recent date 
    last_12 = most_recent_date + relativedelta(months=-12)

    # Performing a query to retrieve the date and precipitation scores
    query = session.query(Measurement.date, Measurement.prcp).\
                    filter(func.strftime(Measurement.date) >= last_12).\
                    filter(Measurement.prcp.isnot(None)).all()

    #closing session
    session.close()

    # Creating dictionary
    precipitation = []
    for date, prcp in query:
            precipitation_dictionary= {}
            precipitation_dictionary['date'] = date 
            precipitation_dictionary['precipitation'] = prcp
            precipitation.append(precipitation_dictionary)
    #json
    return jsonify(precipitation)



# stations route
@app.route("/api/v1.0/stations")
def stations():
    # creating session
    session = Session(engine)

    # returning all stations in the stations table
    query = session.query(Station.name).all()

    # closing session
    session.close()

    # creating a list of stations
    stations = list(np.ravel(query))

    # json
    return jsonify(stations)



# temperature observation route
@app.route("/api/v1.0/tobs")
def tobs():
    # creating session 
    session = Session(engine)

    #### querying the dates and temeparatures observations of the most active station for the last year of data ####
    #--.---------------.---------------.---------------.---------------.---------------.---------------.---------------.

    # grabbing the most recent date in the "measurements" table
    most_recent_date = session.query(Measurement.date).order_by((Measurement.date).desc()).first()
    most_recent_date = datetime.strptime(most_recent_date[0], '%Y-%m-%d').date()

    # storing the 12 month offset from the most recent date 
    last_12 = most_recent_date + relativedelta(months=-12)

    # initializing most_active_station for the last year. (12 months from the latest date in the data)
    most_active_station = session.query(Measurement.station).\
                                group_by(Measurement.station).\
                                order_by(func.count(Measurement.station).desc()).first()[0]

    # writing the actual query, as instructed, to pull the dates and temeparatures observations of the most active station for the last year of data
    session.query(Measurement.date, Measurement.tobs).\
                        filter(Measurement.station == most_active_station).\
                        filter(func.strftime(Measurement.date) >= last_12).\
                        filter(Measurement.tobs.isnot(None)).all()

    # storing the 24 month offset from the most recent date 
    last_24 = most_recent_date + relativedelta(months=-24)

    #### querying the dates and temeparatures observations of the most active station for the previous of data ####
    #--.---------------.---------------.---------------.---------------.---------------.---------------.---------------.

    query = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.station == most_active_station).\
                filter(and_(func.strftime(Measurement.date) >= last_24), func.strftime(Measurement.date < last_12)).\
                filter(Measurement.tobs.isnot(None)).all()


    #looping through query, grabbing temperatures and adding them to list
    temperature_of_observation = []
    for tobs in query:
        temperature_of_observation.append(tobs[1])

    # json
    return jsonify(temperature_of_observation)



    
if __name__ == '__main__':
    app.run(debug=True)
