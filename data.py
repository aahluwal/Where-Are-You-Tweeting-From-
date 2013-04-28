from model import Word, Container, Tweet, Boston, San_Francisco, Los_Angeles, Houston, New_York, Atlanta, Chicago, Miami, Seattle
from math import sqrt, log, sin, cos, radians, atan2
from app import db
import math
import model
import string
import operator
import haversine
from operator import itemgetter 
from werkzeug.contrib.cache import MemcachedCache
cache = MemcachedCache(['127.0.0.1:11211'])
import json
import datetime


# Main Naiive Bayes classification equation derived from http://nlp.stanford.edu/IR-book/html/htmledition/naive-bayes-text-classification-1.html
#This paper says that P(Document/Class) AKA P(Tweet/City) is relative to P(City)*P(Word1/CITY)*P(Word2/CITY)*...*P(Wordn/CITY). I calculate this for every City and rank 
#the cities to see which city a tweet most likely came from

#global instances of each city
los_angeles = Los_Angeles()
san_francisco = San_Francisco()
houston = Houston()
miami = Miami()
atlanta = Atlanta()
new_york = New_York()
seattle = Seattle()
chicago = Chicago()
boston = Boston()
#global list of instances
cities = [los_angeles, san_francisco, houston, miami, atlanta, new_york, chicago, seattle, boston]
session = db.session


#Limit tweet results to be within 150 miles/240km of a major city
def distanceIsWithinHundredMiles(lon1,lat1,lon2,lat2):
    d = haversine.haversine(lon1, lat1, lon2, lat2)
    if d < 240:
	return True
    else:
	return False 


#Returns list of US tweets- Note: To increase speed I have placed indexes on longitude and latitude in tweets table using Postgresql.
ALL_TWEETS = []
def get_tweet_list():
    global ALL_TWEETS
    if ALL_TWEETS:
	return ALL_TWEETS

    all_tweets = session.query(Tweet).filter(Tweet.longitude > -125.0).filter(Tweet.longitude < -65.0).filter(Tweet.latitude > 25.0).filter(Tweet.latitude < 50.0).all()
    list_of_tweets = []
    for tweet in all_tweets:
	if tweet.text.startswith("RT"):
	    continue
	else:
	    list_of_tweets.append(tweet)

    ALL_TWEETS = list_of_tweets
    print "updating tweet list from db"
    return ALL_TWEETS


#Pythagorean theorem with haversine to account for earth's curvature. Calculates distance between tweet and city
def distance_between_2_points((lon1, lat1),(lon2, lat2)):
    d = haversine.haversine(lon1, lat1, lon2, lat2)
    return float(d)

#Return list of tweets and their corresponding, closest city, given that the city is within 150 miles of the tweet 
def closest_major_cities(list_of_tweets):
    tweet_cities = []
    for tweet in list_of_tweets:
	closest_city = cities[0]
	for i in range(1, len(cities)):
	    new_city = cities[i]
	    if distance_between_2_points((closest_city.lon, closest_city.lat),(tweet.longitude,tweet.latitude)) > distance_between_2_points((new_city.lon, new_city.lat), (tweet.longitude,tweet.latitude)):
		closest_city = new_city 
	if distanceIsWithinHundredMiles(tweet.longitude, tweet.latitude, closest_city.lon, closest_city.lat):
	    tweet_cities.append((tweet, closest_city))
    return tweet_cities

#Returns dictionary with cities/instances as keys and values of lists of the corresponding tweets for each city 
CITY_TWEET_MAP = None
def map_cities_to_tweets():
    global CITY_TWEET_MAP
    if CITY_TWEET_MAP:
	return CITY_TWEET_MAP
    list_of_us_tweets = get_tweet_list()	
    major_cities = closest_major_cities(list_of_us_tweets)
    tweet_to_city_dict = {}
    for i in range(0, len(major_cities)):
	tweet = major_cities[i][0]
	city_name = major_cities[i][1].name
	if city_name not in tweet_to_city_dict:
	    tweet_to_city_dict[city_name] = [tweet]
	else:
	    previous = tweet_to_city_dict[city_name]
	    tweet_to_city_dict[city_name] = tweet_to_city_dict[city_name] + [tweet] 
    CITY_TWEET_MAP = tweet_to_city_dict
    print "updating new city_tweet_map from db" 
    return CITY_TWEET_MAP

