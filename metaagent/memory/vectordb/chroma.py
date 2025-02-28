import uuid
from typing import Any, Optional, Iterable, List

import chromadb
from chromadb.utils import embedding_functions

from metaagent.memory.vectordb.base import VectorStoreBase
from metaagent.logs import logger

# TODO: Coming soon, the chroma vector store is still under development. We will support after the chroma vector store is stable.

class ChromaVS(VectorStoreBase):
    def __init__(
            self,
            collection_name: str,
            embedding_model: str,
            ApiKey: Optional[str] = None,
    ):
        """Initialize the Chroma Vector Store.
        Args:
            collection_name: The name of the collection to create.
            embedding_model: The name of the embedding model to use, now support ['OpenAI', 'huggingface'].
            ApiKey: The api key to use for the embedding model.
        """

        if embedding_model == 'OpenAI':
            self.embedding_model = embedding_functions.OpenAIEmbeddingFunction(
                api_key=ApiKey,
                model_name="text-embedding-ada-002"
            )
        elif embedding_model == 'huggingface':
            self.embedding_model = embedding_functions.HuggingFaceEmbeddingFunction(
                api_key=ApiKey,
                model_name="sentence-transformers/all-MiniLM-L6-v2"
                )

        self.client = chromadb.PersistentClient(path='./chroma.db')
        self.collection_name = collection_name
        self.embedding_model = embedding_model

    def create_load_collection(self):
        """Create or load a Chroma Collection.
        Args:
        collection_name: The name of the collection to create.
        """
        collections = self.list_cols()
        for collection in collections:
            if collection.name == self.collection_name:
                logger.debug(f"Collection {self.collection_name} already exists. Skipping creation.")
        if self.embedding_model is None:
            self.collection = self.client.get_or_create_collection(name=self.collection_name)  # Use the default embedding function
        else:
            self.collection = self.client.get_or_create_collection(name=self.collection_name, embedding_function=self.embedding_model)
        return self.collection

    def clear_collection(self):
        """Clear a Chroma Collection.
        Args:
        collection_name: The name of the collection to clear.
        """
        self.collection.clear()
        return self.collection

    def add_texts(
            self,
            texts: Iterable[str],
            metadatas: Optional[List[dict]] = None,
            ids: Optional[List[str]] = None,
            **kwargs: Any,
    ) -> List[str]:
        """Add texts to the vector store."""
        ids = ids or [str(uuid.uuid4()) for _ in texts]
        if len(ids) < len(texts):
            raise ValueError("Number of ids must match number of texts.")

        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        return ids

    def query_text(self, query: str, top_k: int = 1, metadata: Optional[dict] = {}, **kwargs: Any) -> List[str]:
        """Return docs most similar to query using specified search type."""
        filters = {}
        for key in metadata.keys():
            filters[key] = metadata[key]
        results = self.collection.query(
            query_texts=query,
            n_results=top_k,
            where=filters
        )
        # TODO Check if the query is empty
        # TODO Check the results['documents'] 
        documents = results['documents'][0]
        return documents


if __name__ == '__main__':
    collection_name = 'test'
    embedding_model = 'OpenAI'
    chroma = ChromaVS(collection_name, embedding_model)
    chroma.load_collection()
    chroma.add_texts(['apple', 'water'])
    chroma.query_text('cup')
