from enum import Enum

from jina import Executor, requests, Flow
from docarray import DocList

from metaagent.information import Info
from metaagent.environment.environment import EnvInfo

class Agent_info(BaseDoc):
    name: str
    role: str
    profile: str
    goal: str
    constraints: str
    desc: str

class HubStart(Executor):
    def __init__(self) -> None:
        pass

    @requests
    def sendto_agents(self, env_info: EnvInfo, agents_info: DocList[Info]):
        # Send environment info to agents
        pass


class HubEnd(Executor):
    def __init__(self) -> None:
        pass

    @requests
    def recievefrom_agents(self):
        # Recieve new environment info from agents
        pass


class AgentsHub():
    def __init__(self) -> None:
        pass

    def add_agents(self):
        # Write YAML file
        pass

    def delete_agent(self):
        pass

    def run(self):
        workflow = Flow.load_config('agentshub.yml')
        with workflow:
            pass

    def interacte(self, env_info: DocList[Info]) -> DocList[Info]:
        # Recieve info from agents

        pass
