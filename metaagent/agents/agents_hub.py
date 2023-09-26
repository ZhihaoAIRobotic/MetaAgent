
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


class HubStart(Executor):
    @requests(request_schema=DocList[TextDoc], response_schema=DocList[InteractionInfo])
    def sendto_agents(self, docs, **kwargs):
        return DocList[InteractionInfo]([InteractionInfo(env_info=EnvInfo(env_memory=ShortTermMemory([Info(content=docs.text, cause_by='UserInput')])))])


class HubEnd(Executor):
    @requests(request_schema=DocList[InteractionInfo], response_schema=DocList[Response])
    def recievefrom_agents(self, docs, **kwargs):
        response_audio = docs[0].env_info.env_memory.remember_by_actions(['Say']).content
        response_image = docs[0].env_info.env_memory.remember_by_actions(['DrawImage']).content
        response_videos = docs[0].env_info.env_memory.remember_by_actions(['MakeVideos']).content
        response_text = docs[0].env_info.env_memory.remember_by_actions(['WriteText']).content

        audio = DocList[ResponseListDoc]([ResponseListDoc(response_list=audio_url) for audio_url in response_audio])
        image = DocList[ResponseListDoc]([ResponseListDoc(response_list=image_url) for image_url in response_image])
        text = DocList[ResponseListDoc]([ResponseListDoc(response_list=text) for text in response_text])
        video = DocList[ResponseListDoc]([ResponseListDoc(response_list=video_url) for video_url in response_videos])

        response = Response(audio=audio, image=image, text=text, video=video)

        return DocList[Response]([response])


class AgentsHub():
    def __init__(self, workflow: str) -> None:
        self.workflow = workflow
        self.jina_dict = {'jtype': 'Flow', 'with': {'protocol': 'http', 'port': 60066}, 'executors': [{'name': 'start', 'py_modules': './agents/agents_hub.py', 'uses': 'HubStart'}, {'name': 'end', 'py_modules': './agents/agents_hub.py', 'uses': 'HubEnd'}]}

    def add_agents(self, name: str, agent: str, needs=None, **kwargs):
        # Write YAML file
        with open(self.workflow, 'w') as file:
            # py_path = os.path.abspath(sys.modules[agent.__module__].__file__)

            if needs:
                # self.jian_dict['executors'].insert(-1, {'name': str(agent.__name__), 'uses': str(agent.__name__), 'py_modules': py_path, 'needs': needs})
                self.jina_dict['executors'].insert(-1, {'name': name, 'uses': agent, 'needs': needs})
            else:
                # self.jian_dict['executors'].insert(-1, {'name': str(agent.__name__), 'uses': str(agent.__name__), 'py_modules': py_path})
                self.jina_dict['executors'].insert(-1, {'name': name, 'uses': agent})

            yaml.dump(self.jina_dict, file, sort_keys=False)

    def interacte(self):
        print('##################workflow####################')
        print(self.workflow)
        flow = Flow.load_config(self.workflow)
        flow.plot()
        with flow:
            flow.block()
