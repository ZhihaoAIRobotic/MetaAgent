
from typing import List
from docarray import BaseDoc, DocList
from docarray.documents import TextDoc


class Info(BaseDoc):
    """list[<role>: <content>]"""
    content: List = []
    instruction: str = ''
    agent_id: str = ''  # the profile of the agent
    role: str = 'user'  # system / user / assistant
    cause_by: str = ''

    @property
    def Info_str(self):
        # prefix = '-'.join([self.role, str(self.cause_by)])
        return f"{self.role}: {self.content}"

    def Info_str_repr(self):
        return self.Info_str()

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content
        }


class ResponseListDoc(BaseDoc):
    response_list: List[str] = []


class Response(BaseDoc):
    image: DocList[ResponseListDoc] = DocList[ResponseListDoc]()
    text: DocList[ResponseListDoc] = DocList[ResponseListDoc]()
    audio: DocList[ResponseListDoc] = DocList[ResponseListDoc]()
    video: DocList[ResponseListDoc] = DocList[ResponseListDoc]()


