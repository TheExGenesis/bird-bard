# %%
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff
import pandas as pd
import openai
import toolz.curried as tz
from src.topic_modelling.openai_utils import count_tokens, init_openai
from src.topic_modelling.prep_archive import load_and_process_tweets_for_embed, BASE_PATH
from tqdm import tqdm
from ast import literal_eval

init_openai()

OPENAI_TOK_LIMIT = 250000
MY_TOK_LIMIT = 500 # max that seems to work
TWEETS_PER_BATCH = 50

def split_chunks_by_token_limit(texts, tok_limit=MY_TOK_LIMIT):
    chunks = []
    chunk = []
    chunk_size = 0
    for text in texts:
        chunk_size += count_tokens(text)
        if chunk_size > tok_limit:
            chunks.append(chunk)
            chunk = []
            chunk_size = 0
        chunk.append(text)
    chunks.append(chunk)
    return chunks



# @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def get_embeddings_batched(texts, model="text-embedding-ada-002"):
    """side-effect: calls openai API to get embeddings"""
    assert all([isinstance(x, str) for x in texts])
    # batched
    # chunks = split_chunks_by_token_limit(texts)
    chunks = list(tz.partition(TWEETS_PER_BATCH ,texts, pad=None))
    embeddings = []
    for chunk in tqdm(chunks):
        texts = [text.replace("\n", " ") for text in chunk if text is not None]
        embeddings += (
            openai.Embedding.create(
                input=texts, model=model
            )["data"]
        )
    return embeddings
# %%
def make_embeddings(df:pd.DataFrame)->pd.DataFrame:
    """side-effect: calls openai API to get embeddings"""
    embeddings = get_embeddings_batched(df.full_text)
    df['ada_embedding'] = tz.pipe(embeddings, tz.pluck("embedding"), list)
    return df

def make_embeddings_test(path):
    """side-effect: loads tweets calls openai API to get embeddings"""
    df = load_and_process_tweets_for_embed(path)
    w_embeddings_df = make_embeddings(df)
    w_embeddings_df.to_csv(BASE_PATH+'data/embedded_tweets.csv', index=False)

@tz.curry
def remove_prefix(prefix, string):
    if string.startswith(prefix):
        return string[len(prefix):]
    return string

@tz.curry
def remove_suffix(suffix, string):
    if string.endswith(suffix):
        return string[: -len(suffix)]
    return string

def convert_string_to_array(string):
    return tz.pipe(string, remove_prefix("["),remove_suffix("]"), lambda x: x.split(","), tz.map(float), list)

def load_embeddings(path = BASE_PATH+'data/embedded_tweets.csv'):
    df = pd.read_csv(path, converters={'ada_embedding': literal_eval})
    # df['ada_embedding'] = tz.pipe(df.ada_embedding, tz.map(convert_string_to_array), list)
    return df

# %%
if __name__ == "__main__":
    df = make_embeddings_test()