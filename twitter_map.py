from flask import Flask, flash, render_template, redirect, request, session, url_for,g
from model import session as db_session, Tweet
from flask.ext.sqlalchemy import SQLAlchemy
import model
import data
import os

app = Flask(__name__)
app.config.from_object(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/twitter'
app.secret_key = 'some_key'

@app.route("/")
def index():
    tweet_city_dict = data.map_cities_to_tweets()
    return render_template("test.html", tweet_city_dict=tweet_city_dict)

if __name__ == "__main__":
    app.run(debug=True)
