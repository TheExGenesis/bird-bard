# %%
from operator import itemgetter
from api_v1 import get_tweepy_api_v1
from archive_utils import extract_archive_ids
import toolz.curried as tz
import json
from tqdm import tqdm
import os
# %%
ARCHIVE_API_LOOKUP_PATH = "/Users/frsc/Documents/Projects/birdbard/birdBARD/data/archive_api_lookup"
TMP_TWEETS_PATH = f"{ARCHIVE_API_LOOKUP_PATH}/tweets"
TMP_USERS_PATH = f"{ARCHIVE_API_LOOKUP_PATH}/users"
FINAL_TWEETS_PATH = f"{ARCHIVE_API_LOOKUP_PATH}/tweets.json"
FINAL_USERS_PATH = f"{ARCHIVE_API_LOOKUP_PATH}/users.json"

def load_json_chunks(ARCHIVE_API_LOOKUP_PATH=ARCHIVE_API_LOOKUP_PATH):
    """
    loads the json chunks from the archive api lookup
    """
    tweets = []
    users = []
    os.makedirs(TMP_TWEETS_PATH, exist_ok=True)
    for filename in sorted(os.listdir(ARCHIVE_API_LOOKUP_PATH+"/tweets")):
        try:
            with open(f"{TMP_TWEETS_PATH}/{filename}", "r") as f:
                tweets += json.loads(f.read())
        except Exception as e:
            print(f"Couldn't load {filename}: {e}")
    os.makedirs(TMP_USERS_PATH, exist_ok=True)
    for filename in sorted(os.listdir(ARCHIVE_API_LOOKUP_PATH+"/users")):
        try:
            with open(f"{TMP_USERS_PATH}/{filename}", "r") as f:
                users += json.loads(f.read())
        except Exception as e:
            print(f"Couldn't load {filename}: {e}")
    tweets = tz.pipe(tweets, tz.unique(key=lambda x: x['id_str']), list)
    users = tz.pipe(users, tz.unique(key=lambda x: x['id_str']), list)
    return tweets, users

def get_highest_filename_number(path):
    """
    returns the highest number in a filename in a directory
    """
    numbers = [0] + [int(path.split("_")[1].split(".")[0]) for path in os.listdir(path) if path.endswith('.json')]
    return max(numbers)+1

def lookup_archive_tweets(api, tweet_ids, user_ids):
    """
    returns a list of tweet ids and user ids from the archive
    """
    # TODO filter out ids in already downloaded chunks
    base_i = get_highest_filename_number(TMP_TWEETS_PATH)
    tweet_ids_chunks = tz.partition(100, tweet_ids, pad=None)
    for i, tweet_ids_chunk in tqdm(enumerate(tweet_ids_chunks)):
        tweets = api.lookup_statuses([id for id in tweet_ids_chunk if id is not None], include_entities=True, tweet_mode="extended")
        tweets_json = list(map(lambda x: x._json, tweets))
        os.makedirs(TMP_TWEETS_PATH, exist_ok=True)
        if len(tweets_json) > 0:
            with open(f"{TMP_TWEETS_PATH}/tweets_{base_i+i}.json", "w") as f:
                f.write(json.dumps(tweets_json))
    # lookup users
    base_i = get_highest_filename_number(TMP_USERS_PATH)
    user_ids_chunks = tqdm(tz.partition(100, user_ids, pad=None))
    for i, user_ids_chunk in enumerate(user_ids_chunks):
        users = api.lookup_users(user_id=[id for id in user_ids_chunk if id is not None])
        users_json = list(map(lambda x: x._json, users))
        os.makedirs(TMP_USERS_PATH, exist_ok=True)
        if len(user_ids) > 0:
            with open(f"{TMP_USERS_PATH}/users_{base_i+i}.json", "w") as f:
                f.write(json.dumps(users_json))

def join_chunks_and_clean(ARCHIVE_API_LOOKUP_PATH=ARCHIVE_API_LOOKUP_PATH):
    downloaded_tweets, downloaded_users = load_json_chunks(ARCHIVE_API_LOOKUP_PATH)
    with open(f"{FINAL_TWEETS_PATH}", "w") as f:
        f.write(json.dumps(downloaded_tweets))
    with open(f"{FINAL_USERS_PATH}", "w") as f:
        f.write(json.dumps(downloaded_users))
    # delete temporary chunk files in
    if os.path.exists(TMP_TWEETS_PATH):
        os.remove(TMP_TWEETS_PATH)  
    if os.path.exists(TMP_USERS_PATH):
        os.remove(TMP_USERS_PATH)

def download_missing_tweets(ARCHIVE_API_LOOKUP_PATH=ARCHIVE_API_LOOKUP_PATH):
    """
    loads the json chunks from the archive api lookup, compares them to the archive ids, and downloads the missing tweets
    """
    downloaded_tweets, downloaded_users = load_json_chunks()
    # from archive
    user_tweet_ids, in_reply_to_ids, user_ids = itemgetter("tweet_ids", "in_reply_to_ids", "user_ids")(extract_archive_ids())
    archive_tweet_ids = tz.pipe(user_tweet_ids + in_reply_to_ids, tz.unique, list)
    downloaded_tweet_ids = tz.pipe(downloaded_tweets, tz.pluck("id_str"), list)
    downloaded_user_ids = tz.pipe(downloaded_users, tz.pluck("id_str"), list)
    desired_tweet_ids = list(set(archive_tweet_ids).difference(set(downloaded_tweet_ids)))
    desired_user_ids = list(set(user_ids).difference(set(downloaded_user_ids)))
    api = get_tweepy_api_v1()
    print(f"requesting {len(desired_tweet_ids)} tweets and {len(desired_user_ids)} users")
    lookup_archive_tweets(api, desired_tweet_ids, desired_user_ids)
    # when done
    print("done, joining and cleaning")
    join_chunks_and_clean(ARCHIVE_API_LOOKUP_PATH)

if __name__ == "__main__":
    download_missing_tweets()