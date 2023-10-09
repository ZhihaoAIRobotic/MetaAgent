from transformers import AutoTokenizer, AutoModel
from jina import Deployment, Executor, requests
from docarray.documents import TextDoc
from docarray import DocList


class Chatglm2(Executor):
    def __init__(self, time=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(time)
        self.tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm2-6b", trust_remote_code=True)
        model = AutoModel.from_pretrained("THUDM/chatglm2-6b", trust_remote_code=True, device='cuda')
        self.model = model.eval()

    @requests(on='/chat')
    def chat(self, docs, **kwargs):
        input = docs[0].text 
        response, history = self.model.chat(self.tokenizer, input, history=[])
        # print(response)
        doc = DocList[TextDoc]([TextDoc(text=response)])
        return doc


if __name__ == '__main__':
    dep = Deployment(uses=Chatglm2, port=60008, protocol='http')
    with dep:
        dep.block()
