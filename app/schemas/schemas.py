from pydantic import BaseModel


class DocsInfo(BaseModel):
    url: str
    chatId: str


class Message(BaseModel):
    message: str
