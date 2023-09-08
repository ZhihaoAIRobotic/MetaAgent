
from typing import Dict, Union, TypeVar

from jina import Executor, requests, Flow
from docarray import DocList

from metaagent.information import Info
from metaagent.environment.env_info import EnvInfo
from metaagent.agents.agent_info import AgentInfo, InteractionInfo
from metaagent.agents.product_manager import ProductManager
from metaagent.memory.shortterm_memory import ShortTermMemory


# InteractionInfoType = TypeVar('InteractionInfoType', bound='InteractionInfo')

class HubStart(Executor):
    @requests
    def sendto_agents(self, docs: DocList[InteractionInfo], **kwargs) -> DocList[InteractionInfo]:
        # Send environment info to agents
        print('env_info', docs[0].env_info.env_memory)



class HubEnd(Executor):
    @requests
    def recievefrom_agents(self, docs: DocList[InteractionInfo], **kwargs) -> DocList[InteractionInfo]: 
        # Recieve new environment info from agents
        # docs[0].env_info.env_shorterm_memory.add(Info(content='doc1', cause_by='Agent'))
        # print(docs[0].env_info.env_shorterm_memory.remember_by_actions(['Agent'])[0].content)
        print('env_info', docs[0].env_info.env_memory)

        


class AgentsHub():
    def __init__(self) -> None:
        pass

    def add_agents(self):
        # Write YAML file
        pass

    def delete_agent(self):
        pass

    def interacte(self, interactioninfo: InteractionInfo, **kwargs):
        # workflow = Flow.load_config('agentshub.yml')
        workflow = Flow().add(name='start', uses='HubStart').add(name='pm', uses=ProductManager, needs='start').add(name='end', uses='HubEnd', needs='pm')
        # workflow.plot()
        interactioninfo_list = DocList[InteractionInfo]([interactioninfo])
        print('InteractionInfo', interactioninfo)
        with workflow:
            feedback = workflow.post('/', inputs=interactioninfo_list, return_type=DocList[InteractionInfo])
        return feedback[0]
            #block()  #, return_type=InteractionInfo
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
