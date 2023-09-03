from __future__ import annotations

from dataclasses import dataclass, field
from typing import Type, TypedDict

from pydantic import BaseModel

from metaagent.logs import logger


class RawMessage(TypedDict):
    content: str
    role: str


@dataclass
class Message:
    """list[<role>: <content>]"""
    content: str
    instruct_content: BaseModel = field(default=None)
    role: str = field(default='user')  # system / user / assistant
    cause_by: Type["Action"] = field(default="")
    sent_from: str = field(default="")
    send_to: str = field(default="")

    def __str__(self):
        # prefix = '-'.join([self.role, str(self.cause_by)])
        return f"{self.role}: {self.content}"

    def __repr__(self):
        return self.__str__()

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content
        }
