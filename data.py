from model import session, Tweet, Boston, San_Francisco, Los_Angeles, Houston, New_York, Atlanta, Chicago, Miami, Seattle
from math import sqrt, log, sin, cos, radians, atan2
import math
import model
import string
import operator
import haversine
from operator import itemgetter 

# Main Naiive Bayes classification equation derived from http://nlp.stanford.edu/IR-book/html/htmledition/naive-bayes-text-classification-1.html
#This paper says that P(Document/Class) AKA P(Tweet/City) is relative to P(City)*P(Word1/CITY)*P(Word2/CITY)*...*P(Wordn/CITY). I calculate this for every City and rank 
#the cities to see which city a tweet most likely came from

#global instances
los_angeles = Los_Angeles()
san_francisco = San_Francisco()
houston = Houston()
miami = Miami()
atlanta = Atlanta()
new_york = New_York()
seattle = Seattle()
chicago = Chicago()
boston = Boston()
cities = [los_angeles, san_francisco, houston, miami, atlanta, new_york, chicago, seattle, boston]

def cosrad(n):
    return math.cos(math.radians(n))

#Limit tweet results to be within 100 miles/161km of a major city
def distanceIsWithinHundredMiles(lon1,lat1,lon2,lat2):
    d = haversine.haversine(lon1, lat1, lon2, lat2)
    if d < 240:
	return True
    else:
	return False 


#returns list of US tweets
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
    return ALL_TWEETS


#pythagorean theorem to calculate closest city in km
def distance_between_2_points((lon1, lat1),(lon2, lat2)):
    d = haversine.haversine(lon1, lat1, lon2, lat2)
    return float(d)

#Return list of tweets and their corresponding, closest city, given that the city is within 100 miles of the tweet 
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

#returns dictionary with cities/instances as keys and values of lists of the corresponding tweets 
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
	city = major_cities[i][1]
	if city not in tweet_to_city_dict:
	    tweet_to_city_dict[city] = [tweet]
	else:
	    previous = tweet_to_city_dict[city]
	    tweet_to_city_dict[city] = tweet_to_city_dict[city] + [tweet] 

    CITY_TWEET_MAP = tweet_to_city_dict
    return CITY_TWEET_MAP



# Begin Bayesian Problem

#creates a dictionary 'container' with city instances as keys and dictionaries of words from tweets as keys and counts as values
def city_corpus_dict():
    tweet_to_city_dict = map_cities_to_tweets()
    #city_keys = tweet_to_city_dict.keys()-- don't need this line bc cities list is global now
    container = {}
    for city in cities:
	city_corpus_dict = {}
	for tweet in tweet_to_city_dict[city]:
	    tweet_text = tweet.text.encode("utf-8").lower().translate(string.maketrans("",""),string.punctuation).split()
	    for word in tweet_text:
		if word not in city_corpus_dict:
		    city_corpus_dict[word]=1
		else:
		    previous = city_corpus_dict[word]
		    city_corpus_dict[word] = previous+1
	container[city] = city_corpus_dict
    return container 


#returns total count of all words in a city
def create_city_word_count(city):
    container = city_corpus_dict()
    word_count_dict = container[city] 
    words = word_count_dict.keys()
    total_count = 0.0
    for word in words:
	total_count += word_count_dict[word] 
    return float(total_count) 

#returns total word count for all cities combined
def create_total_word_count():
    container = city_corpus_dict() 
    cities = container.keys()
    total_count = 0.0
    for city in cities:
	word_count_dict = container[city] 
	words = word_count_dict.keys()
	for word in words:
	    total_count += word_count_dict[word] 
    return float(total_count) 

#returns the # of total tweets in a city- Never gets called
def create_region_tweet_count(city):
    tweet_to_cty_dict = map_cities_to_tweets()
    tweet_list = tweet_to_cty_dict[city]
    tweet_count = 0.0
    for tweet in tweet_list:
	tweet_count += 1.0
    return float(tweet_count) 

#returns the # of total tweets overall- Never gets called
def create_tweet_total_count():
    tweet_to_cty_dict = map_cities_to_tweets()
    #cities = tweet_to_city_dict.keys()-- don't need this bc cities is global list of city instances
    total_tweet_count = 0.0
    for city in cities:
	tweet_list = tweet_to_cty_dict[city]
	for tweet in tweet_list:
	    total_tweet_count += 1.0
    return float(total_tweet_count)

