# https://docs.trychroma.com/

import chromadb
from chromadb.utils import embedding_functions

# Configure Chroma to save and load from your local machine. Data will be persisted automatically
# and loaded on start (if it exists).
client = chromadb.PersistentClient(path="../storage/chromadb")

# Here the standard embeddings are used. Other embeddings can be used: https://docs.trychroma.com/embeddings
# Also, better embedding models from Huggingface can be used: https://huggingface.co/spaces/mteb/leaderboard
# Just add embeddings when adding documents and use the same model when querying:
# https://docs.trychroma.com/usage-guide#adding-data-to-a-collection
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-mpnet-base-v2")


# Create a collection with the default embedding function


# Add some data to the collection
def add_data(documents, metadatas, ids, name):
    print('Add data')
    collection = client.get_or_create_collection(name=name, embedding_function=sentence_transformer_ef)
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )


def query_email_collection(query_texts, n_results, name):
    collection = client.get_or_create_collection(name=name, embedding_function=sentence_transformer_ef)
    # Query the collection
    results = collection.query(
        query_texts=query_texts,
        n_results=n_results
    )
    return results
