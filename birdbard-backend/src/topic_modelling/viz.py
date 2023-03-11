# %%
import umap
from sklearn.datasets import load_digits
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from prep_archive import load_and_process_tweets_for_embed, BASE_PATH
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

# %%
if __name__ == "__main__":
    df = pd.read_csv(BASE_PATH+'/data/embedded_tweets_feb18.csv')
    df['ada_embedding'] = df.ada_embedding.apply(convert_ada_to_np)
    plot_embeddings(list(df.ada_embedding), df.full_text, title="Tweet embeddings")

