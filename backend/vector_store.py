import chromadb
from chromadb.utils import embedding_functions
from models import Memory

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="../data/chroma_db")

# Use default embedding function (all-MiniLM-L6-v2)
default_ef = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_or_create_collection(name="memories", embedding_function=default_ef)

def add_memory(content: str, metadata: dict = {}):
    collection.add(
        documents=[content],
        metadatas=[metadata],
        ids=[str(metadata.get("id", collection.count() + 1))]  # Simple ID generation
    )
    return True

def search_memories(query: str, n_results: int = 2):
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results
