from model import Tweet, Chicago, Los_Angeles, San_Francisco, Houston, Atlanta, New_York, Seattle, Miami, Boston
from math import sqrt, log 
import math
import model
import string
from data import los_angeles, chicago, san_francisco, new_york, miami, atlanta, houston, seattle, boston
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
    'Atlanta': 'small_blue',
    'Boston': 'small_yellow'
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
		another_row = [city_to_color_map[city], city, tweet.screename, tweet.text.encode("utf").lower().translate(string.maketrans("",""),string.punctuation), tweet.latitude, tweet.longitude, tweet.created_at]
		fusion_table_writer.writerow(another_row)

									
	la_red_marker = ['large_red', 'Los Angeles', ' ', ' ', 34.0522, -118.2436, ' ']
	sf_blue_marker = ['large_blue', 'San Francisco', ' ', ' ', 37.781569, -122.416534, ' '] 
	ch_green_marker = ['large_green', 'Chicago', ' ', ' ', 41.878, -87.6298, ' '] 
	mi_yellow_marker = ['large_yellow', 'Miami', ' ', ' ', 25.7889, -80.2264, ' ']
	ho_purple_marker = ['large_purple', 'Houston', ' ', ' ', 29.760, -95.369, ' '] 
	ny_red_marker = ['large_red', 'New York', ' ', ' ', 40.703546, -73.951721, ' ']
	se_yellow_marker = ['large_yellow', 'Seattle', ' ', ' ', 47.609,  -122.33, ' ']
	at_blue_marker = ['large_blue', 'Atlanta', ' ', ' ', 33.749, -84.3879, ' ']
	bo_yellow_marker = ['large_yellow', 'Boston', ' ', ' ', 42.3583 , -71.0603, ' '] 

	fusion_table_writer.writerow(la_red_marker)
	fusion_table_writer.writerow(sf_blue_marker)
	fusion_table_writer.writerow(ch_green_marker)
	fusion_table_writer.writerow(mi_yellow_marker)
	fusion_table_writer.writerow(ho_purple_marker)
	fusion_table_writer.writerow(ny_red_marker)
	fusion_table_writer.writerow(se_yellow_marker)
	fusion_table_writer.writerow(at_blue_marker)
	fusion_table_writer.writerow(bo_yellow_marker)


















if __name__ == "__main__":
        main()
