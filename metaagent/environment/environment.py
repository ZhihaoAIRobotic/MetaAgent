# Conmunicate with Agent Executor with jina client
from typing import List

import jina
from docarray import BaseDoc, DocList

from metaagent.agents.agents_hub import AgentHub
from metaagent.agents.base_agent import Agent
from metaagent.information import Info


    


class Environment():
    def __init__(self) -> None:
        self.agents = AgentHub()
        self.info = DocList[Info]()
        
    def add_agents(self, agents: List[str]) -> None:
        for agent_name in agents:
            self.agents.add_agents()

    def delete_agent(self):
        pass

    def interacte(self):
        pass

    def run(self):
        self.agents.run()