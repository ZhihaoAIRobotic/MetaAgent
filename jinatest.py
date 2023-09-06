from jina import Executor, requests, Flow
from docarray import DocList
from docarray import BaseDoc
import time
from docarray.index import InMemoryExactNNIndex


class Info(BaseDoc):
    text: str
    action: str


class ShortTermMemory(BaseDoc):
    storage: DocList[Info]

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


# b = ['a','b'] 



class FooExecutor(Executor):
    def __init__(self, foo, bar: int, **kwargs):
        super().__init__(**kwargs)
        self.bar = bar

    @requests
    def foo(self, docs: DocList[ShortTermMemory], **kwargs) -> DocList[ShortTermMemory]:
        docs[0].add(Info(text='foo', action='a'))


class BarExecutor(Executor):
    @requests
    def bar(self, docs: DocList[ShortTermMemory], **kwargs) -> DocList[ShortTermMemory]:
        print("query content: ", docs[0].remember_by_action('a').text)


class BazExecutor(Executor):
    @requests
    def baz(self, docs: DocList[ShortTermMemory], **kwargs) -> DocList[ShortTermMemory]:
        docs[0].storage.text = 'bar'


class MyExecutor(Executor):
    @requests
    def foo(self, docs: DocList[ShortTermMemory], **kwargs) -> DocList[ShortTermMemory]:
        print(docs)  # process docs here

        # f = Flow().add(uses=Executor)  # you can add your Executor to a Flow


f = (
    Flow()
    .add(uses=FooExecutor, uses_with={"foo": 1, "bar": 1}, name='fooExecutor')
    .add(uses=BarExecutor, name='barExecutor', needs='fooExecutor')
    .add(uses=BazExecutor, name='bazExecutor', needs='fooExecutor')
    .add(uses=MyExecutor, needs=['barExecutor', 'bazExecutor'])
)



with f:
    b = DocList[Info]([Info(text='doc1', action='a'), Info(text='doc2', action='b')])
    a = ShortTermMemory(storage=b)
    d = f.post('/', inputs=a, return_type=DocList[ShortTermMemory]).storage
    print(d[0].text)
    # f.block()


# from jina import Client, Executor, Deployment, requests
# from docarray import BaseDoc

# class MyExecutor(Executor):

#     @requests
#     def foo(self, parameters, **kwargs):
#         print(parameters['hello'])

# dep = Deployment(uses=MyExecutor)



# with dep:
#     client = Client(port=dep.port)
#     client.post('/', BaseDoc(), parameters={'hello': dog})