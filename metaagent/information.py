
from docarray import BaseDoc, DocList
from docarray.documents import TextDoc

class Info(BaseDoc):
    """list[<role>: <content>]"""
    content: str = ''
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

class Response(BaseDoc):
    image: DocList[TextDoc] = DocList[TextDoc]()
    text: DocList[TextDoc] = DocList[TextDoc]()
    audio: DocList[TextDoc] = DocList[TextDoc]()
    video: DocList[TextDoc] = DocList[TextDoc]()