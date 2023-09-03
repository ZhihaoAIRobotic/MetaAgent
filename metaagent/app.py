# from transformers import AutoTokenizer, AutoModel
# from jina import Deployment, Executor, Flow, requests
# from docarray.documents import TextDoc
# from docarray import DocList
# from metaagent.models import Chatglm2
# from memory.processing import Dataloader
# import json
# import yaml
# from metaagent.utils import get_class

# with open('./dima/config.yaml', 'r') as config_file:
#     config = yaml.safe_load(config_file)

# # llmmodel = get_class('Chatglm2')(time=1)
# f = Flow().add(name='LLM_Model', uses=get_class(config['LLM_Model']))
# # dep = Deployment(uses=ChatGLM2, port=60008, protocol='http')


# # with f:
#     # f.block()
# # 
from metaagent.agents.base_agent import Role

def test_role_desc():
    i = Role(profile='Sales', desc='Best Seller')
    # assert i.profile == 'Sales'
    # assert i._setting.desc == 'Best Seller'


if __name__ == '__main__':
    test_role_desc()
