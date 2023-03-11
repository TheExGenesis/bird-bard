# %%
import sys
sys.path.append("/Users/frsc/Documents/Projects/birdbard/birdBARD")
from src.topic_modelling.prep_archive import load_and_process_tweets_for_embed, process_tweets_for_embed
from src.twitter_archive_to_db.archive_utils import BASE_PATH, load_looked_up_archive_json
from src.vector_search.vector_search_utils import convert_looked_up_tweets_to_df
import os
import json
from src.topic_modelling.make_embeddings import make_embeddings
import toolz.curried as tz
# %%
# new_archive_path = os.path.join(BASE_PATH,"data/exgenesis-archive/data/tweets.js")
# archive = load_archive_tweets(new_archive_path)

# load the looked up archive


if __name__ == "__main__":
    archive = load_looked_up_archive_json()
    df = convert_looked_up_tweets_to_df(archive)
    vector_search_tweets_df = process_tweets_for_embed(df)
    vs_tweets_embedded_df = make_embeddings(vector_search_tweets_df)
    vs_tweets_embedded_df.to_csv(os.path.join(BASE_PATH,"data/vector_search_tweets.csv"), index=False)