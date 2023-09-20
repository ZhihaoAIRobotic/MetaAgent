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


class Environment():
    def __init__(self, workflow, **kwargs):
        self.agents = AgentsHub(workflow)
        # self.info = InteractionInfo()

    def run(self):
        response = self.agents.interacte()
        return response

