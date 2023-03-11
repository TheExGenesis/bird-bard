# %%
import sys 
sys.path.append("/Users/frsc/Documents/Projects/birdbard/birdBARD")
import pinecone
from src.topic_modelling.prep_archive import BASE_PATH
from src.topic_modelling.make_embeddings import load_embeddings
import os
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff
import toolz.curried as tz
from tqdm import tqdm
from src.vector_search.pinecone_utils import DEFAULT_INDEX_NAME, load_pinecone_key, convert_tweet_df_to_pinecone_upsert, upsert_pinecone, partition_df_by_size, call_w_partition_max_len


def upsert_pinecone_with_partition(df, index_name=DEFAULT_INDEX_NAME, partition_max_len=50):
    """
    upserts a dataframe into pinecone in batches of 1000
    """
    return call_w_partition_max_len(df, upsert_pinecone(index_name), partition_max_len)

def populate_pinecone_w_embeddings(embeddings_path=f"{BASE_PATH}/data/vector_search_tweets.csv"):
    """
    SIDE-EFFECTS
    populates pinecone with the embeddings from the archive
    """
    PINECONE_KEY = load_pinecone_key(BASE_PATH)
    pinecone.init(api_key=PINECONE_KEY, environment="us-east1-gcp")
    tweet_df = load_embeddings(embeddings_path)
    upsert_pinecone_with_partition(tweet_df)
    
if __name__ == "__main__":
    populate_pinecone_w_embeddings("/Users/frsc/Documents/Projects/birdbard/birdBARD/data/vector_search_tweets.csv")