
# %%
import toolz.curried as tz
import pandas as pd
import json
from src.topic_modelling.tz_utils import pick
from src.vector_search.vector_search_utils import clean_tweet_text, convert_to_datetime
import datetime

BASE_PATH = "/Users/frsc/Documents/Projects/birdbard/birdBARD"
ARCHIVE_PATH = f"{BASE_PATH}/data/exgenesis-archive"


# %%
def process_tweets_for_embed(tweets_df):
    tweets_df["full_text"] = tweets_df["full_text"].apply(clean_tweet_text)
    tweets_df["created_at"] = tweets_df["created_at"].apply(convert_to_datetime)
    # tweets_df["in_reply_to_status_id_str"] = tweets_df["in_reply_to_status_id_str"].apply(tz.map(tz.compose(str, int)))
    # tweets_df["in_reply_to_user_id_str"] = tweets_df["in_reply_to_user_id_str"].apply(tz.map(tz.compose(str, int)))
    tweets_df = tweets_df[tweets_df["created_at"] > datetime.datetime(2019, 1, 1, tzinfo=datetime.timezone.utc)]
    # tweets_df = tweets_df[tweets_df["favorite_count"] > 0]
    tweets_df = tweets_df[tweets_df.full_text.replace("\n", " ") != '']
    return tweets_df
"""
load tweets.csv, clean text, convert created_at to datetime, filter for tweets after 2019
"""
def load_and_process_tweets_for_embed(path = BASE_PATH + "/data/tweets.csv"):
    tweets_df = pd.read_csv(path)
    return process_tweets_for_embed(tweets_df)
    

# %%
    
    
