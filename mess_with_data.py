# Messing with data.py 


from model import session, Tweet, San_Francisco, Los_Angeles, Houston, New_York, Atlanta, Chicago, Miami, Seattle
from math import sqrt, log
import math
import model
from sklearn import feature_selection
import string

#global instances
los_angeles = Los_Angeles()
san_francisco = San_Francisco()
houston = Houston()
miami = Miami()
atlanta = Atlanta()
new_york = New_York()
seattle = Seattle()
chicago = Chicago()
cities = [los_angeles, san_francisco, houston, miami, atlanta, new_york, chicago, seattle]
CITY_TWEET_MAP = None

#returns list of US tweets
def get_tweet_list():
    all_tweets = session.query(Tweet).filter(Tweet.longitude > -125.0).filter(Tweet.longitude < -65.0).filter(Tweet.latitude > 25.0).filter(Tweet.latitude < 50.0).all()
    list_of_tweets = []
    for tweet in all_tweets:
	if tweet.text.startswith("RT"):
	    continue
	else:
#	    decoded_tweet = tweet.__repr__().decode("latin-1")
	    list_of_tweets.append(tweet)
    return list_of_tweets 

#pythagorean theorem to calculate closest city
def distance_between_2_points(start, end):
    lon1, lat1 = start
    lon2, lat2 = end
    dlon = lon2-lon1
    dlat = lat2-lat1
    distance = sqrt(((dlon)*(dlon))+((dlat)*(dlat)))
    return float(distance)

#returns list of closest cities that correspond to index of tweets
def closest_major_cities(list_of_tweets):
    tweet_cities = []
    for tweet in list_of_tweets:
	closest_city = cities[0]
	for i in range(1, len(cities)):
	    new_city = cities[i]
	    if distance_between_2_points((closest_city.lon, closest_city.lat),(tweet.longitude,tweet.latitude)) > distance_between_2_points((new_city.lon, new_city.lat), (tweet.longitude,tweet.latitude)):
		closest_city = new_city 
	tweet_cities.append(closest_city)
    return tweet_cities

#returns dictionary with cities/instances as keys and values of lists of the corresponding tweets 
def map_cities_to_tweets():
    global CITY_TWEET_MAP
    if CITY_TWEET_MAP:
	return CITY_TWEET_MAP
    list_of_us_tweets = get_tweet_list()
    major_cities = closest_major_cities(list_of_us_tweets)
    tweet_to_city_dict = {}
    for i in range(0, len(major_cities)):
	tweet = list_of_us_tweets[i]
	city = major_cities[i]
	if city not in tweet_to_city_dict:
	    tweet_to_city_dict[city] = [tweet]
	else:
	    previous = tweet_to_city_dict[city]
	    tweet_to_city_dict[city] = tweet_to_city_dict[city] + [tweet] 
    CITY_TWEET_MAP = tweet_to_city_dict
    return tweet_to_city_dict 



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


# CHANGED TO: P(W/City) = Number of times the word occurs in the city / total word count for the city. To do smoothing, then add 1 to the numerator and add len(corpus) to denominator.
def prob_word_given_city(city, word):
    number_times_word_in_city = find_count_of_word_in_city(city,word)
    count_city_word_total = create_city_word_count(city)
    leng_city_corpus = find_leng_city_corpus(city)
    prob_w_given_c = (number_times_word_in_city +1.0)/(count_city_word_total + leng_city_corpus)
    print 'Probability of %s given %s: %s' % (
	    word,
	    city.name,
	    prob_w_given_c)
    debug_data = {}
    debug_data['times_word_in_city'] = number_times_word_in_city
    debug_data['count_city_word_total'] = count_city_word_total
    debug_data['leng_city_corpus'] = leng_city_corpus
    print debug_data
    return float(prob_w_given_c)

#Finds number of unique word entries in a city corpus 
def find_leng_city_corpus(city):
    cty_corpus_dict = city_corpus_dict()
    dic = cty_corpus_dict[city]
    leng_city_corpus = len(dic.keys())
    return leng_city_corpus

#Finds number of unique word entries in total
def find_leng_total_corpus():
    length = 0.0
    cty_corpus_dict = city_corpus_dict()
    for city in cities:
	dic = cty_corpus_dict[city]
	length += len(dic.keys())
    return float(length)
	    
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
    count = 1
    for city in cities:
	tweet_list = tweet_to_cty_dict[city]
	for tweet in tweet_list:
	    for item in tweet.text.encode("utf-8").lower().translate(string.maketrans("",""),string.punctuation).split():
		if item==word:
		    count+=1.0
    return float(count) 

