# from jina import Executor, requests, Deployment
# from docarray import BaseDoc

# # first define schemas
# class MyDocument(BaseDoc):
#     text: str

# # then define the Executor
# class MyExecutor(Executor):

#     @requests(on='/hello')
#     async def task(self, doc: MyDocument, **kwargs) -> MyDocument:
#         yield MyDocument(text=f'hello world 1')
            
# with Deployment(
#     uses=MyExecutor,
#     port=12345,
# ) as dep:
#     dep.block()


# from jina import Client
from metaagent.information import Info
from metaagent.environment.env_info import EnvInfo
from metaagent.agents.agent_info import AgentInfo, InteractionInfo
from metaagent.agents.product_manager import ProductManager
from metaagent.memory.shortterm_memory import ShortTermMemory



# client = Client(port=61149, protocol='grpc', asyncio=True)
# interactioninfo = EnvInfo()
# test = client.stream_doc('/', inputs=interactioninfo, return_type=EnvInfo)
# print(test)


from typing import Dict, Union, TypeVar
from jina import Executor, requests, Flow
from docarray import DocList, BaseDoc
from pydantic import BaseModel


T_input = TypeVar('T_input', bound='EnvInfo')
T_output = TypeVar('T_output', bound='EnvInfo')

class MyExecutor(Executor):
    @requests(on='/f')
    def foo(
        self,
        doc: T_input,
        **kwargs, 
    ) -> T_output:
        print('foo')

workflow = Flow().add(name='start', uses='MyExecutor')#.add(name='pm', uses=ProductManager, needs='start').add(name='end', uses='HubEnd', needs='pm')
        # workflow.plot()
interactioninfo = EnvInfo()
print('InteractionInfo', interactioninfo)
with workflow:
    a=workflow.post('/f', interactioninfo)
    print(a[0])
    
    
    #post('/', inputs=interactioninfo)