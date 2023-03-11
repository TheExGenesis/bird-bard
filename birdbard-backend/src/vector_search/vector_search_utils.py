# %%
BASE_PATH = "/Users/frsc/Documents/Projects/birdbard/birdBARD"
import sys
from typing import List

sys.path.append(BASE_PATH)
import datetime
import toolz.curried as tz
import pandas as pd
import json
import os

from src.topic_modelling.tz_utils import pick
from src.schema import Tweet, ArchiveTweet, VectorSearchTweet
from src.twitter_archive_to_db.archive_utils import load_archive_tweets, ARCHIVE_PATH

TWEET_KEYS_FOR_DF = [
    "id", 
    "full_text", 
    "created_at", 
    "favorite_count", 
    "retweet_count",
    "in_reply_to_status_id_str",
    "in_reply_to_user_id_str",
    "in_reply_to_screen_name"
    ]

def produce_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

def get_full_text(tweet: Tweet) -> str:
    def get_text_full_text(tweet):
        if "full_text" in tweet:
            return tweet["full_text"]
        else:
            return tweet["text"]
        
    if "quoted_status" in tweet:
        return get_text_full_text(tweet["quoted_status"])
    elif "retweeted_status" in tweet:
        return get_text_full_text(tweet["retweeted_status"])
    else:
        return get_text_full_text(tweet)

def convert_tweets_json_to_df(tweets_json: List[ArchiveTweet]) -> pd.DataFrame:
    id_text_pairs = tz.pipe(tweets_json, tz.pluck("tweet"), tz.map(pick(TWEET_KEYS_FOR_DF)), list)
    tweets_df = pd.DataFrame(id_text_pairs, columns=TWEET_KEYS_FOR_DF)
    tweets_df.fillna(-1, inplace=True)
    return tweets_df

def convert_looked_up_tweets_to_df(tweets_json: List[Tweet]) -> pd.DataFrame:
    id_text_pairs = tz.pipe(tweets_json, tz.map(pick(TWEET_KEYS_FOR_DF)), list)
    tweets_df = pd.DataFrame(id_text_pairs, columns=TWEET_KEYS_FOR_DF)
    tweets_df.fillna(-1, inplace=True)
    tweets_df['full_text'] = list(map(get_full_text, tweets_json))
    tweets_df["in_reply_to_status_id_str"].fillna(-1, inplace=True)
    tweets_df["in_reply_to_user_id_str"].fillna(-1, inplace=True)
    tweets_df["in_reply_to_screen_name"].fillna(-1, inplace=True)
    return tweets_df

def extract_tweets():
    """side effects: reads tweets.js, writes tweets.csv"""
    tweets = load_archive_tweets(os.path.join(ARCHIVE_PATH,"/data/tweets.js"))
    tweets_df = convert_tweets_json_to_df(tweets)
    tweets_df.to_csv(os.path.join(BASE_PATH, f"data/tweets_{produce_timestamp()}.csv"), index=False)
    return tweets_df
# %%
# pre embedding stuff
"""
Clean tweet text from things like links, mentions, hashtags, etc.
"""
import re

def clean_tweet_text(tweet):
    # remove links
    tweet = re.sub(r"http\S+", "", tweet)
    # remove mentions at the start of the tweet. e.g. "@user1 @user2 tweet text" -> "tweet text"
    tweet = re.sub(r"^(@\S+ )+", "", tweet)
    # remove RT
    tweet = re.sub(r"RT @\S+:", "", tweet)
    # remove leading and trailing spaces
    tweet = tweet.strip()
    return tweet

# %%
"""
convert created_at: "Tue Aug 16 01:31:11 +0000 2016" to datetime
"""

def convert_to_datetime(created_at):
    return datetime.datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
