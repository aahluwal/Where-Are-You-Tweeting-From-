from model import Container,Tweet, Features, Boston, Chicago, Los_Angeles, San_Francisco, Houston, Atlanta, New_York, Seattle, Miami
import model
from math import sqrt, log
from operator import itemgetter
import math
import operator
import model
import haversine
import string
from data import cities, los_angeles, boston, chicago, houston, atlanta, new_york, seattle, miami, san_francisco
import data 
import json
# Main Mutual Information equation derived from http://nlp.stanford.edu/IR-book/html/htmledition/mutual-information-1.html
from app import db
session = db.session

#Helper function to get list of unique words
def get_corpus():
    corpus = {}
    city_to_dict_of_words_to_counts = data.city_corpus_dict()
    for city in cities:
	city_corpus = city_to_dict_of_words_to_counts[city.name]
	for word in city_corpus.keys():
	    corpus[word] = True
    return corpus.keys()

#N11: Tweets containing word and in city; N10: Tweets containing word and not in city; N00: Tweets not containing word, and not in city; N01: Tweets not containing wird and in the city.
def get_tweet_word_counts(word, city):
    city_tweet_corpus_dict = data.city_tweet_corpus_dict()
    word_tweet_count_dic = city_tweet_corpus_dict[city.name]
    N11 = word_tweet_count_dic.get(word,0)
    
    Ndot_1 = data.create_region_tweet_count(city)
    N01 = Ndot_1 - N11
    N = data.create_tweet_total_count()
    Ndot_0 = N - Ndot_1
    N1_dot = 0 
    for c in cities:
	tweet_corpus_d = city_tweet_corpus_dict[c.name]
	N1_dot += tweet_corpus_d.get(word, 0)
    N10 = N1_dot - N11 
    N00 = Ndot_0 - N10
    N0_dot = N00 + N01 

    return {
	    'N10': float(N10), 'N11': float(N11), 'N01': float(N01), 'N00': float(N00)}

#Creates an instance of the features class corresponding to a given city. Returns list of features (attribute of that features instance)
def get_hardcoded_features(city):
    feature_instance = model.session.query(Features).filter(Features.city_name==city.name).first()
    features = feature_instance.list_of_features() 
    features = features[:30]
    return features 

#Stores ranked list of words in the database 
def populate_db_with_features(city):
    feature_list =  rank(city)
       
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
    word_dict = city_corpus[city.name]
    feature_weight_list = []
    count = 0
    for word in word_dict.keys():
	wf = get_tweet_word_counts(word, city)
	score = mutual_info_score(wf['N11'], wf['N10'], wf['N01'], wf['N00'])
	feature_weight_list.append((word, score))
	count += 1
    feature_weight_list.sort(key=operator.itemgetter(1), reverse=True)
    winner_list = []
    feature_word_list = [t[0] for t in feature_weight_list]
    stop_words = {'every':1, 'got':1,'through':1,'our':1,'especially':1,'about':1,'before':1, 'between':1, 'by':1, 'during':1, 'except':1, 'for':1, 'with':1, 'without':1,'in':1, 'how':1,'his':1, 'took':1, 'could':1, 'would':1, 'will':1, 'at':1, 'should':1, 'can':1, 'we':1, 'us':1, 'as':1,'at':1, 'him':1,'to':1,'sometimes':1, 'you':1, 'were':1, 'i':1, 'my':1, 'her':1, 'he':1,'me':1, 'this':1, 'was':1, 'had':1,'all':1, 'the':1, 'but':1, 'or':1, 'and':1,'there':1, 'it':1, 'is':1, 'then':1, 'a':1, 'an':1, 'be':1, 'for':1, 'of':1, 'what':1, 'when':1, 'why':1, 'where':1, 'are':1, 'am':1, 'because':1, 'they':1}
    for word in feature_word_list:
	if word not in stop_words:
	    winner_list.append(word)
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
    if not N11 > 0:
	return float("-inf")
    if N11 > 0 and N1_dot > 0:
	first_log = (N11/N) * math.log((N*N11)/(N1_dot*Ndot_1), 2)
    else:
	first_log = 0
    return first_log + (N01/N) * math.log((N*N01)/(N0_dot*Ndot_1), 2) + third_log + (N00/N) * math.log((N*N00)/(N0_dot*Ndot_0), 2)

#Returns list of user words and their position in the ranked list of features features
def get_city_included_features(city, tweet_string):
    tweet_words = tweet_string.encode("utf-8").lower().translate(string.maketrans("",""),string.punctuation).split()
    uniques = set(tweet_words)
    tweet_words = list(uniques)
    features = model.session.query(Features).filter(Features.city_name==city.name).first()
    features = features.city_features
    features = json.loads(features)
    included_features = []
    for index, feature in enumerate(features):
	if feature in tweet_words:
	    included_features.append((feature.encode("utf-8"), index+1))
    return included_features

def included_feature_strings(city, tweet_string):
    features = get_city_included_features(city, tweet_string)
    feature_strings = []
    for feature in features:
	word_feature = feature[0]  
	feature_string = " is ranked number  ".join(['"%s"' % word_feature, str(feature[1])])
	feature_strings.append(feature_string)
    return feature_strings
	
        
#Returns dictionary of each city and their corresponding included_features list, given a tweet
def get_included_features_dict(tweet_string):
    included_features_dict = {}
    for city in cities:
	included_features_dict[city.name] = get_city_included_features(city,tweet_string)
    return included_features_dict


def main():
    m = get_tweet_word_counts("beach",miami)
    print "miami is %s" % m
    la = get_tweet_word_counts("beach", los_angeles)
    print "la is %s" % la
    ny = get_tweet_word_counts("beach", new_york)
    print "ny is %s" % ny
if __name__ == "__main__":
    main()

