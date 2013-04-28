import data
import feature_selection
from data import cities

#Before running this file:
#Upon reseeding DB tweets table with new data:
#DELETE from features, words, and containers tables. Note: I have set indexes on 'longitude' and 'latitude' in the tweets table, and on 'city' and 'word' 
    # from words table to increase speed in text classification 
#Call this file to repopulate those tables with up to date values 

def main(): 
    
    data.city_corpus_dict()
    #Creates city to word to prob(w/city) dict
    data.city_word_prob_dict()
    #seeds words table with city, word, prob(w/city)
    data.seed_words_table()
    data.city_tweet_corpus_dict()
    for city in cities:
	data.create_region_tweet_count(city)
	feature_selection.populate_db_with_features(city)
    data.create_tweet_total_count()

if __name__ == "__main__":
        main()
