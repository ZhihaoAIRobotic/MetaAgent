from jina import Executor, requests, Flow
from docarray import DocList
from docarray import BaseDoc
import time


class SimpleDoc(BaseDoc):
    text: str


class ShortTermMemory(BaseDoc):
    storage: DocList[SimpleDoc]
    # storage: List[str]


# b = ['a','b'] 
b = DocList[SimpleDoc]([SimpleDoc(text=f'doc {i}') for i in range(2)])
a = ShortTermMemory(storage=b)


class FooExecutor(Executor):
    def __init__(self, foo, bar: int, **kwargs):
        super().__init__(**kwargs)
        self.bar = bar

    @requests
    def foo(self, docs: DocList[ShortTermMemory], **kwargs) -> DocList[ShortTermMemory]:
        print(docs)


class BarExecutor(Executor):
    @requests
    def bar(self, docs: DocList[ShortTermMemory], **kwargs) -> DocList[ShortTermMemory]:
        docs[0].storage.text = 'bar'


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
    c = DocList[ShortTermMemory]([ShortTermMemory(storage=b)])
    d = f.post('/', inputs=c, return_type=DocList[ShortTermMemory]).storage
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