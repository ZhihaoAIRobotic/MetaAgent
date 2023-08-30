import sys   
sys.path.append("/home/lzh/CodeProject/DIMA/")
from transformers import AutoTokenizer, AutoModel
from jina import Deployment, Executor, Flow, requests
from docarray.documents import TextDoc
from docarray import DocList
from dima.models import Chatglm2
from memory.processing import Dataloader




def get_class(class_name):
    # 👇️ returns None if class with given name doesn't exist
    return getattr(sys.modules[__name__], class_name, None)

 

f = Flow().add(name='myexec1', uses=Chatglm2)
# dep = Deployment(uses=ChatGLM2, port=60008, protocol='http')


with f:
    f.block()
