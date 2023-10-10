
from metaagent.utils import get_class
from jina import Deployment, Executor, requests
from docarray import DocumentArray, Document
from docarray import Document as Jocument
from metaagent.memory.embedding.huggingface import HuggingFaceEmbeddings
from metaagent.memory.vector_store.chroma import ChromaVS
from metaagent.memory.processing.auto_dataloader import Dataloader


class KnowledgeDatabase(Executor):
    def __init__(self, file_path, vector_store="ChromaVS", collection_name=None, embedding_model="HuggingFaceEmbeddings", text_field=None,  **kwargs):
        super(KnowledgeDatabase, self).__init__()
        self.data_loader = Dataloader()
        docs = self.data_loader(file_path)
        self.vector_store = get_class(vector_store)(collection_name=collection_name,
                                        embedding_model=get_class(embedding_model), text_field=text_field)
        ids = self.vector_store.add_texts(docs)
        print("Load %d data from local persist vector file..."%ids)

    @requests(on='/find_matching_text')
    def find_matching_text(self, query: str, **kwargs) -> DocumentArray:
        results = self.vector_store.get_matching_text(query)
        results = DocumentArray([Jocument(text=results)])
        return results


def main():
    parser = argparse.ArgumentParser(
    description='Start LLM and Embeddings models as a service.')
    parser.add_argument('--file_path', type=str, default='/home/wy/桌面/datasets/taxonomy-IJCV.pdf')
    parser.add_argument('--collection_name', type=str, default='computer vision')
    parser.add_argument('--embedding_model', type=str, default='/home/wy/桌面/datasets/taxonomy-IJCV.pdf')
    parser.add_argument('--text_field', type=str, default='stereo vision')
    args, _ = parser.parse_known_args()

    query = 'what is the binocular vision?'
    knowledgeDatabaseChroma = KnowledgeDatabaseChroma(args.file_path, args.ccollection_name, args.embedding_model, args.text_field)

    results = knowledgeDatabaseChroma.find_matching_text(query)
    print(results)

if __name__ == '__main__':
    main()