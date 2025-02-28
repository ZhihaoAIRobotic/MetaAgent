from abc import ABC, abstractmethod


class VectorStoreBase(ABC):
    @abstractmethod
    async def create_col(self, name, vector_size, distance):
        """Create a new collection."""
        pass

    @abstractmethod
    async def insert_vectors(self, collection_name, vectors, metadata):
        """Insert vectors into a collection."""
        pass

    async def insert_docs(self, collection_name, docs, metadata, embedding_model):
        """Insert docs directly into a collection."""
        pass

    @abstractmethod
    async def delete(self, collection_name, vector):
        """Delete a vector from a collection."""
        pass

    async def update(self, collection_name, vector, metadata):
        """Update a vector and its payload."""
        pass

    @abstractmethod
    async def query_vectors(self, collection_name, vector, k):
        """Query for similar vectors."""
        pass

    async def query_docs(self, collection_name, doc, k):
        """Query for similar docs."""
        pass

    async def search(self):
        """Retrieve a vector by ID."""
        pass

    async def list_cols(self):
        """List all collections."""
        pass

    async def delete_col(self, name):
        """Delete a collection."""
        pass

    async def col_info(self, name):
        """Get information about a collection."""
        pass
