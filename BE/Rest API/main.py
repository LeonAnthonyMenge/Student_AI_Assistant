import base64

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uvicorn
import base_models
from BE.Database.SqlLite.database import SessionLocal, engine
from BE.Database.SqlLite import models
from literalai.helper import utc_now
from BE.Database.SqlLite.models import Step
from BE.AI.llm import llm

app = FastAPI()
now = utc_now()

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.post("/users/authenticate")
async def get_user(login: base_models.User_login, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == login.username).first()
    if user is None:
        raise HTTPException(401, detail="Invalid username or password")
    decoded_password = base64.b85decode(login.password.encode('utf-8')).decode('utf-8')
    print(decoded_password)
    verified = (user.password == decoded_password)
    if not verified:
        raise HTTPException(401, detail="Invalid username or password")
    return {"message": "User", "data": user}


@app.post("/user/registrate")
async def create_user(user: base_models.User, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.htw_mail == user.htw_mail).first()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    new_user = models.User(username=user.username, password=user.password, createdAt=now, htw_mail=user.htw_mail, htw_password=user.htw_password)
    db.add(new_user)
    db.commit()

    return status.HTTP_201_CREATED


@app.get('/user/{identifier}')
async def get_user_by_identifier(identifier: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.htw_mail == identifier).first()
    if user is None:
        raise HTTPException(401, detail="Invalid Identifier")
    print(user)
    response = {'message': 'User', 'data': user}
    return response

@app.get('/user')
async def get_all_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@app.get("/threads/{user_id}")
async def get_thread(user_id: str, db: Session = Depends(get_db)):
    threads = db.query(models.Thread).filter(models.Thread.userId == user_id).all()
    return threads

#TODO: umschreiben
@app.get("/steps/{thread_id}")
async def get_thread_thread_id(thread_id: str, db: Session = Depends(get_db)):
    threads = db.query(models.Thread).filter(models.Thread.id == thread_id).all()
    serialized_threads = []
    for thread in threads:
        steps = db.query(models.Step).filter(models.Step.threadId == thread.id).all()
        serialized_steps = []
        for step in steps:
            serialized_steps.append(base_models.Step(
                id=step.id,
                name=step.name,
                type=step.type,
                threadId=step.threadId,
                disableFeedback=step.disableFeedback,
                streaming=step.streaming,
                waitForAnswer=step.waitForAnswer,
                isError=step.isError,
                output=step.output,
                createdAt=step.createdAt,
                start=step.start,
                end=step.end,
                generation=step.generation,
                language=step.language,
                indent=step.indent
            ))
        serialized_threads.append(base_models.Thread_incl_Steps(
            id=thread.id,
            name=thread.name,
            createdAt=str(thread.createdAt),
            userId=thread.userId,
            userIdentifier=thread.userIdentifier,
            steps=serialized_steps
        ))

    return serialized_threads

# TODO: umschreiben
@app.post('/step')
async def add_step(step: base_models.Step, db: Session = Depends(get_db)):
    print(f'Step: {step}')
    new_step: Step = models.Step(
        id=step.id,
        name=step.name,
        type=step.type,
        threadId=step.threadId,
        disableFeedback=step.disableFeedback,
        streaming=step.streaming,
        waitForAnswer=step.waitForAnswer,
        isError=step.isError,
        output=step.output,
        createdAt=step.createdAt,
        start=step.start,
        end=step.end,
        generation=step.generation,
        language=step.language,
        indent=step.indent
    )
    db.add(new_step)
    db.commit()


@app.post('/thread')
async def get_or_create_thread(thread: base_models.Thread_incl_Steps, db: Session = Depends(get_db)):
    new_thread = models.Thread(
        name=thread.name,
        userId=thread.userId,
    )
    db.add(new_thread)
    db.commit()
    # TODO: Bessere Lösung finden
    thread = db.query(models.Thread).filter(models.Thread.userId == new_thread.userId and models.Thread.name == new_thread.name)
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
    answer = llm.complete(message.content)
    return answer

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=4000)
