from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Optional
from metaagent.memory.shortterm_memory import Memory
from metaagent.config import Config
from pathlib import Path


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
