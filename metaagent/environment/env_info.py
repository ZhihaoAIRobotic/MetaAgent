
from docarray import BaseDoc

from metaagent.memory.shortterm_memory import ShortTermMemory


class EnvInfo(BaseDoc):
    # agents_name: list[str]
    env_memory: ShortTermMemory = ShortTermMemory()
    history: str = ""
