import uuid
from typing import Any, Optional, Iterable, List
import chromadb
from chromadb import Settings
from dima.configs.config import CHROMA_HOST_NAME, CHROMA_PORT
from dima.memory.vector_store.base import VectorStore
from dima.memory.embedding.base import Embeddings
from dima.memory.base import Memory


def _build_chroma_client():
    return chromadb.Client(Settings(chroma_api_impl="rest", chroma_server_host=CHROMA_HOST_NAME,
                                    chroma_server_http_port=CHROMA_PORT))


class ChromaVS(VectorStore):
    def __init__(
            self,
            collection_name: str,
            embedding_model: Embeddings,
            text_field: str,
            namespace: Optional[str] = "",
    ):
        self.client = _build_chroma_client()
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.text_field = text_field
        self.namespace = namespace

    @classmethod
    def create_collection(cls, collection_name):
        """Create a Chroma Collection.
        Args:
        collection_name: The name of the collection to create.
        """
        chroma_client = _build_chroma_client()
        return chroma_client.get_or_create_collection(name=collection_name)

    def add_texts(
            self,
            texts: Iterable[str],
            metadatas: Optional[List[dict]] = None,
            ids: Optional[List[str]] = None,
            namespace: Optional[str] = None,
            batch_size: int = 32,
            **kwargs: Any,
    ) -> List[str]:
        """Add texts to the vector store."""
        if namespace is None:
            namespace = self.namespace

        metadatas = []
        ids = ids or [str(uuid.uuid4()) for _ in texts]
        if len(ids) < len(texts):
            raise ValueError("Number of ids must match number of texts.")

        for text, id in zip(texts, ids):
            metadata = metadatas.pop(0) if metadatas else {}
            metadata[self.text_field] = text
            metadatas.append(metadata)
        collection = self.client.get_collection(name=self.collection_name)
        collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        return ids

    def get_matching_text(self, query: str, top_k: int = 5, metadata: Optional[dict] = {}, **kwargs: Any) -> List[Memory]:
        """Return docs most similar to query using specified search type."""
        embedding_vector = self.embedding_model.embed_query(query)
        collection = self.client.get_collection(name=self.collection_name)
        filters = {}
        for key in metadata.keys():
            filters[key] = metadata[key]
        results = collection.query(
            query_embeddings=embedding_vector,
            include=["documents"],
            n_results=top_k,
            where=filters
        )

        documents = []

        for node_id, text, metadata in zip(
                results["ids"][0],
                results["documents"][0],
                results["metadatas"][0]):
            documents.append(
                Memory(
                    text_content=text,
                    metadata=metadata
                )
            )

        return documents