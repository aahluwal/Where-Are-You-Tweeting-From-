Where-Are-You-Tweeting-From-
============================

Use of Naiive Bayes Text Classification and Mutual Information Feature selection to predict from what major city region a twitter user is tweeting 

I created an automated script to gather tweets with known longitudes/latitudes using Twitter's Streaming API over the course of 4 weeks to create a random sample set.

I filtered them down to 9 major city regions: Los Angeles, San Francisco, Boston, New York, Chicago, Seattle, Atlanta, Houston, and Miami, 
and I mapped the results on Google Maps using the Fusion Table API.

I used documentation from http://nlp.stanford.edu/IR-book/html/htmledition/mutual-information-1.html to implement Mutual Information
to find each regions most significant "features" or words.

I used documentation from http://nlp.stanford.edu/IR-book/html/htmledition/naive-bayes-text-classification-1.html to implement a 
Naive Bayes Text classifier that can predict where a tweet with an unknown longitude/latitude is from, based on an
analysis of past tweets.  The classifier tokenizes a user's input/tweet, and assigns a weighted value (Probability of a word, given a city) 
to every word in the input. The classifier also takes into account the sample set of a given region, and finally ranks each city-- making the winner
the final prediction.  

I used the results from applying Mutual Information to better communicate to the user how a prediction was made.
When you hover over a city amongst the rankings, a user can see if/what words from their tweet are significant words to 
what city regions.  

The link to the final project online is where-are-you-tweeting-from.herokuapp.com

