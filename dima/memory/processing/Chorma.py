import os

from langchain.chains import VectorDBQA
from auto_dataloader import *
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma




class DIMAVectorStore():

    """KnownLedge2Vector class is order to load document to vector
    and persist to vector store.

        Args:
           - model_name

        Usage:
            k2v = KnownLedge2Vector()
            persist_dir = os.path.join(VECTORE_PATH, ".vectordb")
            print(persist_dir)
            for s, dc in k2v.query("what is oceanbase?"):
                print(s, dc.page_content, dc.metadata)

    """
    def __init__(self, datasets_dir, vector_path, top_k, embeddings, dataloader):
        self.datasets_dir = datasets_dir
        self.vector_path = vector_path
        self.dataloader = dataloader
        self.top_k = top_k
        self.embeddings = HuggingFaceEmbeddings(model_name=embeddings)

    def init_vector_store(self):
        persist_dir = os.path.join(self.vector_path, ".vectordb")
        print("Vector store Persist address is: ", persist_dir)
        if os.path.exists(persist_dir):
            # Loader from local file.
            print("Loader data from local persist vector file...")
            vector_store = Chroma(
                persist_directory=persist_dir, embedding_function=self.embeddings
            )
            # vector_store.add_documents(documents=documents)
        else:
            documents = self.dataloader.split_docs(self.datasets_dir)
            # reinit
            vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=persist_dir,
            )
            vector_store.persist()
        return vector_store

    def query(self, q):
        """Query similar doc from Vector"""
        vector_store = self.init_vector_store()
        docs = vector_store.similarity_search_with_score(q, k=self.top_k)
        for doc in docs:
            dc, s = doc
            yield s, dc

def main():
    parser = argparse.ArgumentParser(
    description='Start LLM and Embeddings models as a service.')
    parser.add_argument('--datasets_dir', type=str, default='/home/wy/桌面/datasets')
    parser.add_argument('--llm_model_name', type=str, default='chatglm2-6b')
    parser.add_argument('--vector_path', type=str, default='/home/wy/桌面/vector_store')
    parser.add_argument('--top_k', type=int, default=10)

    args, _ = parser.parse_known_args()
    dataloader = DIMAdataloader()
    VectorStore = DIMAVectorStore(datasets_dir=args.datasets_dir, vector_path=args.vector_path,
                                  top_k=args.top_k, embeddings=args.llm_model_name, dataloader=dataloader)


    VectorStore.query("what is the deep learning technique?")

if __name__ == '__main__':
    main()

