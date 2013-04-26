import model
import sqlalchemy.exc
import json 

def load_tweet_data(session):
    in_file = open("seed_data/seeded_files/tweet_data_json_17.txt")
    input_text = in_file.read()
    list_of_dicts = json.loads(input_text)
    for dict in list_of_dicts:
	tweet = model.Tweet.create_from_dict(dict)
	session.add(tweet)
	session.commit()
	
def load_tweet_from_python(session):
    f  = open("test.txt")
    text = f.read() 
    python_dicts = eval(text)
    for dict in python_dicts:
        tweet = model.Tweet.create_from_dict(dict)
	session.add(tweet)
	session.commit()

def main(session):
    load_tweet_data(session)
	

if __name__ == "__main__":
    s = model.session
    main(s)
