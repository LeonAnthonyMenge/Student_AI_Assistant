import base64
import uuid
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
import uvicorn
import base_models
from BE.Database.SqlLite.database import SessionLocal, engine
from BE.Database.SqlLite import models
from literalai.helper import utc_now
from BE.AI.llm import get_agent, llama3
from BE.Services.mailservice import initialize, add_mails_to_db
from BE.Services.lsf_service import get_module_names, find_optimal_schedule

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

    # background_tasks.add_task(add_mails_to_db(user.htw_mail, user.htw_password))

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
async def create_thread(thread: base_models.Thread, db: Session = Depends(get_db)):
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


@app.post('/thread/auto_create')
async def auto_create_thread(thread: base_models.Thread, db: Session = Depends(get_db)):
    heading = str(llama3.complete(f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>You are an chat backend assistant. 
                        Your Task is it to create a short Headline for user prompts which can be used as a headline for the chat. 
                        The headline can have maximum 2 words. Important: Do not answer the question. Only create the Headline!
                        <|eot_id|><|start_header_id|>user<|end_header_id|>
                        {thread.name}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""))
    print(heading)
    thread_id = str(uuid.uuid4())
    new_thread = models.Thread(
        id=thread_id,
        name=heading,
        userId=thread.userId,
    )
    db.add(new_thread)
    db.commit()
    thread = db.query(models.Thread).filter(models.Thread.id == thread_id).first()
    return thread


@app.delete('/thread/delete/{thread_id}')
async def delete_thread(thread_id: str, db: Session = Depends(get_db)):
    thread = db.query(models.Thread).filter(models.Thread.id == thread_id).first()

    if thread:
        messages = db.query(models.Message).filter(models.Message.threadId == thread_id).all()
        if messages:
            for message in messages:
                db.delete(message)
        db.delete(thread)
        db.commit()


@app.post('/chat')
async def post_message(message: base_models.AI_Message, db: Session = Depends(get_db)):
    print(message.content)
    messages = db.query(models.Message).filter(models.Message.threadId == message.thread_id).all()
    chat_history = []
    for mes in messages:
        chat_history.append(str(f"{{role: {mes.role}, content: {mes.content}}}"))

    if len(chat_history) >= 3:
        chat_history = chat_history[-3:]
    if message.topic == 'Moodle':
        message_split = message.content.split("'2,5'")
        for entry in message_split:
            chat_history.append(str(f"{{role: user, content: {entry}}}"))

    chat_history_str = " ".join(chat_history)
    agent = get_agent(message.topic)
    try:
        answer = agent.query(chat_history_str)
    except Exception as e:
        print(e)
        answer = llama3.complete(chat_history_str)
        print("llama")
    return answer

@app.get("/module/names")
def get_module_name():
    return get_module_names()

@app.post("/get_course_plan")
def get_course_plan(courses: base_models.CourseList):
    optimal_plan = find_optimal_schedule(courses.courses)
    prompt = f"""
    You are a scheduling assistant, and you've determined the most efficient way to select the necessary classes based on the provided data.
    Please format the following course information into an easily readable table and inform the user that these courses offer the best efficiency.
    Multiple classes can be in one day and most importantly don't forget any classes!
    Total time spend in university: {optimal_plan[0]}
    courses: {optimal_plan[1]}
    """
    return llama3.complete(prompt)


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=4000)
