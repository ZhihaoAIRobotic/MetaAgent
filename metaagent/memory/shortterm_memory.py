from __future__ import annotations
from collections import defaultdict
from typing import Iterable, Type, List

from docarray import BaseDoc, DocList
from docarray.index import InMemoryExactNNIndex
# from metaagent.actions.action import Action
# from metaagent.agents.comunication import Message
from metaagent.information import Info


class SimpleDoc(BaseDoc):
    text: str


class ShortTermMemory(BaseDoc):
    storage: DocList[Info] = DocList[Info]()

    # storage: List[str]
    def add(self, info: Info):
        if info in self.storage:
            return
        self.storage.append(info)

    def add_batch(self, infos: DocList[Info]):
        for info in infos:
            self.add(info)

    def remember(self, k=0) -> DocList[Info]:
        """Return the most recent k memories, return all when k=0"""
        return self.storage[-k:]
    
    def remember_news(self, observed: DocList[Info], k=0) -> DocList[Info]:
        """remember the most recent k memories from observed Messages, return all when k=0"""
        already_observed = self.remember(k)
        news = DocList[Info]()
        for i in observed:
            if i in already_observed:
                continue
            news.append(i)
        return news

    def remember_by_action(self, action: str) -> DocList[Info]:
        """Return all messages triggered by a specified Action"""
        storage_index = InMemoryExactNNIndex[Info]()
        storage_index.index(self.storage)
        query = {'action': {'$eq': action}}
        content = storage_index.filter(query)
        return content

    def remember_by_actions(self, actions: Iterable[str]) -> DocList[Info]:
        """Return all messages triggered by specified Actions"""
        contents = DocList[Info]()
        for action in actions:
            storage_index = InMemoryExactNNIndex[Info]()
            storage_index.index(self.storage)
            query = {'action': {'$eq': action}}
            contents = contents + storage_index.filter(query)
        return DocList[Info](contents)


# b = ['a','b'] 
# a = SimpleDoc(text='doc 1')
# b = DocList[SimpleDoc]([SimpleDoc(text=f'doc {i}') for i in range(2)])
# print(a in b)

# class ShortTermMemory:
#     """The most basic memory: super-memory"""

#     def __init__(self):
#         """Initialize an empty storage list and an empty index dictionary"""
#         self.storage: list[Message] = []
#         self.index: dict[Type[Action], list[Message]] = defaultdict(list)

#     def add(self, message: Message):
#         """Add a new message to storage, while updating the index"""
#         if message in self.storage:
#             return
#         self.storage.append(message)
#         if message.cause_by:
#             self.index[message.cause_by].append(message)

#     def add_batch(self, messages: Iterable[Message]):
#         for message in messages:
#             self.add(message)

#     def get_by_role(self, role: str) -> list[Message]:
#         """Return all messages of a specified role"""
#         return [message for message in self.storage if message.role == role]

#     def get_by_content(self, content: str) -> list[Message]:
#         """Return all messages containing a specified content"""
#         return [message for message in self.storage if content in message.content]

#     def delete(self, message: Message):
#         """Delete the specified message from storage, while updating the index"""
#         self.storage.remove(message)
#         if message.cause_by and message in self.index[message.cause_by]:
#             self.index[message.cause_by].remove(message)

#     def clear(self):
#         """Clear storage and index"""
#         self.storage = []
#         self.index = defaultdict(list)

#     def count(self) -> int:
#         """Return the number of messages in storage"""
#         return len(self.storage)

#     def try_remember(self, keyword: str) -> list[Message]:
#         """Try to recall all messages containing a specified keyword"""
#         return [message for message in self.storage if keyword in message.content]

#     def get(self, k=0) -> list[Message]:
#         """Return the most recent k memories, return all when k=0"""
#         return self.storage[-k:]

#     def remember(self, observed: list[Message], k=0) -> list[Message]:
#         """remember the most recent k memories from observed Messages, return all when k=0"""
#         already_observed = self.get(k)
#         news: list[Message] = []
#         for i in observed:
#             if i in already_observed:
#                 continue
#             news.append(i)
#         return news

#     def get_by_action(self, action: Type[Action]) -> list[Message]:
#         """Return all messages triggered by a specified Action"""
#         return self.index[action]

#     def get_by_actions(self, actions: Iterable[Type[Action]]) -> list[Message]:
#         """Return all messages triggered by specified Actions"""
#         rsp = []
#         for action in actions:
#             if action not in self.index:
#                 continue
#             rsp += self.index[action]
#         return rsp