#importing dependencies 
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


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


#precipitation route 
@app.route("/api/v1.0/precipitation")
def names():
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
    
    return jsonify(precipitation)
  


if __name__ == '__main__':
    app.run(debug=True)
