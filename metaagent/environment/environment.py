# Conmunicate with Agent Executor with jina client
from typing import List

import jina
from docarray import BaseDoc, DocList

from metaagent.agents.agents_hub import AgentsHub
from metaagent.memory.shortterm_memory import ShortTermMemory
from metaagent.environment.env_info import EnvInfo


class Environment():
    def __init__(self) -> None:
        self.agents = AgentsHub()
        self.info = EnvInfo(agents_name=[], env_memory=ShortTermMemory, history='')

    def add_agent(self, agent: str) -> None:
        self.agents.add_agents(agent)
        self.agents_name.append(agent)
        
    def add_agents(self, agents: List[str]) -> None:
        for agent_name in agents:
            self.add_agents()

    def get_Agents(self) -> List[str]:
        """获得环境内的所有角色
           Process all Role runs at once
        """
        return self.agents_name

    def run(self):
        self.agents.run()
        self.info = self.agents.interacte(self.info)

