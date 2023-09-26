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

from metaagent.environment.environment import Environment
# from metaagent.agents.multi_modal_agent import MultiModelAgent


if __name__ == '__main__':
    workflow = '/home/lzh/CodeProject/DIMA/metaagent/workflow.yml'
    env = Environment(workflow)
    env.agents.add_agents('writer_agent', '/home/lzh/CodeProject/DIMA/metaagent/agents/writer_agent.yml')
    env.agents.add_agents('story_board_agent', '/home/lzh/CodeProject/DIMA/metaagent/agents/story_board_agent.yml', needs=['writer_agent'])
    env.agents.add_agents('cartoonist_agent', '/home/lzh/CodeProject/DIMA/metaagent/agents/cartoonist_agent.yml', needs=['story_board_agent'])
    env.run()