# P(W/City) = Number of times the word occurs in the city / total word count for the city. To do smoothing, then add 1 to the numerator and add len(corpus) to denominator.
def prob_word_given_city(city, word):
   
    number_times_word_in_city = find_count_of_word_in_city(city,word)
    count_city_word_total = create_city_word_count(city)
    leng_city_corpus = find_leng_city_corpus(city)
    prob_w_given_c = (number_times_word_in_city +1.0)/(count_city_word_total + leng_city_corpus)
    return float(prob_w_given_c)

#Finds number of unique word entries in a city corpus 
def find_leng_city_corpus(city):
    cty_corpus_dict = city_corpus_dict()
    dic = cty_corpus_dict[city]
    leng_city_corpus = len(dic.keys())
    return float(leng_city_corpus)

#Finds number of unique word entries in total
def find_leng_total_corpus():
    length = 0.0
    uniques = set()
    cty_corpus_dict = city_corpus_dict()
    for city in cities:
	dic = cty_corpus_dict[city]
	uniques |= set(dic.keys())
    return float(len(uniques))
	    
#P(City)- We will assume that the likelihood correlates to how well represented the city is in the whole sample size
def prob_city_overall(city):
    number_city_tweets = create_region_tweet_count(city)
    number_total_tweets = create_tweet_total_count()
    p = number_city_tweets/number_total_tweets
    return float(p)

#P(Not-City) = 1 - P(City)
def prob_not_city(city):
    p = float(1.0 - prob_city_overall(city))
    return float(p) 

#Finds number of times a word occurs in a city's corpus
def find_count_of_word_in_city(city, word):
    word = str(word)
    tweet_to_cty_dict = map_cities_to_tweets()
    tweet_list = tweet_to_cty_dict[city]
    count = 0.0
    for tweet in tweet_list:
	for item in tweet.text.encode("utf-8").lower().translate(string.maketrans("",""),string.punctuation).split():
	    if item==word:
		count+=1.0
    return float(count)

#Find number of times a word occurs total
def find_count_of_word_total(word):
    word = str(word)
    tweet_to_cty_dict = map_cities_to_tweets()
    for city in cities:
	tweet_list = tweet_to_city_dict[city]
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
    x = 0
    tweet_words = tweet_string.encode("utf-8").lower().translate(string.maketrans("",""),string.punctuation).split()
    for word in tweet_words:
	prob_w_given_c = prob_word_given_city(city, word)
	print 'P(w | c) = %s for (w: %s, c: %s)' % (
		prob_w_given_c,
		word,
		city.name)
	x += math.log(prob_w_given_c)
    prob_city_given_tweet_relative_to = math.log(prob_city_overall(city)) + x 
    return float(prob_city_given_tweet_relative_to)

#def find_best_city_match(tweet_string):
#    highest_fit_city = prob_tweet_from_city(cities[0], tweet_string)
#    for i in range(1,len(cities)):
#	if prob_tweet_from_city(cities[i],tweet_string) > highest_fit_city:
#	    highest_fit_city = prob_tweet_from_city(cities[i],tweet_string)
#   return  cities[i].name	

#Creates a list of relative probabilities for each City
def create_list_of_probs(tweet_string):
    new_list = []
    for city in cities:
	tu = (city, prob_tweet_from_city(city, tweet_string))
	new_list.append(tu)
    return new_list

#Chooses the highest relative probability amongst the cities
#def pick_winner(tweet_string):
#    new_list = create_list_of_probs(tweet_string)
#    x = (new_list[0][0], new_list[0][1])
#    for i in range(1, len(new_list)):
#	if new_list[i][1]  > x[1]:
#	    x = (new_list[i][0], new_list[i][1])
#    return x

#Sorts list of tuples (city, prob) by probability in descending order
def create_ranking(tweet_string):
    probs = create_list_of_probs(tweet_string)
    probs.sort(key=operator.itemgetter(1), reverse=True)
    x = probs
    return x

def main():

    #p = create_ranking("There's a party on the beach today")
    #print p
    g = map_cities_to_tweets()
    print g


if __name__ == "__main__":
    main()
