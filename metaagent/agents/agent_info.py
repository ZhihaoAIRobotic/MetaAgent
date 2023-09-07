from __future__ import annotations

from docarray import BaseDoc, DocList
from typing import List

from metaagent.memory.shortterm_memory import ShortTermMemory
from metaagent.information import Info


class AgentInfo(BaseDoc):
    name: str
    profile: str
    goal: str
    constraints: str
    memory: ShortTermMemory = ShortTermMemory()
    news: DocList[Info] = DocList[Info]()
    watch_action_results: List[str] = []

    @property
    def history(self) -> list[str]:
        info_strs = self.memory.remember()
        return [i.Info_str for i in info_strs]
    
    @property
    def important_memory(self) -> list[str]:
        """Get the information corresponding to the watched actions"""
        return self.memory.remember_by_action(self.watch_action_results)
    
    @property
    def role_id(self) -> str:
        return f"{self.name}({self.profile})"
    