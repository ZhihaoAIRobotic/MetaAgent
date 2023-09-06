from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Optional
from metaagent.memory.shortterm_memory import Memory
from metaagent.config import Config
from pathlib import Path


# class VectorStore(ABC):
#     @abstractmethod
#     def add_info(
#             self,
#             info: Iterable[str],
#             metadatas: Optional[List[dict]] = None,
#             **kwargs: Any,
#     ) -> List[str]:
#         """Add texts to the vector store."""

#     @abstractmethod
#     def get_matching_text(self, query: str, top_k: int, filter=None, **kwargs: Any) -> List[Memory]:
#         """Return docs most similar to query using specified search type."""

#     def add_documents(self, documents: List[Memory], **kwargs: Any) -> List[str]:
#         """Run more documents through the embeddings and add to the vectorstore.
#         """
#         texts = [doc.text_content for doc in documents]
#         metadatas = [doc.metadata for doc in documents]
#         return self.add_texts(texts, metadatas, **kwargs)


class BaseStore(ABC):
    """FIXME: consider add_index, set_index and think 颗粒度"""

    @abstractmethod
    def search(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def write(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def add(self, *args, **kwargs):
        raise NotImplementedError


class LocalStore(BaseStore, ABC):
    def __init__(self, raw_data: Path, cache_dir: Path = None):
        if not raw_data:
            raise FileNotFoundError
        self.config = Config()
        self.raw_data = raw_data
        if not cache_dir:
            cache_dir = raw_data.parent
        self.cache_dir = cache_dir
        self.store = self._load()
        if not self.store:
            self.store = self.write()

    def _get_index_and_store_fname(self):
        fname = self.raw_data.name.split('.')[0]
        index_file = self.cache_dir / f"{fname}.index"
        store_file = self.cache_dir / f"{fname}.pkl"
        return index_file, store_file

    @abstractmethod
    def _load(self):
        raise NotImplementedError

    @abstractmethod
    def _write(self, docs, metadatas):
        raise NotImplementedError
