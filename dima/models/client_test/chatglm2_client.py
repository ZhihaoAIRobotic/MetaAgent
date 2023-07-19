from jina import Client
from docarray import DocList
from docarray.documents import TextDoc


client = Client(host='0.0.0.0:54382')
response = client.post('/chat', inputs=DocList[TextDoc]([TextDoc(text='do you want to go for dinner with me?')]))
print(f'Text: {response[0].text}')