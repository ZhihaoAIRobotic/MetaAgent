from __future__ import annotations

from docarray import BaseDoc

from metaagent.memory.shortterm_memory import ShortTermMemory


class EnvInfo(BaseDoc):
    # agents_name: list[str]
    env_memory: ShortTermMemory
    history: str
