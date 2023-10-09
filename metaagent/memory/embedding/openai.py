from typing import List
from abc import ABC, abstractmethod
import openai


class OpenAiEmbedding:
    def __init__(self, api_key, model="text-embedding-ada-002"):
        self.model = model
        self.api_key = api_key

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Compute doc embeddings using a HuggingFace transformer model.

        Args:
            texts: The list of texts to embed.

        Returns:
            List of embeddings, one for each text.
        """
        texts = list(map(lambda x: x.replace("\n", " "), texts))
        response = openai.Embedding.create(
                api_key=self.api_key,
                input=texts,
                engine=self.model
            )
        embeddings = response['data'][:]['embedding']
        return embeddings.tolist()

    def embed_query(self, text) -> List[float]:
        try:
            response = openai.Embedding.create(
                api_key=self.api_key,
                input=[text],
                engine=self.model
            )
            return response['data'][0]['embedding']
        except Exception as exception:
            return {"error": exception}