from sqlalchemy import Column, JSON, String, ForeignKey, Text, Boolean, Integer, ARRAY
from sqlalchemy.ext.declarative import declarative_base
import uuid
from literalai.helper import utc_now
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    htw_mail = Column(String, primary_key=True, nullable=False, index=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    createdAt = Column(String, nullable=False)
    htw_password = Column(String, nullable=False)

    def __init__(self,htw_mail, username, password, createdAt, htw_password):
        self.username = username
        self.password = password
        self.createdAt = createdAt
        self.htw_mail = htw_mail
        self.htw_password = htw_password


class Thread(Base):
    __tablename__ = "threads"

    id = Column(String, primary_key=True)
    createdAt = Column(String)
    name = Column(String)
    userId = Column(String, ForeignKey("users.htw_mail"))

    def __init__(self, id, name, userId):
        self.id = id
        self.createdAt = utc_now()
        self.name = name
        self.userId = userId

    user = relationship("User", backref="threads")

#TODO: change from chainlit to streamlit requirements
class Step(Base):
    __tablename__ = "steps"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)  # Not Null constraint
    type = Column(String, nullable=False)  # Not Null constraint
    threadId = Column(String, ForeignKey("threads.id"), nullable=False)  # Not Null constraint
    disableFeedback = Column(Boolean, nullable=False)  # Not Null constraint
    streaming = Column(Boolean, nullable=False)  # Not Null constraint
    waitForAnswer = Column(Boolean)
    isError = Column(Boolean)
    output = Column(Text)
    createdAt = Column(Text)
    start = Column(Text)
    end = Column(Text)
    generation = Column(JSON)
    language = Column(Text)
    indent = Column(Integer)  # Use Integer instead of INT

    thread = relationship("Thread", backref="steps")


