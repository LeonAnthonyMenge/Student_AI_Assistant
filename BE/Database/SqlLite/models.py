from sqlalchemy import Column, JSON, String, ForeignKey, ARRAY
from sqlalchemy.ext.declarative import declarative_base
import uuid
from literalai.helper import utc_now
from sqlalchemy.orm import relationship

from BE.Database.SqlLite.database import SessionLocal

Base = declarative_base()
db = SessionLocal()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    htw_mail = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    createdAt = Column(String, nullable=False)
    htw_password = Column(String, nullable=False)
    mail_list = Column(JSON, nullable=True, default=list)

    def add_mail_timestamp(self, timestamp: str):
        user = db.merge(self)
        if user.mail_list is None:
            user.mail_list = []
        user.mail_list.append(timestamp)
        db.commit()
        db.refresh(user)

    def __init__(self, htw_mail, username, password, createdAt, htw_password):
        self.id = str(uuid.uuid4())
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


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True)
    content = Column(String, nullable=False)
    role = Column(String, nullable=False)
    threadId = Column(String, ForeignKey("threads.id"), nullable=False)
    createdAt = Column(String)

    def __init__(self, content, role, thread_id):
        self.id = str(uuid.uuid4())
        self.created_at = utc_now()
        self.content = content
        self.role = role
        self.threadId = thread_id

    thread = relationship("Thread", backref="messages")
