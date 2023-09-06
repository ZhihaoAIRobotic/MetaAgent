from __future__ import annotations

from metaagent.logs import logger
from metaagent.memory.shortterm_memory import Memory
from metaagent.memory.memory_storage import MemoryStorage
from metaagent.information import Message


class LongTermMemory(Memory):
    """
    The Long-term memory for Roles
    - recover memory when it staruped
    - update memory when it changed
    """

    def __init__(self):
        self.memory_storage: MemoryStorage = MemoryStorage()
        super(LongTermMemory, self).__init__()
        self.rc = None  # RoleContext
        self.msg_from_recover = False

    def recover_memory(self, role_id: str, rc: "RoleContext"):
        messages = self.memory_storage.recover_memory(role_id)
        self.rc = rc
        if not self.memory_storage.is_initialized:
            logger.warning(f"It may the first time to run Agent {role_id}, the long-term memory is empty")
        else:
            logger.warning(
                f"Agent {role_id} has existed memory storage with {len(messages)} messages " f"and has recovered them."
            )
        self.msg_from_recover = True
        self.add_batch(messages)
        self.msg_from_recover = False

    def add(self, message: Message):
        super(LongTermMemory, self).add(message)
        for action in self.rc.watch:
            if message.cause_by == action and not self.msg_from_recover:
                # currently, only add role's watching messages to its memory_storage
                # and ignore adding messages from recover repeatedly
                self.memory_storage.add(message)

    def remember(self, observed: list[Message], k=0) -> list[Message]:
        """
        remember the most similar k memories from observed Messages, return all when k=0
            1. remember the short-term memory(stm) news
            2. integrate the stm news with ltm(long-term memory) news
        """
        stm_news = super(LongTermMemory, self).remember(observed, k=k)  # shot-term memory news
        if not self.memory_storage.is_initialized:
            # memory_storage hasn't initialized, use default `remember` to get stm_news
            return stm_news

        ltm_news: list[Message] = []
        for mem in stm_news:
            # integrate stm & ltm
            mem_searched = self.memory_storage.search(mem)
            if len(mem_searched) > 0:
                ltm_news.append(mem)
        return ltm_news[-k:]

    def delete(self, message: Message):
        super(LongTermMemory, self).delete(message)
        # TODO delete message in memory_storage

    def clear(self):
        super(LongTermMemory, self).clear()
        self.memory_storage.clean()