# %%
from bertopic import BERTopic
from sklearn.datasets import fetch_20newsgroups
 
docs = fetch_20newsgroups(subset='all',  remove=('headers', 'footers', 'quotes'))['data']

topic_model = BERTopic(language="multilingual")
topics, probs = topic_model.fit_transform(docs)
# %%
topic_model.get_topic_info()

# %%
topic_model.get_document_info(docs)

# %%
