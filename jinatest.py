from jina import Executor, requests, Flow
from docarray import DocList
from docarray import BaseDoc
import time
from docarray.index import InMemoryExactNNIndex
from typing import Iterable, Type, List

from metaagent.information import Info
# from metaagent.environment.env_info import EnvInfo
# from metaagent.agents.agent_info import AgentInfo, InteractionInfo
# from metaagent.agents.product_manager import ProductManager
from metaagent.memory.shortterm_memory import ShortTermMemory


# class Info(BaseDoc):
#     """list[<role>: <content>]"""
#     content: str = ''
#     instruction: str = ''
#     role: str = 'user'  # system / user / assistant
#     cause_by: str = ''
#     sent_from: str = ''
#     send_to: str = ''
    
#     @property
#     def Info_str(self):
#         # prefix = '-'.join([self.role, str(self.cause_by)])
#         return f"{self.role}: {self.content}"

#     def Info_str_repr(self):
#         return self.Info_str()

#     def to_dict(self) -> dict:
#         return {
#             "role": self.role,
#             "content": self.content
#         }

# class ShortTermMemory(BaseDoc):
#     storage: DocList[Info] = DocList[Info]()

#     # storage: List[str]
#     def add(self, info: Info):
#         if info in self.storage:
#             return
#         self.storage.append(info)

#     def add_batch(self, infos: DocList[Info]):
#         for info in infos:
#             self.add(info)

#     def remember(self, k=0) -> DocList[Info]:
#         """Return the most recent k memories, return all when k=0"""
#         return self.storage[-k:]
    
#     def remember_news(self, observed: DocList[Info], k=0) -> DocList[Info]:
#         """remember the most recent k memories from observed Messages, return all when k=0"""
#         already_observed = self.remember(k)
#         news = DocList[Info]()
#         for i in observed:
#             if i in already_observed:
#                 continue
#             news.append(i)
#         return news

#     def remember_by_action(self, action: str) -> DocList[Info]:
#         """Return all messages triggered by a specified Action"""
#         storage_index = InMemoryExactNNIndex[Info]()
#         storage_index.index(self.storage)
#         print(action)
#         query = {'cause_by': {'$eq': action}}
#         content = storage_index.filter(query)
#         print(content.content)
#         return content

#     def remember_by_actions(self, actions: Iterable[str]) -> DocList[Info]:
#         """Return all messages triggered by specified Actions"""
#         contents = DocList[Info]()
#         for action in actions:
#             storage_index = InMemoryExactNNIndex[Info]()
#             storage_index.index(self.storage)
#             query = {'cause_by': {'$eq': action}}
#             contents = contents + storage_index.filter(query)
#         return DocList[Info](contents)




class FooExecutor(Executor):
    def __init__(self, foo, bar: int, **kwargs):
        super().__init__(**kwargs)
        self.bar = bar

    @requests
    def foo(self, docs: DocList[ShortTermMemory], **kwargs) -> DocList[ShortTermMemory]:
        print(docs)
        docs[0].add(Info(content='foo', action='a'))


class BarExecutor(Executor):
    @requests
    def bar(self, docs: DocList[ShortTermMemory], **kwargs) -> DocList[ShortTermMemory]:
        print(docs)
        docs[0].add(Info(content='bar', action='a'))


class BazExecutor(Executor):
    @requests
    def baz(self, docs: DocList[ShortTermMemory], **kwargs) -> DocList[ShortTermMemory]:
        print('baz')
        docs[0].add(Info(content='baz', action='b'))


class MyExecutor(Executor):
    @requests
    def foo(self, docs: DocList[ShortTermMemory], **kwargs) -> DocList[ShortTermMemory]:
        # Both BarExecutor and BazExecutor only received a single Document from FooExecutor because they are run in parallel. The last Executor executor3 receives both DocLists and merges them automatically. This automated merging can be disabled with no_reduce=True. Merge and transfer are finished here. 
        print(docs)
        # print(docs[0])  # process docs here
        # print(docs[1])  # process docs here

        # f = Flow().add(uses=Executor)  # you can add your Executor to a Flow


f = (
    Flow()
    .add(uses=FooExecutor, uses_with={"foo": 1, "bar": 1}, name='fooExecutor')
    .add(uses=BarExecutor, name='barExecutor', needs='fooExecutor')
    .add(uses=MyExecutor, needs=['barExecutor'])
)

f.plot()

with f:
    b = DocList[Info]([Info(content='doc1', action='b'), Info(content='doc2', action='b')])
    a = ShortTermMemory(storage=b)
    print(a)
    d = f.post('/', inputs=a, return_type=DocList[ShortTermMemory])
    print(d)
    print([i.Info_str for i in d[0].storage])
    # print(type(d[0].storage)))
    print(DocList[Info](b+d[0].storage))
    # print(d[0].text)
    # f.block()