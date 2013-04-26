import data
from data import cities

def main():
    data.city_word_prob_dict()
    data.city_tweet_corpus_dict()
    data.city_corpus_dict()
    for city in cities:
	data.create_region_tweet_count(city)
    data.create_tweet_total_count()
if __name__ == "__main__":
        main()
