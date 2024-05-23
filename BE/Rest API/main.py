import base64
import uuid

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
import uvicorn
import base_models
from BE.Database.SqlLite.database import SessionLocal, engine
from BE.Database.SqlLite import models
from literalai.helper import utc_now
from BE.AI.llm import agent
from BE.Services.mailservice import initialize, add_mails_to_db

app = FastAPI()
now = utc_now()

models.Base.metadata.create_all(bind=engine)
initialize()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.delete("/threadsdelete")
def delete_all_threads():
    try:
        db = SessionLocal()
        threads = db.query(models.Thread).all()
        for thread in threads:
            db.query(models.Thread).filter(models.Thread.id == thread.id).delete()
            db.delete(thread)
        db.commit()
    finally:
        db.close()


@app.post("/users/authenticate")
async def get_user(login: base_models.User_login, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == login.username).first()
    if user is None:
        raise HTTPException(401, detail="Invalid username or password")
    decoded_password = base64.b85decode(login.password.encode('utf-8')).decode('utf-8')
    verified = (user.password == decoded_password)
    if not verified:
        raise HTTPException(401, detail="Invalid username or password")
    background_tasks.add_task(add_mails_to_db(user))
    return {"message": "User", "data": user}


@app.post("/user/registrate")
async def create_user(user: base_models.User, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.htw_mail == user.htw_mail).first()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    new_user = models.User(username=user.username, password=user.password, createdAt=now, htw_mail=user.htw_mail,
                           htw_password=user.htw_password)
    db.add(new_user)
    db.commit()

    #background_tasks.add_task(add_mails_to_db(user.htw_mail, user.htw_password))

    return status.HTTP_201_CREATED


@app.get('/user/{mail}')
async def get_user_by_identifier(mail: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.htw_mail == mail).first()
    if user is None:
        raise HTTPException(401, detail="Invalid Identifier")
    return user


@app.get('/user')
async def get_all_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@app.get("/threads/{user_id}")
async def get_thread(user_id: str, db: Session = Depends(get_db)):
    threads = db.query(models.Thread).filter(models.Thread.userId == user_id).all()
    return threads


@app.get("/messages/{thread_id}")
async def get_messages_thread_id(thread_id: str, db: Session = Depends(get_db)):
    messages = db.query(models.Message).filter(models.Message.threadId == thread_id).all()
    return messages


@app.post('/message')
async def add_step(message: base_models.Message, db: Session = Depends(get_db)):
    new_message = models.Message(
        content=message.content,
        role=message.role,
        thread_id=message.thread_id
    )
    db.add(new_message)
    db.commit()


@app.post('/thread')
async def get_or_create_thread(thread: base_models.Thread, db: Session = Depends(get_db)):
    thread_id = str(uuid.uuid4())
    new_thread = models.Thread(
        id=thread_id,
        name=thread.name,
        userId=thread.userId,
    )
    db.add(new_thread)
    db.commit()
    thread = db.query(models.Thread).filter(models.Thread.id == thread_id).first()
    return thread


@app.delete('/thread/delete/{thread_id}')
async def delete_thread(thread_id, db: Session = Depends(get_db)):
    print('in delete')
    thread = db.query(models.Thread).filter(models.Thread.id == thread_id).first()
    db.query(models.Step).filter(models.Step.threadId == thread_id).delete()

    if thread:
        db.delete(thread)
        db.commit()


@app.post('/chat')
async def post_message(message: base_models.Message):
    answer = agent.query(message.content)
    return answer


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=4000)
