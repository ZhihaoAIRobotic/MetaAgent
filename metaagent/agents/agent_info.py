
from docarray import BaseDoc, DocList
from typing import List

from metaagent.memory.shortterm_memory import ShortTermMemory
from metaagent.information import Info
from metaagent.environment.env_info import EnvInfo


class AgentInfo(BaseDoc):
    name: str = ''
    profile: str = ''
    goal: str = ''
    constraints: str = ''
    memory: ShortTermMemory = ShortTermMemory()
    news: DocList[Info] = DocList[Info]()
    watch_action_results: List[str] = []

    @property
    def history(self) -> List[str]:
        info_strs = self.memory.remember()
        return [i.Info_str for i in info_strs]

    @property
    def important_memory(self) -> List[str]:
        """Get the information corresponding to the watched actions"""
        return self.memory.remember_by_actions(self.watch_action_results).content

    @property
    def role_id(self) -> str:
        return f"{self.name}({self.profile})"


class InteractionInfo(BaseDoc):
    env_info: EnvInfo = EnvInfo()
    agents_info: DocList[AgentInfo] = DocList[AgentInfo]()
    # agent_memory: DocList[ShortTermMemory] = DocList[ShortTermMemory]()
    # env_memory: ShortTermMemory = ShortTermMemory()