#Seeds into db dictionary inside dictionary, maps city names to key-value pair of word to # of tweets in city that word occurs in.
def city_tweet_corpus_dict():
    key = 'city_tweet_corpus_dict'
    n = session.query(Container).filter(Container.key==key).first()
    if not n:
	n={}
	tweet_to_city_dict = map_cities_to_tweets()
	for city in cities:
	    city_tweet_corpus_dict = {}

	    for tweet in tweet_to_city_dict[city.name]:
		tweet_text = tweet.text.encode("utf-8").lower().translate(string.maketrans("",""),string.punctuation).split()
		uniques = set(tweet_text)
		tweet_text = list(uniques)
		for word in tweet_text:
		    if word not in city_tweet_corpus_dict:
			city_tweet_corpus_dict[word]=1
		    else:
			previous = city_tweet_corpus_dict[word]
			city_tweet_corpus_dict[word] = previous+1
	    n[city.name] = city_tweet_corpus_dict
	d = Container(key=key, value=json.dumps(n))
	model.session.add(d)
	model.session.commit()
    else:
	n = json.loads(n.value)
    return n 

#Seeds into db dictionary inside dictionary, maps city names to key-value pair of word to probablity of word given city. 
def city_word_prob_dict():
    key = 'city_word_prob_dict'
    n  = session.query(Container).filter(Container.key== key).first()
    if not n:
	n = {}
	cty_corpus_dict = city_corpus_dict()
	for city in cities:
	    w_dic ={}
	    word_dict = cty_corpus_dict[city.name]
	    for word in word_dict.keys():
		w_dic[word] = prob_word_given_city(city,word)
	    n[city.name] = w_dic
	d = Container(key = key, value = json.dumps(n))
	model.session.add(d)
	model.session.commit()
    else:
	n = json.loads(n.value)
    return n


#Calls above function. Seeds into words table, city, word, and prob(W/City)
def seed_words_table():
    cty_word_prob_dict = city_word_prob_dict()
    for city in cities: 
	word_prob_dict = cty_word_prob_dict[city.name]
	for word in word_prob_dict.keys():
	    n = Word(word = word, city = city.name, probability = prob_word_given_city(city, word))
	    model.session.add(n)
	    model.session.commit()




# Begin Bayesian Problem

#Creates a dictionary inside dictionary, maps city name to key-value pairs of word in city to overall count of word occurrance in that city
def city_corpus_dict():
    key = 'city_corpus_dict'
    n = session.query(Container).filter(Container.key==key).first()
    if not n:
	print 'Couldn\'t get city corpus dict from database'
	tweet_to_city_dict = map_cities_to_tweets()
	n = {}
	for city in cities:
	    city_corpus_dict = {}
	    for tweet in tweet_to_city_dict[city.name]:
		tweet_text = tweet.text.encode("utf-8").lower().translate(string.maketrans("",""),string.punctuation).split()
		for word in tweet_text:
		    if word not in city_corpus_dict:
			city_corpus_dict[word]=1
		    else:
			previous = city_corpus_dict[word]
			city_corpus_dict[word] = previous+1
	    n[city.name] = city_corpus_dict
	d = Container(key=key, value=json.dumps(n))
	model.session.add(d)
	model.session.commit()
    else:
	n = json.loads(n.value)
    return n

#Memcaches key:city to value:total word count in city. Good use of Memcached because total word count of city stays constant for every call of function P(W/city) 
def create_city_word_count(city):
    key = city.name.replace(" ", "_")
    total_city_count = cache.get(key)
    if total_city_count is None:
	print "Missed the cache tota_city_count: %s" %  key
	container = city_corpus_dict()
	word_count_dict = container[city.name] 
	words = word_count_dict.keys()
	total_city_count = 0.0
	for word in words:
	    total_city_count += word_count_dict[word] 
	cache.set(key, total_city_count, timeout=5*60)
    return total_city_count 

#Returns total word count for all cities combined
def create_total_word_count():
    container = city_corpus_dict() 
    city_names = container.keys()
    total_count = 0.0
    for city_name in city_names:
	word_count_dict = container[city_name] 
	words = word_count_dict.keys()
	for word in words:
	    total_count += word_count_dict[word] 
    return float(total_count) 

