# %%
import tiktoken
import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff
from src.topic_modelling.prep_archive import BASE_PATH

def init_openai():
    openai.organization = "org-itss8bUKzHlQxm51E1VzgRCw"
    openai.api_key_path = f"{BASE_PATH}/.openai_key"


def count_tokens(text):
    encoding = tiktoken.get_encoding("p50k_base") #for code modelas and text-davinci002 and 003
    return len(encoding.encode(text))

# @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def get_single_embedding(text, model="text-embedding-ada-002"):
    init_openai()
    return openai.Embedding.create(
        input=text.replace("\n", " "), model=model
    )["data"][0]["embedding"]
# %%
