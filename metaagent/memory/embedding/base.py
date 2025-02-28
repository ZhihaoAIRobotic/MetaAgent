"""Interface for embedding models."""
from abc import ABC, abstractmethod
from typing import List, Any
import asyncio


class EmbeddingBase(ABC):
    """Interface for embedding models."""
    @abstractmethod
    async def get_embeddings(self, texts: List[str], semaphore: asyncio.Semaphore) -> Any:
        """
        Get embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            semaphore: Semaphore for controlling concurrency
            
        Returns:
            Embeddings in the format specific to the embedding provider
        """
        raise NotImplementedError("Subclasses must implement get_embeddings")
    
    @abstractmethod
    async def process_data(self, data: List[dict]) -> List[dict]:
        """
        Process data to get embeddings.
        
        Args:
            data: List of dictionaries containing 'id' and 'text' keys
            
        Returns:
            List of dictionaries containing embeddings and metadata
        """
        raise NotImplementedError("Subclasses must implement process_data")

