# %%
import sys 
sys.path.append("/Users/frsc/Documents/Projects/birdbard/birdBARD")
import pinecone
import toolz.curried as tz
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff
from src.topic_modelling.openai_utils import get_single_embedding
from src.vector_search.pinecone_utils import DEFAULT_INDEX_NAME, query_pinecone_w_embedding
# %%
# @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))



def query_pinecone_w_text(text:str, top_k=10, **kwargs):
    print("getting embedding...")
    embedded_query = get_single_embedding(text)
    print("querying pinecone...")
    return query_pinecone_w_embedding(embedded_query, top_k, **kwargs)
# %%

if __name__ == "__main__":
    resp = query_pinecone_w_text("Comparative computational theology", top_k=20)
    for i, match in enumerate(resp['matches']):
        # print(f"{match['score']} - {match['metadata']['full_text']}")
        print(f"{i}. - {match['metadata']['full_text']}")
# %%
