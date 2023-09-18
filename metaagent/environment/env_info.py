
from docarray import BaseDoc

from metaagent.memory.shortterm_memory import ShortTermMemory


class EnvInfo(BaseDoc):
    env_memory: ShortTermMemory = ShortTermMemory()  # Interaction information of all agent
    history: str = ""
