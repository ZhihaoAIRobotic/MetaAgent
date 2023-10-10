from typing import List, Dict

from metaagent.logs import logger
from metaagent.memory.shortterm_memory import Memory
# from metaagent.memory.memory_storage import MemoryStorage
from metaagent.information import Message
from metaagent.memory.vector_store.chroma import ChromaVS


class LongTermMemory():
    """
    The Long-term memory for Roles
    - recover memory when it staruped
    - update memory when it changed
    """

    def __init__(self, workid, embedding_model: str = None):
        self.rc = None
        self.memory_storage = ChromaVS(workid, embedding_model)

    def remember_infos(self, message: Message):
        """
        remember the message into memory_storage
        """
        # TODO add message to memory_storage
        self.memory_storage.add(message)

    def remember_knowledge(self, message: Message):
        """
        remember the message into memory_storage
        """
        # TODO add message to memory_storage
        self.memory_storage.add(message)

    def recall_from_infors(self, observed: List[Message], k=0) -> List[Message]:
        """
        remember the most similar k memories from observed Messages, return all when k=0
            1. remember the short-term memory(stm) news
            2. integrate the stm news with ltm(long-term memory) news
        """
        return

    def recall_from_knowledge(self, observed: List[Message], k=0) -> List[Message]:
        """
        remember the most similar k memories from observed Messages, return all when k=0
            1. remember the short-term memory(stm) news
            2. integrate the stm news with ltm(long-term memory) news
        """
        return 
    
    def forget(self, message: Message):
        '''
        delete specific content in memory_storage
        '''
        # TODO delete message in memory_storage

    def clear(self):
        '''
        clear all content in memory_storage
        '''
        # TODO delete message in memory_storage

