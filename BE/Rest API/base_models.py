from pydantic import BaseModel
from typing import List, Optional


class User_login(BaseModel):
    username: str
    password: str

class User(BaseModel):
    username: str
    password: str
    htw_mail: str
    htw_password: str

class Step(BaseModel):
    id: str
    name: str
    type: str
    threadId: str
    disableFeedback: bool
    streaming: bool
    waitForAnswer: bool = False  # Optional field with default value
    isError: bool = False  # Optional field with default value
    output: Optional[str]  # Allow output to be None
    createdAt: Optional[str]  # Allow createdAt to be None
    start: Optional[str]  # Allow start to be None
    end: Optional[str]  # Allow end to be None
    generation: Optional[dict]  # Change JSON to dict for Pydantic
    language: Optional[str]  # Allow language to be None
    indent: Optional[int]

class Thread(BaseModel):
    name: str
    userId: str

class Thread_incl_Steps(BaseModel):
    id: str
    name: str
    createdAt: str
    userId: str
    userIdentifier: str
    steps: List[Step]

class Message(BaseModel):
    content: str