#NotCalled in relative formula
#P(W/Not-City) = We divide the difference between # of tweets total containing word and # of tweets in city containing word by difference between # of total tweets and # of tweets in city.
#   Ultimately means dividing # of tweets that contain the word but are not in the city, by the # of tweets total that are not in the city  
# CHANGED FROM: (Total number of times 'word' occurs outside of the city + 1)/ (total word count for those cities + len(total_corpus))
def prob_word_given_not_city(city,word):
    

    
   count_of_word_outside_city = find_count_of_word_total(word) - find_count_of_word_in_city(city,word) + 1
   length_tot_cor = find_leng_total_corpus()
   length_cty_cop = find_leng_city_corpus(city)
   total_nc_word_count = create_total_word_count() - create_city_word_count(city) + (length_tot_cor - length_cty_cop)
   prob_w_given_nc = count_of_word_outside_city/total_nc_word_count
   return float(prob_w_given_nc)

#cumulative P(City/Word)-- would take from above 4 functions, but is relative to P(City)*P(w1/City)*P(w2/City)... corrected with log to account for rare words
#Not called since it is relative to ^
def prob_city_given_word(city,word):
    prob_word_given_c = prob_word_given_city(city,word)
    prob_city = prob_city_overall(city)
    prob_word_given_not_c = prob_word_given_not_city(city,word)
    prob_not_c = prob_not_city(city)

    prob_city_given_word = (prob_word_given_c*prob_city)/(prob_word_given_c*prob_city+prob_word_given_not_c*prob_not_c)
    return float(prob_city_given_word) 

#P(C/Tweet)
#new formula to deal with underflow
def prob_tweet_from_city(city,tweet_string):
    tweet_words = tweet_string.encode("utf-8").lower().translate(string.maketrans("",""),string.punctuation).split()
    probs= [prob_city_given_word(city,word) for word in tweet_words]
    eta = sum([math.log(1.0-prob)-math.log(prob) for prob in probs]) 
    total_prob = 1.0/(1.0 + math.exp(eta))
    return total_prob 



def choose_amongst_cities(tweet_string):
    winner = (cities[0].name, prob_tweet_from_city(cities[0], tweet_string))
    prob_winner = winner[1]
    for i in range(1, len(cities)):
	prob_from_this_city = prob_tweet_from_city(cities[i], tweet_string)
	if prob_from_this_city > prob_winner:
	    prob_winner = prob_from_this_city
	    winner = (cities[i].name, prob_from_this_city)
    return winner

def print_all_amongst_cities(tweet_string):
    city_probs = []
    for i in range(0, len(cities)):
	city_probs.append((cities[i].name, prob_tweet_from_city(cities[i], tweet_string)))
    return city_probs






#below were functions designed to fit sklearn toolkit
def find_feature_label_list():
    corpus_feature_label_list = []
    d = map_cities_to_tweets()
    cities = d.keys()
    for city in cities:
	tweet_object_list = d[city]
	for tweet in tweet_object_list:
	    tweet_string = tweet.text.encode("utf-8").lower()
	    no_punc_string = tweet_string.translate(string.maketrans("",""),string.punctuation)
	    word_list = no_punc_string.split()
	    for word in word_list:
		if word not in corpus_feature_label_list:
		    corpus_feature_label_list.append(word) 
    return corpus_feature_label_list


def create_feature_vector(text,corpus_list):
    text_vector = [0]*len(corpus_list)
    word_list = text.encode("utf-8").split()
    for i in range(0,len(word_list)):
	for j in range(0, len(corpus_list)):
	    if word_list[i] == corpus_list[j]:
		text_vector[j] += 1
    return text_vector 


def create_feature_matrix():
    feature_matrix = []
    d = map_cities_to_tweets()
    cities = d.keys()
    corpus_list = find_feature_label_list()
    print corpus_list
    labels_list = []
    for city in cities:
	tweets = d[city]
	for tweet in tweets:
	    vector = create_feature_vector(tweet.text,corpus_list)
	    feature_matrix.append(vector)
	    labels_list.append(city.name)
    return feature_matrix, labels_list, corpus_list

corpus = None
def main():
    global corpus
   # feature_matrix, labels_list, corpus_list = create_feature_matrix()
   # c2, pvals = feature_selection.chi2(feature_matrix, labels_list)
   # print c2
   # n_greatest = sorted(range(len(c2)), key=lambda i: c2[i])[-20:]
   # for idx in n_greatest:
#	print idx
#	print corpus_list[idx]
#	print ''
   # print p
    #p = choose_amongst_cities("beach party warm")
    #print p
   # q = print_all_amongst_cities("New York City for Life!")
   # print q
    #tweets = city_corpus_dict().items()
    #ny = tweets[0]
    #print ny[1]

    
    p = choose_amongst_cities("party")
    print p
    q = print_all_amongst_cities("party")
    print q
if __name__ == "__main__":
    main()
