from typing import Dict, Union, TypeVar
import os
import sys
import yaml
from collections import OrderedDict

from jina import Executor, requests, Flow
from docarray import DocList, BaseDoc
from docarray.documents import TextDoc

from metaagent.information import Info, Response, ResponseListDoc
from metaagent.environment.env_info import EnvInfo
from metaagent.agents.base_agent import Agent
from metaagent.agents.agent_info import AgentInfo, InteractionInfo
from metaagent.memory.shortterm_memory import ShortTermMemory
from metaagent.minio_bucket import MINIO_OBJ


response_image = [['http://192.168.0.20:9000/metaagent/geeks.jpgX-Amz-Algorithm=AWS4-HMAC-SHA256X-Amz-Credential=minioadmin%3Aminioadmin%2F20230926%2Fus-east-1%2Fs3%2Faws4_requestX-Amz-Date=20230926T115349Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=hostX-Amz-Signature=8a48fada99f19b8af81db49e903446824ca8874c2218fbe0120ba17184d9aaf7','http://192.168.0.20:9000/metaagent/geeks.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256X-Amz-Credential=minioadmin%3Aminioadmin%2F20230926%2Fus-east-1%2Fs3%2Faws4_requestX-Amz-Date=20230926T115359Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=hostX-Amz-Signature=3a19c05c9de8ca4e03ba002898439f04505dff0ea70ba291e71f836733e9888c','http://192.168.0.20:9000/metaagent/geeks.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256X-Amz-Credential=minioadmin%3Aminioadmin%2F20230926%2Fus-east-1%2Fs3%2Faws4_requestX-Amz-Date=20230926T115409Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=hostX-Amz-Signature=8075cfdf95ced80f13d0f37be18a7829f4b4cdd99cd5f550f65202cd4a04bcb3']]
image = DocList[ResponseListDoc]([ResponseListDoc(response_list=image_url) for image_url in response_image])
response = Response(image=image)
print(response.image[0].response_list[0])