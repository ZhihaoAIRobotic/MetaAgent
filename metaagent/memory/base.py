from pydantic import BaseModel, Field


# class Memory(BaseModel):
#     """Interface for interacting with a document."""

#     text_content: str
#     metadata: dict = Field(default_factory=dict)

#     def __init__(self, text_content, *args, **kwargs):
#         super().__init__(text_content=text_content, *args, **kwargs)