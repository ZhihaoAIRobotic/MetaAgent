# Conmunicate with Agent Executor with jina client
from typing import List

import jina
from jina import Executor, requests, Deployment

from docarray import BaseDoc, DocList
from docarray.documents import TextDoc
from metaagent.agents.agents_hub import AgentsHub
from metaagent.memory.shortterm_memory import ShortTermMemory
from metaagent.environment.env_info import EnvInfo
from metaagent.information import Info
from metaagent.agents.agent_info import AgentInfo, InteractionInfo

# Executor
class Environment():
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.agents = AgentsHub()
        self.info = InteractionInfo()

    def add_agent(self, agent: str) -> None:
        self.agents.add_agents(agent)
        self.agents_name.append(agent)

    def add_agents(self, agents: List[str]) -> None:
        for agent_name in agents:
            self.add_agents()

    def add_task(self, task: str) -> None:
        # TODO: Change action name
        self.info.env_info.env_memory.add(Info(content=task, cause_by='UserInput'))
        self.info.env_info.history += f"\n{Info(content=task, cause_by='UserInput').Info_str}"

    def run(self):
        response = self.agents.interacte(self.info)
        return response
    # @requests(request_schema=DocList[TextDoc], response_schema=DocList[TextDoc])
    # def run(self, docs, **kwargs):
    #     response = self.agents.interacte(self.info)
    #     return response


# dep = Deployment(name='env', uses=Environment, protocol='http', port='60688')
# with dep:
#     dep.block()
env = Environment()
env.run()