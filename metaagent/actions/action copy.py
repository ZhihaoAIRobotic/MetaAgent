from typing import Any


class Action:
    def __init__(self):
        self.name = None
        self.params = None
        self.rules = None
        self.example = None

    def __call__(self, params: str,) -> Any:
        pass