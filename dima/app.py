import sys   
sys.path.append("/home/lzh/CodeProject/DIMA/")
from transformers import AutoTokenizer, AutoModel
from jina import Deployment, Executor, Flow, requests
from docarray.documents import TextDoc
from docarray import DocList
from dima.models import Chatglm2
from memory.processing import Dataloader
import json
import yaml

with open('./dima/config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)


def get_class(class_name):
    # 👇️ returns None if class with given name doesn't exist
    return getattr(sys.modules[__name__], class_name, None)


# Chatglm2 = get_class('Chatglm2')
f = Flow().add(name='LLM_Model', uses=get_class(config['LLM_Model']))
# dep = Deployment(uses=ChatGLM2, port=60008, protocol='http')


with f:
    f.block()
