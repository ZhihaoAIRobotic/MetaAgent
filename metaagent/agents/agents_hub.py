from enum import Enum

from jina import Executor, requests, Flow
import docarray



class HubStart(Executor):
    def __init__(self) -> None:
        pass

    @requests
    def sendto_agents(self):
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
