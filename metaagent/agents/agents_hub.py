
from typing import Dict, Union, TypeVar

from jina import Executor, requests, Flow
from docarray import DocList
from docarray.documents import TextDoc

from metaagent.information import Info
from metaagent.environment.env_info import EnvInfo
from metaagent.agents.agent_info import AgentInfo, InteractionInfo
from metaagent.agents.product_manager import ProductManager
from metaagent.agents.multi_modal_agent import MultiModelAgent
from metaagent.memory.shortterm_memory import ShortTermMemory
from metaagent.minio_bucket import MINIO_OBJ


# InteractionInfoType = TypeVar('InteractionInfoType', bound='InteractionInfo')

class HubStart(Executor):
    @requests(request_schema=DocList[TextDoc], response_schema=DocList[InteractionInfo])
    def sendto_agents(self, docs, **kwargs):
        # Send environment info to agents
        # print('env_info', docs[0].env_info.env_memory)
        return DocList[InteractionInfo]([InteractionInfo(env_info=EnvInfo(env_memory=ShortTermMemory([Info(content=docs[0].text, cause_by='UserInput')])))])


class HubEnd(Executor):
    @requests(request_schema=DocList[InteractionInfo], response_schema=DocList[TextDoc])
    def recievefrom_agents(self, docs, **kwargs):
        # Recieve new environment info from agents
        # docs[0].env_info.env_shorterm_memory.add(Info(content='doc1', cause_by='Agent'))
        # print(docs[0].env_info.env_shorterm_memory.remember_by_actions(['Agent'])[0].content)
        # print('env_info', docs[0].env_info.env_memory)
        return DocList[TextDoc]([TextDoc(text=docs[0].env_info.env_memory.content[-1])])


class AgentsHub():
    def __init__(self) -> None:
        pass

    def add_agents(self):
        # Write YAML file
        pass

    def delete_agent(self):
        pass

    def interacte(self, input: DocList[TextDoc], **kwargs):
        # workflow = Flow.load_config('agentshub.yml')
        workflow = (Flow(protocol='http', port=60596).add(name='start', uses=HubStart).add(name='mma', uses=MultiModelAgent).add(name='end', uses=HubEnd))
        with workflow:
        #     agents_feedback = workflow.post('/', inputs=input, return_type=DocList[TextDoc])
        # return agents_feedback
            feedback = workflow.block()
        # return agents_feedback[0]
        # print(feedback)
        # return feedback[0]
        # block()  #, return_type=InteractionInfo
        # print('######################################')
        # print(agents_feedback[0])
        # return agents_feedback
#, return_type=(EnvInfo, DocList[AgentInfo]
# workflow = Flow().add(name='startsss', uses='HubEnd')#.add(name='pm', uses=ProductManager, needs='start').add(name='end', uses='HubEnd', needs='pm')
# workflow = Deployment(name='startsss', uses='HubEnd')
# interactioninfo = DocList[AgentInfo]([AgentInfo()])
# print('InteractionInfo', interactioninfo)
# b = DocList[Info]([Info(content='doc1', action='b'), Info(content='doc2', action='b')])
# interactioninfo = ShortTermMemory(storage=b)
# with workflow:
#     agents_feedback = workflow.post('/', inputs=interactioninfo, return_type=DocList[ShortTermMemory])
# print('######################################')
# print(agents_feedback[0])