from model import session, Tweet, San_Francisco, Los_Angeles, Houston, New_York, Atlanta, Chicago, Miami
from math import sqrt
import model

def get_tweet_list():
    all_tweets = session.query(Tweet).filter(Tweet.longitude > -125).filter(Tweet.longitude < -65).filter(Tweet.latitude > 25).filter(Tweet.latitude < 50).all()
    list_of_tweets = []
    for tweet in all_tweets:
#	decoded_tweet = tweet.__repr__().decode("latin-1")
        list_of_tweets.append(tweet)
    return list_of_tweets 

def distance_between_2_points(start, end):
    lon1, lat1 = start
    lon2, lat2 = end
    dlon = lon2-lon1
    dlat = lat2-lat1
    distance = sqrt(((dlon)*(dlon))+((dlat)*(dlat)))
    return distance

def closest_major_cities(list_of_tweets):
    los_angeles = Los_Angeles()
    san_francisco = San_Francisco()
    houston = Houston()
    miami = Miami()
    atlanta = Atlanta()
    new_york = New_York()
    chicago = Chicago()
    cities = [los_angeles, san_francisco, houston, miami, atlanta, new_york, chicago]
    
    tweet_cities = []
    for tweet in list_of_tweets:
	closest_city = cities[0]
	for i in range(1, len(cities)-1):
	    new_city = cities[i]
	    if distance_between_2_points((closest_city.lon, closest_city.lat),(tweet.longitude,tweet.latitude)) > distance_between_2_points((new_city.lon, new_city.lat), (tweet.longitude,tweet.latitude)):
		closest_city = new_city 
	tweet_cities.append(closest_city)
    return tweet_cities

def map_cities_to_tweets():
    list_of_us_tweets = get_tweet_list()
    major_cities = closest_major_cities(list_of_us_tweets)
    tweet_to_city_dict = {}
    for i in range(0, len(major_cities)-1):
	tweet = list_of_us_tweets[i]
	city = major_cities[i]
	if city not in tweet_to_city_dict:
	    tweet_to_city_dict[city] = [tweet]
	else:
	    previous = tweet_to_city_dict[city]
	    tweet_to_city_dict[city] = tweet_to_city_dict[city] + [tweet] 
    return tweet_to_city_dict 


if __name__ == "__main__":
    main()
