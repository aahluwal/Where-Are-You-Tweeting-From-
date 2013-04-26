from flask import Flask, flash, render_template, redirect, request, session, url_for,g
#from model import session as db_session, Tweet
from flask.ext.sqlalchemy import SQLAlchemy
#import model
import data
from data import cities
import os
import feature_selection

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'some_key'



@app.route("/")
def index():
    tweet_city_dict = data.map_cities_to_tweets()
    return render_template("home.html", tweet_city_dict=tweet_city_dict)

@app.route("/classify_text", methods=["POST"])
def classify_text():
    tweet = request.form['tweet']
    rankings = data.create_ranking(tweet)
    top_5_words = feature_selection.top_words_in_tweet(rankings[0][0],tweet)
    cty_corpus_dict = data.city_corpus_dict()
    word_count_dict = cty_corpus_dict[rankings[0][0].name]
    final_result = []
    for word in top_5_words:
	final_result.append(word)

    names = []
    for i in range(0, len(rankings)):
	city_name = rankings[i][0].name
	names.append(city_name)
    return render_template("map.html", tweet=tweet, names=names, rankings=rankings, final_result=final_result)

@app.route("/classify_text", methods=["GET"])
def classify():
    return redirect(url_for("index"))

@app.route("/top_words", methods=["GET"])
def feature_select():
    cities = data.cities
    return render_template("features.html", cities=cities)

@app.route("/city/<city_name>", methods=["GET"])
def list_features(city_name):
    cities = data.cities
    city = None
    for i in range(0, len(cities)):
	if cities[i].name == city_name:
	    feature_list = feature_selection.get_hardcoded_features(cities[i])
	    city = cities[i]
    if city:
	latitude = city.lat
	longitude = city.lon
	city_name = city.name
	city_tweet_count = data.create_region_tweet_count(city)
	city_word_count = data.find_leng_city_corpus(city)
    return render_template("city_words.html", features= feature_list, city_name=city_name, latitude=latitude, longitude=longitude, city_tweet_count=city_tweet_count, city_word_count=city_word_count)


if __name__ == "__main__":
    app.run(debug=True)
