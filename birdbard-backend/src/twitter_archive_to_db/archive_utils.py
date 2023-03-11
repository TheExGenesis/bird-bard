# %%
BASE_PATH = "/Users/frsc/Documents/Projects/birdbard/birdBARD"
import sys
from typing import List

from src.schema import Tweet, ArchiveTweet, VectorSearchTweet
sys.path.append(BASE_PATH)
import datetime
import toolz.curried as tz
import pandas as pd
import json
import os

from src.topic_modelling.tz_utils import pick

# %%
# archive stuff
ARCHIVE_PATH = f"{BASE_PATH}/data/exgenesis-archive"


def extract_archive_ids(ARCHIVE_PATH = f"{BASE_PATH}/data/exgenesis-archive"):
    """
    returns a list of tweet ids and user ids from the archive
    """
    with open(ARCHIVE_PATH + "/data/tweets.js", "r") as f:
        # get the content as a string
        content = f.read().split("window.YTD.tweets.part0 = ")[1]
        # load content as json
        tweets = json.loads(content)
        tweet_ids = tz.pipe(tweets, tz.pluck("tweet"), tz.filter(lambda x: "id_str" in x), tz.pluck(["id"]), tz.concat, list)
        in_reply_to_ids = tz.pipe(tweets, tz.pluck("tweet"), tz.filter(lambda x: "in_reply_to_status_id_str" in x), tz.pluck(["in_reply_to_status_id_str"]), tz.concat, list)
        user_ids = tz.pipe(tweets, tz.pluck("tweet"), tz.filter(lambda x: "in_reply_to_user_id_str" in x), tz.pluck(["in_reply_to_user_id_str"]), tz.concat, list)
        return {"tweet_ids": tweet_ids, "in_reply_to_ids": in_reply_to_ids, "user_ids": user_ids}



def load_archive_tweets(path):
    with open(path, "r") as f:
        # get the content as a string
        content = f.read().split("window.YTD.tweets.part0 = ")[1]
        # load content as json
        tweets = json.loads(content)
    return tweets

# lookup stuff
def load_looked_up_archive_json(looked_up_archive_path = os.path.join(BASE_PATH,"data/archive_api_lookup/tweets.json")):
    with open(looked_up_archive_path, "r") as f:
        return json.load(f)