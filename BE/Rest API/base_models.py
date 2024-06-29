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


class Thread(BaseModel):
    name: str
    userId: str


class Message(BaseModel):
    content: str
    role: str
    thread_id: str


class AI_Message(BaseModel):
    content: str
    topic: str
    user_id: str
    role: str
    thread_id: str

class CourseList(BaseModel):
    courses: List
