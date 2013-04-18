from model import Tweet, Chicago, Los_Angeles, San_Francisco, Houston, Atlanta, New_York, Seattle, Miami
from math import sqrt, log 
import math
import model
import string
from data import los_angeles, chicago, san_francisco, new_york, miami, atlanta, houston, seattle
import data 
import csv



city_to_color_map = {
    'Los Angeles': 'small_red',
    'San Francisco': 'small_blue',
    'Chicago': 'small_green',
    'Miami': 'small_yellow',
    'Houston': 'small_purple',
    'New York': 'small_red',
    'Seattle': 'small_yellow',
    'Atlanta': 'small_blue'
    }

def main():
    with open('fusion.csv', 'a') as csvfile:
	fusion_table_writer = csv.writer(csvfile, delimiter=',', escapechar='/', quoting=csv.QUOTE_NONE)
	city_to_tweet_dict = data.map_cities_to_tweets()
	a_row = ['color','city', 'screename', 'text', 'latitude', 'longitude', 'created_at']
	fusion_table_writer.writerow(a_row)
	for city in city_to_tweet_dict.keys():
	    tweet_list = city_to_tweet_dict[city]
	    for tweet in tweet_list:
		another_row = [city_to_color_map[city.name], city.name, tweet.screename, tweet.text.encode("utf").lower().translate(string.maketrans("",""),string.punctuation), tweet.latitude, tweet.longitude, tweet.created_at] 
		fusion_table_writer.writerow(another_row)

















if __name__ == "__main__":
        main()
