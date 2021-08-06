import tweepy
import logging
import time
import os
from os import environ
from datetime import datetime, timedelta


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def create_api():
    CONSUMER_KEY = environ['CONSUMER_KEY']
    CONSUMER_SECRET = environ['CONSUMER_SECRET']
    ACCESS_KEY = environ['ACCESS_KEY']
    ACCESS_SECRET = environ['ACCESS_SECRET']
    auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY,ACCESS_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e
    logger.info("API created")
    return api


api = create_api()


def fav_retweet(api):
    logger.info("Retrieving tweets...")
    mentions = api.mentions_timeline(tweet_mode="extended")
    for mention in reversed(mentions):
        if mention.in_reply_to_status_id is not None or mention.user.id == api.me().id:
            # This tweet is a reply or I'm its author so, ignore it
            return

        if not mention.favorited:
            # Mark it as Liked, since we have not done it yet
            try:
                mention.favorite()
                logger.info(f"Liked tweet by {mention.user.name}")
            except Exception as e:
                logger.error("Error on fav", exc_info=True)

        if not mention.retweeted:
            # Retweet, since we have not retweeted it yet
            try:
                mention.retweet()
                time.sleep(60)
                logger.info(f"Retweeted tweet by {mention.user.name}")
            except Exception as e:
                logger.error("Error on fav and retweet", exc_info=True)


def follow_followers(api):
    logger.info("Retrieving and following followers")
    for follower in tweepy.Cursor(api.followers).items():
        if not follower.following:
            try:
                follower.follow()
                time.sleep(70)
                logger.info(f"Following {follower.name}")
            except tweepy.error.TweepError:
                pass


def retweet_tweets_with_hashtag(api, need_hashtags):
    if type(need_hashtags) is list:
        search_query = f"{need_hashtags} -filter:retweets"
        tweets = api.search(q=search_query, lang="en", tweet_mode="extended")
        for tweet in tweets:
            hashtags = [
                i["text"].lower() for i in tweet.__dict__["entities"]["hashtags"]
            ]
            try:
                need_hashtags = [hashtag.strip("#") for hashtag in need_hashtags]
                need_hashtags = list(need_hashtags)
                if set(hashtags) & set(need_hashtags):
                    if tweet.user.id != api.me().id:
                        api.retweet(tweet.id)
                        tweet.favorite()
                        logger.info(f"Retweeted tweet from {tweet.user.name}")
                        time.sleep(65)
            except tweepy.TweepError:
                logger.error("Error on retweet", exc_info=True)
    else:
        logger.error("Hashtag search terms needs to be of type list", exc_info=True)
        return


while True:
    follow_followers(api)
    time.sleep(25)
    retweet_tweets_with_hashtag(api, ["#smallstreamer"])
    logger.info("Waiting 1 ...")
    time.sleep(30)
    fav_retweet(api)
    logger.info("Waiting 2 ...")
    time.sleep(30)

