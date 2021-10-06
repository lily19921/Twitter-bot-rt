import tweepy
import time 
import os
from os import environ
CONSUMER_KEY = environ['CONSUMER_KEY']
CONSUMER_SECRET = environ['CONSUMER_SECRET']
ACCESS_KEY = environ['ACCESS_KEY']
ACCESS_SECRET = environ['ACCESS_SECRET']
auth = tweepy.OAuthHandler('CONSUMER_KEY','CONSUMER_SECRET')
auth.set_access_token('ACCESS_KEY','ACCESS_SECRET')
api=tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
user=api.me()
search='@Liliaa_rt'
nrTweets=500


for tweet in tweepy.Cursor(api.search, search).items(nrTweets):
    try :
        print('Tweet Liked')
        tweet.retweet()
        tweet.favorite()
        time.sleep(60)
    except tweepy.TweepError as e:
        print(e.reason)
    except StopIteration:
        break