#Returns the # of total tweets in a city- Called when calculating Mutual Information Scores N10, N00, N01, N11
def create_region_tweet_count(city):
    key = city.name.replace(' ', '_') + 'tweet_count'
    region_tweet_count = session.query(Container).filter(Container.key==key).first()
    if not region_tweet_count:
	tweet_to_cty_dict = map_cities_to_tweets()
	tweet_list = tweet_to_cty_dict[city.name]
	region_tweet_count = 0.0
	for tweet in tweet_list:
	    region_tweet_count += 1.0
	d = Container(key=key, value=json.dumps(region_tweet_count))
	model.session.add(d)
	model.session.commit()
    else:
	region_tweet_count = json.loads(region_tweet_count.value)
    return region_tweet_count 

#Returns the # of total tweets overall- Called when calculating Mutual Information Scores N10, N00, N01, N11
def create_tweet_total_count():
    key = 'total_tweet_count' 
    total_tweet_count = session.query(Container).filter(Container.key==key).first()
    if not total_tweet_count:
	tweet_to_cty_dict = map_cities_to_tweets()
	total_tweet_count = 0.0
	for city in cities:
	    tweet_list = tweet_to_cty_dict[city.name]
	    for tweet in tweet_list:
		total_tweet_count += 1.0
	d = Container(key=key, value=json.dumps(total_tweet_count))
	model.session.add(d)
	model.session.commit()
    else:
	total_tweet_count = json.loads(total_tweet_count.value) 
    return total_tweet_count

# P(W/City) = Number of times the word occurs in the city / total word count for the city. To do smoothing, then add 1 to the numerator and add len(corpus) to denominator.
def prob_word_given_city(city, word):
     
    number_times_word_in_city = find_count_of_word_in_city(city,word)
    count_city_word_total = create_city_word_count(city)
    leng_city_corpus = find_leng_city_corpus(city)
    prob_w_given_c = (number_times_word_in_city +1.0)/(count_city_word_total + leng_city_corpus)
    return float(prob_w_given_c)

#Memcaches number of unique word entries in a city corpus 
def find_leng_city_corpus(city):
    key = 'city_corpus_length' + city.name.replace(" ", "_")
    city_corpus_length = cache.get(key)
    if not city_corpus_length:
	print 'Missed the cache Recomputing city_corpus_length'
	cty_corpus_dict = city_corpus_dict()
	dic = cty_corpus_dict[city.name]
	city_corpus_length = len(dic.keys())
	cache.set(key, city_corpus_length, timeout=5*60)
    return city_corpus_length

#Finds number of unique word entries in total
def find_leng_total_corpus():
    length = 0.0
    uniques = set()
    cty_corpus_dict = city_corpus_dict()
    for city in cities:
	dic = cty_corpus_dict[city.name]
	uniques |= set(dic.keys())
    return float(len(uniques))
	    
#P(City)- We will assume that the likelihood correlates to how well represented the city is in the whole sample size
def prob_city_overall(city):
    number_city_tweets = create_region_tweet_count(city)
    number_total_tweets = create_tweet_total_count()
    p = number_city_tweets/number_total_tweets
    return float(p)

#P(Not-City) = 1 - P(City)- Not called in relative formula
#def prob_not_city(city):
#    p = float(1.0 - prob_city_overall(city))
#    return float(p) 

#Memcaches number of times a word occurs in a city's corpus 
def find_count_of_word_in_city(city, word):
    #key = word+city.name.replace(" ", "_")
    #count_of_word = cache.get(key)
    #if not count_of_word:
#	print "Missed the cache of count_of_word: %s" % key
    cty_corpus_dict = city_corpus_dict()
    dic = cty_corpus_dict[city.name]
    count_of_word = dic.get(word, 0)
#	count_of_word = dic.get(word, 0)
#	try:
#	    cache.set(key, count_of_word, timeout=5*60)
#	except Exception:
#	    pass
    return float(count_of_word) 


#Find number of times a word occurs total
def find_count_of_word_total(word):
    word = str(word)
    tweet_to_cty_dict = map_cities_to_tweets()
    for city in cities:
	tweet_list = tweet_to_city_dict[city.name]
	for tweet in tweet_list:
	    for item in tweet.text.encode("utf-8").lower().translate(string.maketrans("",""),string.punctuation).split():
		if item==word:
		    count+=1.0
    return float(count) 

