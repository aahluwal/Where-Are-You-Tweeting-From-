import sys
import tweepy
import json

consumer_key="Q5LGEcvSRFHZq97EzU7FQ"
consumer_secret="sdZeJGtXHSgxN8ALs5xgpaTn2SSn4jxqqWjnHUPhn0"
access_key="1278869893-NRPD3OYMKJDdpYRqRiTpFMBhdKhXcxoDVc3Yj11"
access_secret="Bi43mEBzojlUHyKIG44JW8dhqRdLj0nM1Qquy4DOCPI"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

class CustomStreamListener(tweepy.StreamListener):
	
    def __init__(self):
        super(CustomStreamListener, self).__init__()
        self.num_read = 0

    def on_status(self, status):
	if status.geo:
	    with open('tweet_data_json_12.txt', 'a') as outfile:
		output = {}
		output['screen_name'] = status.author.screen_name
		output['coordinates'] = status.coordinates
		output['text'] = status.text
		output['created_at'] = status.created_at.strftime('%Y-%m-%dT%H:%M:%S')
                outfile.write(json.dumps(output))
		
	if self.num_read > 14000:
	    exit()
	self.num_read += 1
	
    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
	return True # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
	return True # Don't kill the stream

sapi = tweepy.streaming.Stream(auth, CustomStreamListener())
sapi.sample()
print 'done' 

