# Conmunicate with Agent Executor with jina client
from typing import List

import jina
from docarray import BaseDoc, DocList

from metaagent.agents.agents_hub import AgentsHub
from metaagent.memory.shortterm_memory import ShortTermMemory
from metaagent.environment.env_info import EnvInfo
from metaagent.information import Info
from metaagent.agents.agent_info import AgentInfo, InteractionInfo


class Environment():
    def __init__(self) -> None:
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
        self.info.env_info.env_memory.add(Info(content=task, cause_by='BossRequirement'))
        self.info.env_info.history += f"\n{Info(content=task, cause_by='BossRequirement').Info_str}"

    def get_Agents(self) -> List[str]:
        """
           Process all Role runs at once
        """
        return self.agents_name

    def run(self):
        self.add_task('give me a picture of musk')
        self.newinfo = self.agents.interacte(self.info)
        print('######################################')
        print(self.newinfo)


env = Environment()
env.run()