from model import Tweet, Features, Boston, Chicago, Los_Angeles, San_Francisco, Houston, Atlanta, New_York, Seattle, Miami
import model
from math import sqrt, log
from operator import itemgetter
import math
import operator
import model
import haversine
import string
from data import cities
import data 
import json
# Main Mutual Information equation derived from http://nlp.stanford.edu/IR-book/html/htmledition/mutual-information-1.html

def get_corpus():
    corpus = {}
    city_to_dict_of_words_to_counts = data.city_corpus_dict()
    for city in cities:
	city_corpus = city_to_dict_of_words_to_counts[city]
	for word in city_corpus.keys():
	    corpus[word] = True
    return corpus.keys()

def get_tweet_word_counts(word, city):
    city_to_tweet_list_dict = data.map_cities_to_tweets()
    N1_dot = 0
    N = 0
    for c in cities:
	tweet_list = city_to_tweet_list_dict[c]
	for tweet in tweet_list:
	    if word in tweet.text.encode("utf-8").lower().translate(string.maketrans("",""),string.punctuation).split():
		N1_dot += 1
	    N += 1
	
    city_tweets = city_to_tweet_list_dict[city]
    N11 = 0
    Ndot_1 = 0
    for tweet in city_tweets:
	if word in tweet.text.encode("utf-8").lower().translate(string.maketrans("",""),string.punctuation).split():
	    N11 += 1
	Ndot_1 += 1
    N10 = N1_dot - N11
    N01 = Ndot_1 - N11
    N0_dot = N - N1_dot
    Ndot_0 = N - Ndot_1
    N00 = N0_dot - N01
    return {
	    'N10': float(N10), 'N11': float(N11), 'N01': float(N01), 'N00': float(N00)}
    """
    print "N: %s, N11: %s, N10: %s, N01: %s, N00: %s, N1.: %s, N0.: %s, N.1: %s, N.0: %s" % (
	    N,
	    N11,
	    N10,
	    N01,
	    N00,
	    N1_dot,
	    N0_dot,
	    Ndot_1,
	    Ndot_0)
    print mutual_info_score(float(N11), float(N10), float(N01), float(N00))
    """
#Creates an instance of the features class corresponding to a given city. Returns list of features (attribute of that features instance)
def get_hardcoded_features(city):
    feature_instance = model.session.query(Features).filter(Features.city_name==city.name).first()
    features = feature_instance.list_of_features() 
    return features 

#Stores ranked list of words in the database 
def populate_db_with_features(city):
    feature_list = [t[0] for t in rank(city)]
       
    features = json.dumps(feature_list)
    print features
    feature_instance = model.session.query(Features).filter(Features.city_name==city.name).first()
    if feature_instance:
	feature_instance.city_features=features
	model.session.add(feature_instance)
	model.session.commit()
    else:
	new_features = Features(city_features=features, city_name=city.name)
	model.session.add(new_features)
	model.session.commit()

def rank(city):
    city_corpus = data.city_corpus_dict()
    word_dict = city_corpus[city]
    feature_weight_list = []
    print 'num words to check'
    print len(word_dict.keys())
    count = 0
    for word in word_dict.keys():
	wf = get_tweet_word_counts(word, city)
	score = mutual_info_score(wf['N11'], wf['N10'], wf['N01'], wf['N00'])
	feature_weight_list.append((word, score))
	count += 1
    feature_weight_list.sort(key=operator.itemgetter(1), reverse=True)
    winner_list = feature_weight_list[:30]
    return winner_list 

def mutual_info_score(N11, N10, N01, N00):
    N1_dot = N11 + N10
    N0_dot = N01 + N00
    Ndot_1 = N11 + N01
    Ndot_0 = N10 + N00
    N = N10 + N11 + N01 + N00
    if N10 > 0 and N1_dot>0:
	third_log = (N10/N) * math.log((N*N10)/(N1_dot*Ndot_0), 2)
    else:
	third_log = 0
    if N11 > 0 and N1_dot > 0:
	first_log = (N11/N) * math.log((N*N11)/(N1_dot*Ndot_1), 2)
    else:
	first_log = 0
    return first_log + (N01/N) * math.log((N*N01)/(N0_dot*Ndot_1), 2) + third_log + (N00/N) * math.log((N*N00)/(N0_dot*Ndot_0), 2)

def top_words_in_tweet(city, tweet_string):
    tweet_words = tweet_string.encode("utf-8").lower().translate(string.maketrans("",""),string.punctuation).split()
    probs = []
    for word in tweet_words:
	wf = get_tweet_word_counts(word, city)
	score = mutual_info_score(wf['N11'], wf['N10'], wf['N01'], wf['N00'])
	probs.append((word, score))
    probs.sort(key=operator.itemgetter(1), reverse=True)
    words = [t[0] for t in probs]
    top_5_words = words[:5]
    return top_5_words

def main():
    counts = get_tweet_word_counts('nyc', new_york)
    print mutual_info_score(counts['N11'], counts['N10'], counts['N01'], counts['N00'])
    counts = get_tweet_word_counts('the', new_york)
    print mutual_info_score(counts['N11'], counts['N10'], counts['N01'], counts['N00'])
    print rank(boston)
if __name__ == "__main__":
    main()
