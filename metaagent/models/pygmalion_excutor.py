from transformers import AutoTokenizer, AutoModelForCausalLM
from jina import Deployment, Executor, requests
from docarray.documents import TextDoc
from docarray import DocList


class Pygmalion(Executor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tokenizer = AutoTokenizer.from_pretrained("PygmalionAI/pygmalion-6b")
        model = AutoModelForCausalLM.from_pretrained("PygmalionAI/pygmalion-6b", device_map="auto")
        self.model = model.eval()

    @requests(on='/chat')
    def chat(self, docs, **kwargs):
        input_text = docs[0].text 
        inputs = self.tokenizer(input_text, return_tensors="pt").to("cuda")
        outputs = self.model.generate(**inputs, max_new_tokens=15)
        response = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
        print(response)
        doc = DocList[TextDoc]([TextDoc(text=response[0])])
        return doc


if __name__ == '__main__':
    dep = Deployment(uses=Pygmalion, port=60008, protocol='http')
    with dep:
        dep.block()
