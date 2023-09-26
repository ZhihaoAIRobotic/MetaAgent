
from typing import List
from docarray import BaseDoc, DocList
from docarray.documents import TextDoc


class Info(BaseDoc):
    """list[<role>: <content>]"""
    content: List = []
    instruction: str = ''
    role: str = 'user'  # system / user / assistant
    cause_by: str = ''
    sent_from: str = ''
    send_to: str = ''
    
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


