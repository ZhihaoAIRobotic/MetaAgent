from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Optional
from dima.memory.base import Memory


class VectorStore(ABC):
    @abstractmethod
    def add_info(
            self,
            info: Iterable[str],
            metadatas: Optional[List[dict]] = None,
            **kwargs: Any,
    ) -> List[str]:
        """Add texts to the vector store."""

    @abstractmethod
    def get_matching_text(self, query: str, top_k: int, filter=None, **kwargs: Any) -> List[Memory]:
        """Return docs most similar to query using specified search type."""

    def add_documents(self, documents: List[Memory], **kwargs: Any) -> List[str]:
        """Run more documents through the embeddings and add to the vectorstore.
        """
        texts = [doc.text_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        return self.add_texts(texts, metadatas, **kwargs)
    
    