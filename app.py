#!/usr/bin/python3

# Import dependencies
import sqlalchemy
import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify, url_for

# DB setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Initialize Flask app here
app = Flask(__name__)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Routes

'''
Home page
List all routes that are available
'''
@app.route('/')
def index():
    routes = { 'available_routes' : [
                                        '/api/v1.0/precipitation',
                                        '/api/v1.0/stations',
                                        '/api/v1.0/tobs',
                                        '/api/v1.0/<start>',
                                        '/api/v1.0/<Cstart>/<end>'
                                    ]}

    return jsonify(routes)


'''
Convert the query results to a dictionary using date as the key and prcp as the value.
Return the JSON representation of your dictionary.
'''
@app.route('/api/v1.0/precipitation')
def precipitation():
    # Open connection to DB, query then close.
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).\
        order_by(Measurement.date)
    session.close()

    dataset = []
    for date, temp in results:
        dataset.append({date: temp})

    return jsonify(dataset)


# Return a JSON list of stations from the dataset.
@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    results = session.query(Station.name).all()
    session.close()

    return jsonify(results)


'''
Query the dates and temperature observations of the most active station for the last year of data.
Return a JSON list of temperature observations (TOBS) for the previous year.
'''
@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)

    # Find the most recent date in the data set.
    last_measure_date = session.query(func.max(Measurement.date)).scalar()

    # Get the date of one year ago from the last measured date in the population
    one_year_ago = dt.datetime.strptime(last_measure_date,'%Y-%m-%d') - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.tobs).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= one_year_ago).\
            order_by(Measurement.date).all()

    session.close()

    # Flatten list of lists into a single list
    temp_list = []
    for row in results:
        temp_list.append(row[0])

    return jsonify(temp_list)


'''
Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
'''
@app.route('/api/v1.0/<start>')
def start(start):
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).one()

    session.close()

    return jsonify({'TMIN':results[0], 'TMAX':results[1], 'TAVG':results[2]})


'''
When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
'''
@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).\
            filter(func.strftime("%Y-%m-%d", Measurement.date) <= end).one()
    session.close()

    return jsonify({'TMIN':results[0], 'TMAX':results[1], 'TAVG':results[2]})




if __name__ == "__main__":
    # @TODO: Create your app.run statement here
    app.run(debug=True)