#NOT CALLED in relative formula
# P(W/NC)= (Total number of times 'word' occurs outside of the city + 1)/ (total word count for those cities + len(total_corpus))
#def prob_word_given_not_city(city,word):
#       
#   count_of_word_outside_city = find_count_of_word_total(word) - find_count_of_word_in_city(city,word) + 1
#   length_tot_cor = find_length_total_corpus()
#   length_cty_cop = find_length_city_corpus()
#   total_nc_word_count = create_total_word_count() - create_city_word_count() + (length_tot_cor - length_cty_cop)
#   prob_w_given_nc = count_of_word_outside_city/total_nc_word_count
#   return float(prob_w_given_nc)

#cumulative P(City/Word)-- would take from above 4 functions, but is relative to P(City)*P(w1/City)*P(w2/City)... corrected with log to account for rare words
#Not called since it is relative to ^
#def prob_city_given_word(city,word):
#    prob_word_given_c = prob_word_given_city(city,word)
#    prob_city = prob_city_overall(city)
#    prob_word_given_not_c = prob_word_given_not_city(city,word)
#    prob_not_c = prob_not_city(city)

#    prob_city_given_word = (prob_word_given_c*prob_city)/(prob_word_given_c*prob_city+prob_word_given_not_c*prob_not_c)
#    return float(prob_city_given_word) 

#final formula for Prob(City/Tweet)-- puting together components from two function below this.p = (p1p2..pn)/(p1p2..pn+(1-p1)(1-p2)..(1-pn)) 
#CHANGED to log(P(City)+log(P(w1/City)+log(P(w2/City))...

def prob_tweet_from_city(city,tweet_string):
    total_start = datetime.datetime.now()
    stop_words = {'in':1, 'how':1,'his':1, 'took':1, 'could':1, 'would':1, 'will':1, 'at':1, 'should':1, 'can':1, 'we':1, 'us':1, 'as':1,'at':1, 'him':1,'to':1,'sometimes':1, 'you':1, 'were':1, 'i':1, 'my':1, 'her':1, 'he':1,'me':1, 'this':1, 'was':1, 'had':1,'all':1, 'the':1, 'but':1, 'or':1, 'and':1,'there':1, 'it':1, 'is':1, 'then':1, 'a':1, 'an':1, 'be':1, 'for':1, 'of':1, 'what':1, 'when':1, 'why':1, 'where':1, 'are':1, 'am':1, 'because':1, 'they':1,'she':1, 'he':1}
    x = 0
    num_queries = 0
    total_time = datetime.timedelta()
    tweet_words = tweet_string.encode("utf-8").lower().translate(string.maketrans("",""),string.punctuation).split()
    for word in tweet_words:
	if word not in stop_words:
	    num_queries += 1
	    start = datetime.datetime.now()
	    word_instance  = session.query(Word).filter(Word.word==word).filter( Word.city==city.name).first()
	    end = datetime.datetime.now()
	    time = (end - start)
	    total_time += time
	    if not word_instance:
		prob_w_given_c = prob_word_given_city(city, word)
	    else:
		prob_w_given_c = word_instance.probability
	    x += math.log(prob_w_given_c)
    prob_city_given_tweet_relative_to = math.log(prob_city_overall(city)) + x
    total_end = datetime.datetime.now()
    print 'It took %s to run %s queries' % (total_time, num_queries)
    print 'It took %s to calculate %s' % ((total_end - total_start), city.name)
    return float(prob_city_given_tweet_relative_to)

#Creates a list of city, probability-tweet-from-city pairs. Relative probabilities for each city
def create_list_of_probs(tweet_string):
    new_list = []
    for city in cities:
	tu = (city, prob_tweet_from_city(city, tweet_string))
	new_list.append(tu)
    return new_list

#Sorts list of tuples (city, probability-tweet-from-city) by probability in descending order
def create_ranking(tweet_string):
    probs = create_list_of_probs(tweet_string)
    probs.sort(key=operator.itemgetter(1), reverse=True)
    x = probs
    return x

def main():
    pass
if __name__ == "__main__":
    main()
