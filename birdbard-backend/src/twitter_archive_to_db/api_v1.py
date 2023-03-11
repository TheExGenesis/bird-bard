# %%
# load the twitter archive, lookup each tweet id in the API v1.1, and save the json to a file
import tweepy
import logging

logging.basicConfig(level=logging.DEBUG)

TT_BEARER_TOKEN_PATH = "/Users/frsc/Documents/Projects/birdbard/birdBARD/.tt_bearer_token"
TT_ACCESS_TOKEN_PATH = "/Users/frsc/Documents/Projects/birdbard/birdBARD/.tt_access_token"
TT_ACCESS_SCRET_PATH = "/Users/frsc/Documents/Projects/birdbard/birdBARD/.tt_access_secret"
TT_CONSUMER_KEY_PATH = "/Users/frsc/Documents/Projects/birdbard/birdBARD/.tt_consumer_key"
TT_CONSUMER_SECRET_PATH = "/Users/frsc/Documents/Projects/birdbard/birdBARD/.tt_consumer_secret"

def get_tweepy_api_v1():
    with open(TT_BEARER_TOKEN_PATH, "r") as f:
        TT_BEARER_TOKEN = f.read().strip()

    with open(TT_ACCESS_TOKEN_PATH, "r") as f:
        TT_ACCESS_TOKEN = f.read().strip()

    with open(TT_ACCESS_SCRET_PATH, "r") as f:
        TT_ACCESS_SECRET = f.read().strip()

    with open(TT_CONSUMER_KEY_PATH, "r") as f:
        TT_CONSUMER_KEY = f.read().strip()

    with open(TT_CONSUMER_SECRET_PATH, "r") as f:
        TT_CONSUMER_SECRET = f.read().strip()

    auth = tweepy.OAuth1UserHandler(
    TT_CONSUMER_KEY, TT_CONSUMER_SECRET,
    TT_ACCESS_TOKEN, TT_ACCESS_SECRET
    )
    return tweepy.API(auth)

# %%
