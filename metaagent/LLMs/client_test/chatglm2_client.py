from jina import Client
from docarray import DocList
from docarray.documents import TextDoc

# http://region-46.seetacloud.com:27604/
client = Client(host='0.0.0.0:63692')
response = client.post('/chat', inputs=DocList[TextDoc]([TextDoc(text='You are a dual-arm robot. You need to follow human instructions and plan actions to finish manipulation tasks.The actions include: Move_right_arm, Close_right_gripper, Move_left_arm, Close_left_gripper. There is an example, Envronment information: The initial position of the right hand is (0.50,-0.32,0.90). The position of the left hand is (0.50,0.32,0.90).  The position of green button is (0.403,-0.074,0.7), the position of the red button is (0.417,-0.017,0.7). The position of the yellow button is (0.558,-0.001,0.7) Human instruction is : Press red button. Because the position of the red button is (0.417,-0.017,0.7).So the robot action is: Move_right_arm(0.417,-0.017,0.73), Close_gripper(), Move_right_arm(0.417,-0.017,0.705), Open_gripper(). Now for a new task, Envronment information: The position of green button is (0.43,-0.04,0.7), the position of the red button is (0.467,-0.07,0.7). The position of the yellow button is (0.558,0.1,0.7).  Human instruction is : Press yellow button. What is the robot action? Please think step by step.')]))
print(f'Text: {response[0].text}')

# from jina import Executor, requests, Flow
# class MyExec(Executor):
#     @requests(on='/foo')
#     def foo(self, docs, **kwargs):
#         pass
# f = Flow().config_gateway(protocol='http',port=6006).add(uses=MyExec)
# f.expose_endpoint('/foo', summary='my endpoint')
# with f:
#     f.block()