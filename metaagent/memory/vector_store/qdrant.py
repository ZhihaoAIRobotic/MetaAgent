from typing import Union, List
from qdrant_client import QdrantClient
from qdrant_client.models import (
	Distance,
	VectorParams,
	PointStruct,
	PointIdsList,
	Filter,
    MatchValue,
    Range,
    FieldCondition
)

from metaagent.logs import logger
from metaagent.memory.vector_store.base import VectorStoreBase


class Qdrant(VectorStoreBase):
    def __init__(
		self,
		embedding_model: Union[str, List[dict]],
		collection_name: str,
		embedding_batch: int = 100,
		client_type: str = "docker",
        embedding_model_dims: int = 1536,
        similarity_metric: str = "cosine",
		url: str = "http://localhost:6333",
		host: str = "",
		api_key: str = None,
		ingest_batch: int = 64,
        on_disk: bool = False,
		parallel: int = 1,
		max_retries: int = 3):
        self.collection_name = collection_name
        self.ingest_batch = ingest_batch
        self.parallel = parallel
        self.max_retries = max_retries   

        
        if client_type == "docker":
            self.client = QdrantClient(
                url=url,
            )
        elif client_type == "cloud":
            self.client = QdrantClient(
                host=host,
                api_key=api_key,
            )
        else:
            raise ValueError(
                f"client_type {client_type} is not supported\n"
                "supported client types are: docker, cloud"
            )   
        self.create_col(collection_name, embedding_model_dims, on_disk, similarity_metric)


    def create_col(self, collection_name: str, vector_size: int, on_disk: bool = False, similarity_metric: str = "cosine"):
        """
        Create a new collection.

        Args:
            vector_size (int): Size of the vectors to be stored.
            on_disk (bool): Enables persistent storage.
            distance (Distance, optional): Distance metric for vector similarity. Defaults to Distance.COSINE.
        """
        # Skip creating collection if already exists
        if similarity_metric == "cosine":
            distance = Distance.COSINE
        elif similarity_metric == "ip":
            distance = Distance.DOT
        elif similarity_metric == "l2":
            distance = Distance.EUCLID
        else:
            raise ValueError(
                f"similarity_metric {similarity_metric} is not supported\n"
                "supported similarity metrics are: cosine, ip, l2")
     
        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance,
                    on_disk=on_disk
                ),
            )
        else:
            logger.debug(f"Collection {self.collection_name} already exists. Skipping creation.")
        
        return True

    def query(self, query: list, limit: int = 5, filters: dict = None) -> list:
        """
        Search for similar vectors.

        Args:
            query (list): Query vector.
            limit (int, optional): Number of results to return. Defaults to 5.
            filters (dict, optional): Filters to apply to the search. Defaults to None.

        Returns:
            list: Search results.
        """
        query_filter = self._create_filter(filters) if filters else None
        hits = self.client.query_points(
            collection_name=self.collection_name,
            query_vector=query,
            query_filter=query_filter,
            limit=limit,
        )
        return hits
    
    def get(self, vector_id: int) -> dict:
        """
        Retrieve a vector by ID.

        Args:
            vector_id (int): ID of the vector to retrieve.

        Returns:
            dict: Retrieved vector.
        """
        result = self.client.retrieve(collection_name=self.collection_name, ids=[vector_id], with_payload=True)
        return result[0] if result else None
    
    def insert(self, vectors: list, payloads: list = None, ids: list = None):
        """
        Insert vectors into a collection.

        Args:
            vectors (list): List of vectors to insert.
            payloads (list, optional): List of payloads corresponding to vectors. Defaults to None.
            ids (list, optional): List of IDs corresponding to vectors. Defaults to None.
        """
        logger.info(f"Inserting {len(vectors)} vectors into collection {self.collection_name}")
        points = [
            PointStruct(
                id=idx if ids is None else ids[idx],
                vector=vector,
                payload=payloads[idx] if payloads else {},
            )
            for idx, vector in enumerate(vectors)
        ]
        self.client.upsert(collection_name=self.collection_name, points=points)

    def delete(self, vector_id: int):
        """
        Delete a vector by ID.

        Args:
            vector_id (int): ID of the vector to delete.
        """
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=PointIdsList(
                points=[vector_id],
            ),
        )

    def update(self, vector_id: int, vector: list = None, payload: dict = None):
        """
        Update a vector and its payload.

        Args:
            vector_id (int): ID of the vector to update.
            vector (list, optional): Updated vector. Defaults to None.
            payload (dict, optional): Updated payload. Defaults to None.
        """
        point = PointStruct(id=vector_id, vector=vector, payload=payload)
        self.client.upsert(collection_name=self.collection_name, points=[point])

    def _create_filter(self, filters: dict) -> Filter:
        """
        Create a Filter object from the provided filters.

        Args:
            filters (dict): Filters to apply.

        Returns:
            Filter: The created Filter object.
        """
        conditions = []
        for key, value in filters.items():
            if isinstance(value, dict) and "gte" in value and "lte" in value:
                conditions.append(FieldCondition(key=key, range=Range(gte=value["gte"], lte=value["lte"])))
            else:
                conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
        return Filter(must=conditions) if conditions else None

    def list_cols(self) -> list:
        """
        List all collections.

        Returns:
            list: List of collection names.
        """
        return self.client.get_collections()

    def delete_col(self):
        """Delete a collection."""
        logger.warning(f"Deleting collection {self.collection_name}")
        self.client.delete_collection(collection_name=self.collection_name)

    def col_info(self) -> dict:
        """
        Get information about a collection.

        Returns:
            dict: Collection information.
        """
        return self.client.get_collection(collection_name=self.collection_name)
