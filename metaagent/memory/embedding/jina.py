import sys
import os

if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from typing import Literal, List, Dict, Any
import aiohttp  
import asyncio  
from metaagent.memory.embedding.base import EmbeddingBase
from metaagent.schema import EmbeddingText


class JinaEmbedding(EmbeddingBase):
    def __init__(
        self, 
        api_key: str = None,
        dimensions: int = 128,
        task: Literal['text-matching', 'separation', 'classification', 'retrieval.query', 'retrieval.passage'] = 'retrieval.passage',
        concurrency_limit: int = 10
    ):
        """
        Initialize the JinaEmbedding class.
        
        Args:
            api_key: Jina API key. If None, will try to get from environment variable
            dimensions: Dimension of the embeddings
            task: Type of embedding task
            concurrency_limit: Maximum number of concurrent API calls
        """
        self.api_key = api_key or os.getenv('JINA_API_KEY')
        if not self.api_key:
            raise ValueError("JINA_API_KEY not found in environment variables")
            
        self.dimensions = dimensions
        self.task = task
        self.concurrency_limit = concurrency_limit
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

    async def send_request(
        self,
        texts: List[str],
        semaphore: asyncio.Semaphore | None = None
    ) -> Dict[str, Any]:
        """
        Fetch embeddings from the Jina API asynchronously with concurrency control.
        
        Args:
            texts: List of texts to embed
            semaphore: Semaphore for controlling concurrency
            
        Returns:
            Dictionary containing the embeddings data from Jina API
        """
        data = {
            'input': texts,
            'model': 'jina-embeddings-v3',
            'dimensions': self.dimensions,
            'task': self.task
        }
        if semaphore is not None:
            async with semaphore:
                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.post('https://api.jina.ai/v1/embeddings', headers=self.headers, json=data) as response:
                            if response.status == 200:
                                return await response.json()
                            else:
                                print(f"Error: {response.status} - {await response.text()}")
                                return None
                    except Exception as e:
                        print(f"Exception occurred: {e}")
                        return None
        else:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post('https://api.jina.ai/v1/embeddings', headers=self.headers, json=data) as response:
                        return await response.json()
                except Exception as e:
                    print(f"Exception occurred: {e}")
                    return None

    async def get_embeddings(
        self,
        texts: List[str]
    ) -> Dict[str, Any]:
        """
        Fetch embeddings from the Jina API asynchronously with concurrency control.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Dictionary containing the embeddings data from Jina API
        """
        semaphore = asyncio.Semaphore(self.concurrency_limit)
        results = await self.send_request(texts, semaphore)
        embeddings = []
        if results and "data" in results:
            for result in results["data"]:
                embeddings.append(result["embedding"])
        return embeddings

    async def process_data(self, data: List[EmbeddingText]) -> List[dict]:
        """
        Process the data to fetch embeddings concurrently.
        
        Args:
            data: List of EmbeddingText objects
            
        Returns:
            List of dictionaries containing embeddings and metadata
        """
        semaphore = asyncio.Semaphore(self.concurrency_limit)
        texts = [d.text for d in data]
        results = await self.send_request(texts, semaphore)
        vectors = []
        if results and "data" in results:
            for d, result in zip(data, results["data"]):
                embedding = result["embedding"]
                vectors.append({
                        "id": d.id,
                        "values": embedding,
                        "text": d.text
                    })
            else:
                print(f"Failed to fetch embedding for ID: {d.id}")

        return vectors

async def main():
    # Example usage
    concurrency_limit = 5
    data = [
        EmbeddingText(id="vec1", text="Apple is a popular fruit known for its sweetness and crisp texture."),
        EmbeddingText(id="vec2", text="The tech company Apple is known for its innovative products like the iPhone."),
        EmbeddingText(id="vec3", text="Many people enjoy eating apples as a healthy snack."),
        EmbeddingText(id="vec4", text="Apple Inc. has revolutionized the tech industry with its sleek designs and user-friendly interfaces."),
        EmbeddingText(id="vec5", text="An apple a day keeps the doctor away, as the saying goes."),
    ]

    # Initialize the JinaEmbedding class
    jina = JinaEmbedding(
        dimensions=256,
        task='retrieval.passage',
        concurrency_limit=concurrency_limit
    )

    print("Fetching embeddings...")
    vectors = await jina.process_data(data)

    # Simulate upserting into an index
    print("Upserting vectors into the index...")
    index = {"namespace": "ns1", "vectors": [vector["id"] for vector in vectors]}  # Replace with your actual index logic
    print(f"Created {index}")

    # Example of using get_embeddings directly
    data = [
        {"id":"vec1", "text":"Apple is a popular fruit known for its sweetness and crisp texture."},
        {"id":"vec2", "text":"The tech company Apple is known for its innovative products like the iPhone."},
        {"id":"vec3", "text":"Many people enjoy eating apples as a healthy snack."},
        {"id":"vec4", "text":"Apple Inc. has revolutionized the tech industry with its sleek designs and user-friendly interfaces."},
        {"id":"vec5", "text":"An apple a day keeps the doctor away, as the saying goes."},
    ]

    semaphore = asyncio.Semaphore(concurrency_limit)
    texts = [d["text"] for d in data]
    result = await jina.send_request(texts, semaphore)

    if result and "data" in result:
        embeddings = [item["embedding"] for item in result["data"]]
        print(f"Got {len(embeddings)} embeddings directly")
        # Create vectors from the embeddings
        vectors = []
        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            vectors.append({
                "id": data[i]["id"],
                "values": embedding,
                "metadata": {'text': text}
            })
        
        print("Upserting vectors into the index...")
        index = {"namespace": "ns2", "vectors": [vector["id"] for vector in vectors]}
        print(f"Created {index} ")
    else:
        print("Failed to get embeddings directly")

if __name__ == "__main__":
    asyncio.run(main())  
