import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import asyncio

from metaagent.memory.processing.auto_dataloader import DataLoader
from metaagent.memory.vectordb.qdrant import Qdrant_VS, AsyncQdrant_VS
from metaagent.memory.vectordb.pinecone import Pinecone_VS, AsyncPinecone_VS
from metaagent.memory.embedding.jina import JinaEmbedding
from metaagent.schema import EmbeddingText
from metaagent.memory.processing.pdf2markdown import pdf2md


async def main_jina_qdrant():
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    jina_api_key = os.getenv("JINA_API_KEY")
    jina_embedding = JinaEmbedding(api_key=jina_api_key, dimensions=256)
    qdrant = AsyncQdrant_VS(collection_name="test_jina_256", client_type="cloud", embedding_model_name="jina", api_key=qdrant_api_key, url="Your Qdrant URL", embedding_model_dims=256)

    dataloader = DataLoader()
    text_content, images = pdf2md('path/to/your/pdf/file.pdf')
    docs = dataloader.split_data_from_str(text_content, True)
    # print the sum of the length of docs
    print(sum([len(doc.page_content) for doc in docs]))
    vectors = await jina_embedding.process_data([EmbeddingText(id=i, text=doc.page_content) for i, doc in enumerate(docs)])
    await qdrant.insert_vectors(vectors=[vector['values'] for vector in vectors], ids=[vector['id'] for vector in vectors], payloads=[{"content": vector['text']} for vector in vectors])
    
    query_vector = await jina_embedding.get_embeddings(texts=["MCN公司和它的商业模式"])
    print(await qdrant.query_vectors(vectors=query_vector["data"][0]["embedding"], limit=1))


async def main_jina_pinecone():
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    jina_api_key = os.getenv("JINA_API_KEY")
    jina_embedding = JinaEmbedding(api_key=jina_api_key, dimensions=256)
    pinecone = AsyncPinecone_VS(collection_name="test-jina-256", api_key=pinecone_api_key, embedding_model_dims=256, embedding_model_name="jina")

    dataloader = DataLoader()
    docs = dataloader.split_data_from_source('path/to/your/pdf/file.pdf')
    # print the sum of the length of docs
    print(sum([len(doc.page_content) for doc in docs]))

    vectors = await jina_embedding.process_data([EmbeddingText(id=i, text=doc.page_content) for i, doc in enumerate(docs)])
    await pinecone.insert_vectors(vectors=[vector['values'] for vector in vectors], ids=[str(vector['id']) for vector in vectors], payloads=[{"content": vector['text']} for vector in vectors], user_id="test2")

    query_vector = await jina_embedding.get_embeddings(texts=["MCN公司和它的商业模式"])
    print(await pinecone.query_vectors(vectors=query_vector["data"][0]["embedding"], limit=3, user_id="test2"))
    # close pinecone if you are using asyncio
    await pinecone.pc.close()


if __name__ == "__main__":
    asyncio.run(main_jina_pinecone())
