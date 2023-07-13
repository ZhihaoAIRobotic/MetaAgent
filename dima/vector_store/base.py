import warnings
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Optional, Tuple
from pydantic import BaseModel, Field

class Document(BaseModel):
    """Interface for interacting with a document."""

    text_content: str
    metadata: dict = Field(default_factory=dict)

    def __init__(self, text_content, *args, **kwargs):
        super().__init__(text_content=text_content, *args, **kwargs)

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
    def get_matching_text(self, query: str, top_k: int, filter = None, **kwargs: Any) -> List[Document]:
        """Return docs most similar to query using specified search type."""

    def add_documents(self, documents: List[Document], **kwargs: Any) -> List[str]:
        """Run more documents through the embeddings and add to the vectorstore.
        """
        texts = [doc.text_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        return self.add_texts(texts, metadatas, **kwargs)