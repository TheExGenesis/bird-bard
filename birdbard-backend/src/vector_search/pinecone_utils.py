# %%
import os
import toolz.curried as tz
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff
from tqdm import tqdm
import pinecone
from src.topic_modelling.prep_archive import BASE_PATH


DEFAULT_INDEX_NAME = "exgenesis-tweets"

def load_pinecone_key(BASE_PATH):
    PINECONE_KEY_PATH = os.path.join(BASE_PATH, ".pinecone_key")
    with open(PINECONE_KEY_PATH, "r") as f:
        PINECONE_KEY = f.read().strip()
    return PINECONE_KEY

def convert_tweet_df_to_pinecone_upsert(df):
    """
    converts a pandas dataframe to a list of dicts with id, values as ada_embedding, and the rest as metadata
    """
    return [
        {
            "id": str(row["id"]),
            "values": row["ada_embedding"],
            "metadata": {
                "full_text": row["full_text"],
                "created_at": row["created_at"],
                "favorite_count": row["favorite_count"],
                "retweet_count": row["retweet_count"],
                "in_reply_to_status_id_str": str(row["in_reply_to_status_id_str"]),
                "in_reply_to_user_id_str": str(row["in_reply_to_user_id_str"]),
                "in_reply_to_screen_name": str(row["in_reply_to_screen_name"]),
            },
        }
        for _, row in df.iterrows()
    ]


@tz.curry
def upsert_pinecone(index_name, df, BASE_PATH=BASE_PATH):
    PINECONE_KEY = load_pinecone_key(BASE_PATH)
    pinecone.init(api_key=PINECONE_KEY, environment="us-east1-gcp")
    index = pinecone.Index(index_name)
    upsert_response = index.upsert(vectors=convert_tweet_df_to_pinecone_upsert(df))
    return [upsert_response]

@tz.curry
def partition_df_by_size(size, df):
    """
    partitions a dataframe into a list of dataframes of size `size`
    """
    return [
        df.iloc[i : i + size] for i in range(0, df.shape[0], size)
    ]

def call_w_partition_max_len(df, func, partition_max_len):
    """
    calls a function on a dataframe in batches of partition_max_len
    """
    results=[]
    for batch in tqdm(partition_df_by_size(partition_max_len, df)):
        results.append(func(batch))
    return tz.pipe(results, tz.concat, list)

def query_pinecone_w_embedding(embedding, top_k=10, **kwargs):
    PINECONE_KEY = load_pinecone_key(BASE_PATH)
    pinecone.init(api_key=PINECONE_KEY, environment="us-east1-gcp")
    index = pinecone.Index(DEFAULT_INDEX_NAME)
    return index.query(
        vector=embedding,
        top_k=top_k,
        include_metadata=True,
        **kwargs
        )
# %%
