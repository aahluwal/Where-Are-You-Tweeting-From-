import math

trending_list = ["#unpopularopinion i hate it so much when some of u call eleanor a beard or say her 'contract is over' she hasnt done anything bad i like her", "#unpopularopinion I love taylor swift and her music but I'm mad that she's become so different and obsessed with her image", "#unpopularopinion i honestly dont think management are that bad and people need to stop blaming them for everything that goes wrong hate taylor swift"]

non_trending_list = ["Happiness comes from sunshine and eating Bi-Rite cookies.", "With j2h. @ Mission Dolores Park http://instagram.com/p/X5n2VssQr6/", "Also, is there so little news in the world that Vanity Fair is doing profiles of motherfucker's iPhones? That editor should be fired. hate taylor swift"]



# Probability that a word is trending
def word_prob(word):
    word = word.lower()
    trend_corpus = " ".join(trending_list).lower().split()
    non_trend_corpus = " ".join(non_trending_list).lower().split()
    trend_size = len(trend_corpus)
    non_trend_size = len(non_trend_corpus)
    p_trend = float(trend_size)/(trend_size + non_trend_size)
    p_word = float(trend_corpus.count(word))/trend_size

    p_non_trend = 1.0 - p_trend
    p_word_non_trend = float(non_trend_corpus.count(word))/non_trend_size 

    return (p_trend * p_word)/(p_trend*p_word + p_non_trend*p_word_non_trend)

def phrase_bayes(sentence):
    words = sentence.split()
    probs = [ word_prob(word) for word in words ]
    print probs

    #eta = [ math.log(1.0-prob) - math.log(prob) for prob in probs ]
    try:
	eta = sum([ math.log(1-prob) - math.log(prob) for prob in probs ])
    except:
	return 1
    total_prob = 1.0/(1 + math.exp(eta))
    return total_prob



def create_trend_dict(list):
    trend_dict= {}
    for tweet in trending_list:
	word_list = tweet.split()
        for word in word_list:
            if word not in trend_dict:
	        trend_dict[word] = 1
	    else:
                previous_value = trend_dict[word]
                new_value = previous_value + 1
                trend_dict[word] = new_value 
    return trend_dict 

def create_non_trend_dict(list):
    non_trend_dict = {}
    for tweet in non_trending_list:
	word_list = tweet.split()       
	for word in word_list:
	    if word not in non_trend_dict:
	        non_trend_dict[word] = 1
	    else:
                previous_value = non_trend_dict[word]
                new_value = previous_value + 1
                non_trend_dict[word] = new_value 
    return non_trend_dict

def find_count_of_occurrences_in_dict(dict):
    list = dict.values()
    count = 0
    for num in list:
	count += num 
    return count 


def find_probability_that_word_occurs_given_type_set(word, dict_tested_word_is_in, count_of_words_in_set_1, count_of_words_in_set_2):
    prob = 0
    if word in dict_tested_word_is_in:
	prob = ((dict_tested_word_is_in.get(word)/count_of_words_in_set_1)*(count_of_words_in_set_1/(count_of_words_in_set_1+count_of_words_in_set_2)))/((dict_tested_word_is_in.get(word)/(count_of_words_in_set_1+count_of_words_in_set_2)))
    return prob


def main():
    print word_prob("bad")
    print word_prob("with")
    print phrase_bayes("hate taylor swift")
    print phrase_bayes("hate taylor swift")

    #trend_dict = create_trend_dict(trending_list)
    #non_trend_dict = create_non_trend_dict(non_trending_list)
    #count_of_trend = find_count_of_occurrences_in_dict(trend_dict)
    #count_of_non_trend = find_count_of_occurrences_in_dict(non_trend_dict)
    #print count_of_trend
    #print count_of_non_trend
    #word = "#unpopularopinion"
    #probability = find_probability_that_word_occurs_given_type_set(word, trend_dict, count_of_trend, count_of_non_trend) 

if __name__ == "__main__":
    main()
