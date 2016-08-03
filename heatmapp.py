#! usr/bin/env python

from flask import Flask, render_template, request, g, jsonify
from sqlalchemy import create_engine
from flask_compress import Compress
from datetime import date, timedelta
import os

from flask_sqlalchemy import SQLAlchemy


# For models
from sqlalchemy.dialects.postgresql import ARRAY, DOUBLE_PRECISION, INTEGER, TIMESTAMP, JSON


# This app is outgrowing this single-file setup. The next step is to modularize
#  it but for now we'll stick with this while we get the SQLAlchemy data models
#  working


# Configuration
# Later we'll put this in a config.py file
SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
DEBUG = True
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Initialization. Later we'll put this in the __init__.py file
app = Flask(__name__)
app.config.from_object(__name__)
Compress(app)

db = SQLAlchemy(app)
db.create_all()
db.session.commit()


# Data models.  These will go in models.py later


class User(db.Model):
    name = db.Column(db.String(),  primary_key=True)
    gc_username = db.Column(db.String())
    gc_password = db.Column(db.String())

    activities = db.relationship("Activity", backref="user", lazy="dynamic")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<User %r>" % (self.name)


class Activity(db.Model):
    user_name = db.Column(db.String(), db.ForeignKey("user.name"))
    id = db.Column(INTEGER, primary_key=True)
    beginTimestamp = db.Column(TIMESTAMP)
    summary = db.Column(JSON)
    elapsed = db.Column(ARRAY(INTEGER))
    latitudes = db.Column(ARRAY(DOUBLE_PRECISION))
    longitudes = db.Column(ARRAY(DOUBLE_PRECISION))

    def __init__(self, user_name, id, beginTimestamp, summary, elapsed, latitudes, longitudes):
        self.user_name = user_name
        self.id = id
        self.beginTimestamp = beginTimestamp
        self.summary = summary
        self.elapsed = elapsed
        self.latitudes = latitudes
        self.longitudes = longitudes

    def __repr__(self):
        return "<Activity %s - %r>" % (self.user_name, self.id)


# Web views
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/points')
def points():
    tomorrow = (date.today() + timedelta(1)).strftime('%Y-%m-%d')
    today = date.today().strftime('%Y-%m-%d')

    start = request.args.get("start", today)
    end = request.args.get("end", tomorrow)

    points = [[row[0], row[1]] for row in get_points(start, end)]
    resp = jsonify(points)
    resp.status_code = 200

    return resp


def get_points(start=None, end=None):
    # TODO: make sure datetimes are valid and start <= finish

    query = """
            SELECT  lat, lng
            FROM (
                SELECT elapsed, lat, lng
                FROM(
                    SELECT unnest(elapsed) AS elapsed,
                           unnest(latitudes) AS lat,
                           unnest(longitudes) AS lng
                    FROM %s
                    WHERE begintimestamp >= '%s'
                      AND begintimestamp <= '%s'
                    ) AS sub
                ) AS sub2
            WHERE lat <> 0 AND lng <> 0;
            """ % ("activities", start, end)

    result = query_db(query)
    return result


# This works but you really should use `flask run`
if __name__ == '__main__':
    app.run()
