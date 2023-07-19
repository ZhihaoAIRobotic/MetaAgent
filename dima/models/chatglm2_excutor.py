from transformers import AutoTokenizer, AutoModel
from jina import Deployment, Executor, requests
from docarray.documents import TextDoc
from docarray import DocList


class Chatglm2(Executor):
    def __init__(self, param1=1, param2=2, param3=3, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm2-6b", trust_remote_code=True)
        model = AutoModel.from_pretrained("THUDM/chatglm2-6b", trust_remote_code=True, device='cuda')
        self.model = model.eval()

    @requests(on='/chat')
    def chat(self, docs, **kwargs):
        prompt = "Girlfriend's Persona: She is a very cute girlfriend.\
                                            <START> \
                                            [DIALOGUE HISTORY] \
                                            You: hi, dear, \
                                            Girlfriend: hi, dear \
                                            You: "
        prompt2 = " Girlfriend: "
        input = prompt + docs[0].text + prompt2
        response, history = self.model.chat(self.tokenizer, input, history=[])
        # print(response)
        doc = DocList[TextDoc]([TextDoc(text=response)])
        return doc


dep = Deployment(uses=Chatglm2)


with dep:
    dep.block()



# from jina import Executor, requests, Deployment
# from docarray import DocList
# from docarray.documents import TextDoc


# class MyExecutor(Executor):
#     @requests
#     def foo(self, docs: DocList[TextDoc], **kwargs) -> DocList[TextDoc]:
#         for d in docs:
#             d.text = 'hello world'
#         return docs


# with Deployment(uses=MyExecutor) as dep:
#     response_docs = dep.post(on='/', inputs=DocList[TextDoc]([TextDoc(text='hello')]), return_type=DocList[TextDoc])
#     print(f'Text: {response_docs[0].text}')

