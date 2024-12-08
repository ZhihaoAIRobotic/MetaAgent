from collections import defaultdict
from typing import Iterable, Type, List

from docarray import BaseDoc, DocList
from docarray.index import InMemoryExactNNIndex
# from metaagent.actions.action import Action
# from metaagent.agents.comunication import Message
from metaagent.information import Info


class ShortTermMemory(DocList[Info]):

    def add(self, info: Info):
        if info in self:
            return
        self.append(info)

    def add_batch(self, infos: DocList[Info]):
        for info in infos:
            self.add(info)

    def remember(self, k=0) -> DocList[Info]:
        """Return the most recent k memories, return all when k=0"""
        return self[-k:]
    
    def remember_news(self, observed: DocList[Info], k=0) -> DocList[Info]:
        """remember the most recent k memories from observed Messages, return all when k=0"""
        already_observed = self.remember(k)
        news = DocList[Info]()
        for i in observed:
            if i.id in already_observed.id:
                continue
            news.append(i)
        return news

    def remember_by_action(self, action: str) -> DocList[Info]:
        """Return all messages triggered by a specified Action"""
        storage_index = InMemoryExactNNIndex[Info]()
        storage_index.index(self)
        query = {'cause_by': {'$eq': action}}
        content = storage_index.filter(query)
        return content

    def remember_by_actions(self, actions: Iterable[str]) -> DocList[Info]:
        """Return all messages triggered by specified Actions"""
        contents = DocList[Info]()
        for action in actions:
            storage_index = InMemoryExactNNIndex[Info]()
            storage_index.index(self)
            query = {'cause_by': {'$eq': action}}
            contents = contents + storage_index.filter(query) # become a list after + operation
        return DocList[Info](contents)
