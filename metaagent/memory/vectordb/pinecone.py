from pinecone import Pinecone, ServerlessSpec, PineconeAsyncio

from MetaAgent.metaagent.simple_logger import logger
from metaagent.memory.vectordb.base import VectorStoreBase


class Pinecone_VS(VectorStoreBase):
    def __init__(self,
                 collection_name: str,
                 api_key: str, 
                 embedding_model_dims: int,
                 embedding_model_name: str,
                 similarity_metric: str = "cosine",
                 cloud: str = "aws",
                 region: str = "us-east-1"):
        self.api_key = api_key
        self.pc = Pinecone(api_key=self.api_key)
        self.collection_name = collection_name
        self.embedding_model_dims = embedding_model_dims
        self.embedding_model_name = embedding_model_name
        self.similarity_metric = similarity_metric

        spec = ServerlessSpec(cloud=cloud, region=region)
        self.create_col(self.collection_name, self.embedding_model_dims, self.similarity_metric, spec)


    def create_col(self, name: str, vector_size: int, distance: str, spec: ServerlessSpec):
        """Create a new collection."""
        if not self.pc.has_index(name):
            self.pc.create_index(name=name, dimension=vector_size, metric=distance, spec=spec)
        else:
            logger.debug(f"Collection {name} already exists. Skipping creation.")

    def insert_vectors(self, vectors: list, payloads: list = None, ids: list[str]|None = None, user_id: str|None = None):
        """Insert vectors into a collection."""
        points = []
        for v, p, i in zip(vectors, payloads, ids):
            points.append(
                {
                    "id": i,
                    "values": v,
                    "metadata": p,
                }
            )
        index = self.pc.Index(self.collection_name)
        index.upsert(
				vectors=points,
				namespace=user_id,
			)

    def delete(self, ids, user_id: str = None):
        """Delete a vector from a collection."""
        index = self.pc.Index(self.collection_name)
        index.delete(ids=ids, namespace=user_id)

    def update(self, vector, payload, id, user_id: str = None):
        """Update a vector and its payload."""
        points = []
        points.append(
            {
                "id": id,
                "values": vector,
                "metadata": payload
            }
        )
        index = self.pc.Index(self.collection_name)
        index.upsert(
            vectors=points,
            namespace=user_id,
            async_req=True,
        )

    def query_vectors(self, vectors: list, limit: int, user_id: str|None = None, filters: dict|None = None):
        """Query for similar vectors."""
        index = self.pc.Index(self.collection_name)
        return index.query(
            vector=vectors,
            top_k=limit,
            namespace=user_id,
            filter=filters,
            include_metadata=True,
        )

    def list_cols(self):
        """List all collections."""
        return self.pc.list_indexes()

    def delete_col(self, name):
        """Delete a collection."""
        self.pc.delete_index(name)

    def col_info(self, name):
        """Get information about a collection."""
        return self.pc.describe_index(name)


class AsyncPinecone_VS(VectorStoreBase):
    def __init__(self,
                 collection_name: str,
                 api_key: str, 
                 embedding_model_dims: int,
                 embedding_model_name: str,
                 similarity_metric: str = "cosine",
                 cloud: str = "aws",
                 region: str = "us-east-1"):
        self.api_key = api_key
        self.pc = PineconeAsyncio(api_key=self.api_key)
        self.collection_name = collection_name
        self.embedding_model_dims = embedding_model_dims
        self.embedding_model_name = embedding_model_name
        self.similarity_metric = similarity_metric

        spec = ServerlessSpec(cloud=cloud, region=region)
        self.create_col(self.collection_name, self.embedding_model_dims, self.similarity_metric, spec)

    async def create_col(self, name: str, vector_size: int, distance: str, spec: ServerlessSpec):
        """Create a new collection."""
        if not await self.pc.has_index(name):
            await self.pc.create_index(name=name, dimension=vector_size, metric=distance, spec=spec)
        else:
            logger.debug(f"Collection {name} already exists. Skipping creation.")

    async def insert_vectors(self, vectors: list, payloads: list = None, user_id: str|None = None, ids: list[str]|None = None):
        """Insert vectors into a collection."""
        points = []
        for v, p, i in zip(vectors, payloads, ids):
            points.append(
                {
                    "id": i,
                    "values": v,
                    "metadata": p
                }
            )
        host = await self.col_info(self.collection_name)
        host = host.host
        index = self.pc.IndexAsyncio(host)
        await index.upsert(
            vectors=points,
            namespace=user_id,
            async_req=True,
        )

    async def delete(self, ids, user_id: str|None = None):
        """Delete a vector from a collection."""
        host = await self.col_info(self.collection_name)
        host = host.host
        index = self.pc.IndexAsyncio(host)
        await index.delete(ids=ids, namespace=user_id)

    async def update(self, vector, payload, id, user_id: str|None = None):
        """Update a vector and its payload."""
        points = [{
            "id": id,
            "values": vector,
            "metadata": payload
        }]
        host = await self.col_info(self.collection_name)
        host = host.host
        index = self.pc.IndexAsyncio(host)
        await index.upsert(
            vectors=points,
            namespace=user_id,
        )

    async def query_vectors(self, vectors: list, limit: int, user_id: str|None = None, filters: dict|None = None):
        """Query for similar vectors."""
        host = await self.col_info(self.collection_name)
        host = host.host
        index = self.pc.IndexAsyncio(host)
        return await index.query(
            vector=vectors,
            top_k=limit,
            namespace=user_id,
            filter=filters,
            include_metadata=True,
        )
        
    async def list_cols(self):
        """List all collections."""
        return await self.pc.list_indexes()

    async def delete_col(self, name):
        """Delete a collection."""
        await self.pc.delete_index(name)

    async def col_info(self, name):
        """Get information about a collection."""
        return await self.pc.describe_index(name)


