from model import Tweet, Chicago, Los_Angeles, San_Francisco, Houston, Atlanta, New_York, Seattle, Miami
from math import sqrt, log
import math
import model
import string
from data import los_angeles, chicago, san_francisco, new_york, miami, atlanta, houston, seattle
import data 

#
def final_n_formula(city, word):
    #Functions to get list of US tweets, and know exact number of US tweets
    tweet_list_total = data.get_tweet_list()
    #N
    N = float(len(tweet_list_total))
    print "Number tweets total: %s" % (N)

    #Functions to isolate a city's tweet list. 
    tweet_city_dict = data.map_cities_to_tweets()
    tweet_city_list = tweet_city_dict[city]
    
    #N1_dot = number of all tweets that contain the word 
    count2 = 0.0
    for city in tweet_city_dict.keys():
	tweet_list = tweet_city_dict[city]
	for tweet in tweet_list:
	    tweet_words = tweet.text.encode("utf-8").lower().translate(string.maketrans("",""),string.punctuation).split()
	    if word in tweet_words:
		count2 += 1.0
    N1_dot = count2
    print "number of all tweets containing word: %s" % (N1_dot)

    #N.1= all tweets in city
    N_dot_1 = len(tweet_city_list)
    print "Number tweets in city: %s" % (N_dot_1)

    #N.0 = N1_dot + N0_dot = all tweets not in city 
    x = N - N_dot_1
    N_dot_0 = float(x)
    print "Number tweets not in city: %s" % (N_dot_0)

    #N11 = number of tweets in city that contain word 
    count1= 0.0
    for tweet in tweet_city_list:
	tweet_words = tweet.text.encode("utf-8").lower().translate(string.maketrans("",""),string.punctuation).split()
	if word in tweet_words:
	    count1 += 1.0
    N11 = count1	    
    print " number tweets in city with word: %s" % (N11)
    
    #N10 = Number of tweets containing the term not in the city 
    N10 = float(N1_dot - N11)
    print "num tweets containing term not in city: %s" % (N10)
   
    
    #N00= tweets not containing word and not in city 
    N00 = float(N_dot_0 - N10)
    print "tweets not containing word and not in city: %s" % (N00)

    #N01 = tweets don't contain term and in city
    N01 = float(N_dot_1 - N11)
    print "tweets not containing word and not in city: %s" % (N01)

    #N0_dot = tweets that don't contain the word 
    N0_dot = float(N01 + N00) 
    print "count tweets not in city with no word %s" % (N0_dot)

    #final formula = (N_dot_1(log2(N_dot_10/N1_dotN_dot_1)) + ((((N_dot_1/N)log2(NN_dot_1/(N0_dotN_dot_1))))/ ((N1_dot/N)log2(N_dot_10/(N1_dotN.0)))) + ...
    

    first_log_value = float((N*N11)/(N1_dot*N_dot_1))
    print "first log value: %s" % (first_log_value)

    second_log_value = float((N*N01)/(N0_dot*N_dot_1))
    print "second_log_value: %s" % (second_log_value)

    third_log_value = float((N*N10)/(N1_dot*N_dot_0))
    print "third_log_value: %s" % (third_log_value)

    fourth_log_value = float((N*N00)/(N0_dot*N_dot_0))
    print "fourth log value: %s" % (fourth_log_value) 


    part1 = float(N11/N)*(math.log(first_log_value,2))
    print "part 1: %s" % (part1)

    part2 = float(N01/N)*math.log(second_log_value,2)
    print "part2: %s" % (part2)

    part3 = float(N10/N)*math.log(third_log_value,2)
    print "part3: %s" % (part3)

    part4 = float(N00/N)*math.log(fourth_log_value,2) 
    print "part4: %s" % (part4)

    final = float(part1+part2+part3+part4) 
    print "final: %s" % (final)
    
    return final



def pick_top_five_features_in_city(city):
    city_corpus = data.city_corpus_dict()
    word_dict = city_corpus[city]
    feature_weight_list = []
    for word in word_dict.keys():
	p = final_n_formula(city, word)
	feature_weight_list.append((word, p))
    feature_weight_list.sort(key=operator.itemgetter(1))
    winner_list = []
    for i in range(0, 5):
	winner_list.append(feature_weight_list[i])
    return winner_list 

	


    

	

def main():
    winners= pick_top_five_features_in_city(los_angeles)
    print winners
    

    
if __name__ == "__main__":
    main()
