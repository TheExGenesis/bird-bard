# mostly from https://towardsdatascience.com/topic-modeling-with-bert-779f7db187e6
# %%
import umap
from sklearn.datasets import load_digits
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from prep_archive import load_and_process_tweets_for_embed, BASE_PATH
import hdbscan
from math import isnan
from sklearn.metrics.pairwise import cosine_similarity
# Plot tweet embeddings and text on hover with plotly

def plot_embeddings(embeddings, texts, labels=None, title=""):
    reducer = umap.UMAP()
    embedding = reducer.fit_transform(embeddings)
    fig = go.Figure(
        data=[
            go.Scatter(
                x=embedding[:, 0],
                y=embedding[:, 1],
                mode="markers",
                marker=dict(size=10, color=labels),
                text=texts,
            )
        ]
    )
    fig.update_layout(title=title)
    fig.show()

# convert pandas adas to numpy arrays
def convert_ada_to_np(ada):
    return np.array(ada.replace('[','').replace(']','').split(',')).astype(np.float32)

def filter_tweets_for_clustering(df):
    # filter out tweets where df.in_reply_to_screen_name is not nan
    df = df[df.in_reply_to_screen_name.isna()]
    # filter out tweets with fewer than 3 words
    df = df[df.full_text.apply(lambda x: len(x.split(' ')) > 3)]
    return df

def cluster_for_topics(df):
    # dim reduction pre clustering
    embeddings = list(df['ada_embedding'])
    umap_embeddings = umap.UMAP(n_neighbors=15, 
                                n_components=5, 
                                metric='cosine').fit_transform(embeddings)
    # clustering
    cluster = hdbscan.HDBSCAN(min_cluster_size=5,
                              metric='euclidean',                      
                              cluster_selection_method='eom').fit(umap_embeddings)
    print(np.unique(cluster.labels_))
    plot_embeddings(umap_embeddings, [f"{label}. {text}" for label, text in zip(cluster.labels_, df.full_text)], labels=cluster.labels_, title="Tweet embeddings")
    return cluster

# %%
df = pd.read_csv(BASE_PATH+'/data/embedded_tweets_feb18.csv')
df['ada_embedding'] = df.ada_embedding.apply(convert_ada_to_np)
df = filter_tweets_for_clustering(df)
cluster = cluster_for_topics(df)
# %%
df['Doc'] = df['full_text']
df['Topic'] = cluster.labels_
df['Doc_ID'] = range(len(df))
docs_per_topic = df.groupby(['Topic'], as_index = False).agg({'full_text': ' '.join})

# %%
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

def c_tf_idf(documents, m, ngram_range=(1, 1)):
    count = CountVectorizer(ngram_range=ngram_range, stop_words="english").fit(documents)
    t = count.transform(documents).toarray()
    w = t.sum(axis=1)
    tf = np.divide(t.T, w)
    sum_t = t.sum(axis=0)
    idf = np.log(np.divide(m, sum_t)).reshape(-1, 1)
    tf_idf = np.multiply(tf, idf)

    return tf_idf, count
  
tf_idf, count = c_tf_idf(docs_per_topic.full_text.values, m=len(df))

# %%
def extract_top_n_words_per_topic(tf_idf, count, docs_per_topic, n=20):
    words = count.get_feature_names_out()
    labels = list(docs_per_topic.Topic)
    tf_idf_transposed = tf_idf.T
    indices = tf_idf_transposed.argsort()[:, -n:]
    top_n_words = {label: [(words[j], tf_idf_transposed[i][j]) for j in indices[i]][::-1] for i, label in enumerate(labels)}
    return top_n_words

def extract_topic_sizes(df):
    topic_sizes = (df.groupby(['Topic'])
                     .Doc
                     .count()
                     .reset_index()
                     .rename({"Topic": "Topic", "Doc": "Size"}, axis='columns')
                     .sort_values("Size", ascending=False))
    return topic_sizes

top_n_words = extract_top_n_words_per_topic(tf_idf, count, docs_per_topic, n=20)
topic_sizes = extract_topic_sizes(df)
topic_sizes.head(10)

# %%
# save topic_sizes and top_n_words to csv
topic_sizes.to_csv(BASE_PATH+'/data/topic_sizes.csv', index=False)
pd.DataFrame(top_n_words).T.to_csv(BASE_PATH+'/data/top_n_words.csv')
# %%

def merge_smallest_topic_w_most_similar(docs_df, tf_idf,data):
    # untested, maybe to be used as a feature later
    for i in range(20):
        # Calculate cosine similarity
        similarities = cosine_similarity(tf_idf.T)
        np.fill_diagonal(similarities, 0)

        # Extract label to merge into and from where
        topic_sizes = docs_df.groupby(['Topic']).count().sort_values("Doc", ascending=False).reset_index()
        topic_to_merge = topic_sizes.iloc[-1].Topic
        topic_to_merge_into = np.argmax(similarities[topic_to_merge + 1]) - 1

        # Adjust topics
        docs_df.loc[docs_df.Topic == topic_to_merge, "Topic"] = topic_to_merge_into
        old_topics = docs_df.sort_values("Topic").Topic.unique()
        map_topics = {old_topic: index - 1 for index, old_topic in enumerate(old_topics)}
        docs_df.Topic = docs_df.Topic.map(map_topics)
        docs_per_topic = docs_df.groupby(['Topic'], as_index = False).agg({'Doc': ' '.join})

        # Calculate new topic words
        m = len(data)
        tf_idf, count = c_tf_idf(docs_per_topic.Doc.values, m)
        top_n_words = extract_top_n_words_per_topic(tf_idf, count, docs_per_topic, n=20)

# %%
