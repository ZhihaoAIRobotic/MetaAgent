from __future__ import annotations

from dataclasses import dataclass, field
from typing import Type, TypedDict

from pydantic import BaseModel

from metaagent.logs import logger
from docarray import BaseDoc


class RawInfo(BaseDoc):
    content: str
    role: str


class Info(BaseDoc):
    """list[<role>: <content>]"""
    content: str
    instruction: str
    role: str ='user'  # system / user / assistant
    cause_by: str
    sent_from: str
    send_to: str

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
