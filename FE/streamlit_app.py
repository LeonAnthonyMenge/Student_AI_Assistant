import json
import time

import requests
import streamlit as st
import streamlit_authenticator as stauth
import asyncio
from streamlit_signup_test import sign_up, get_users

base_url = 'http://localhost:4000'
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'selected_thread_id' not in st.session_state:
    st.session_state.selected_thread_id = None

if 'selected_topic' not in st.session_state:
    st.session_state.selected_topic = "general help"


async def get_threads():
    res = requests.get(f"{base_url}/threads/{email}")
    return json.loads(res.content)


async def delete_thread(thread_id):
    res = requests.delete(f"{base_url}/thread/delete/{thread_id}")
    return res.status_code


async def get_user():
    res = requests.get(f"{base_url}/user/{email}")
    return json.loads(res.content)


def get_messages(thread_id):
    st.session_state.selected_thread_id = thread_id
    res = requests.get(f'{base_url}/messages/{thread_id}')

    st.session_state.messages = json.loads(res.content)


async def add_message(message: dict):
    st.session_state.messages.append(message)
    thread_id = st.session_state.selected_thread_id
    body = {
        "content": message['content'],
        "role": message['role'],
        "thread_id": thread_id
    }
    res = requests.post(f'{base_url}/message', json=body)
    return res.status_code


def get_ai_answer(user_input):
    body = {
        "content": user_input,
        "role": "User",
        "thread_id": st.session_state.selected_thread_id
    }
    res = requests.post(f'{base_url}/chat', json=body)
    res.raise_for_status()
    answer = str(json.loads(res.content)['response'])

    return answer

    #for word in answer:
     #   yield word + " "
      #  time.sleep(0.05)


def create_thread(chat_name):
    body = {
        "name": chat_name,
        "userId": email
    }
    res = requests.post(f'{base_url}/thread', json=body)
    return asyncio.run(get_threads())


async def auto_create_thread(user_input):
    body = {
        "name": user_input,
        "userId": email
    }
    res = requests.post(f'{base_url}/thread/auto_create', json=body)
    return json.loads(res.content)


users = asyncio.run(get_users())
emails = []
usernames = []
passwords = []

for user in users:
    emails.append(user['htw_mail'])
    usernames.append(user['username'])
    passwords.append(user['password'])

credentials = {'usernames': {}}
for index in range(len(emails)):
    credentials['usernames'][usernames[index]] = {'name': emails[index], 'password': passwords[index]}

Authenticator = stauth.Authenticate(credentials, cookie_name='Streamlit', key="abcd", cookie_expiry_days=5)

email, authentication_status, username = Authenticator.login(':green[Login]', 'main')

info, info1 = st.columns(2)

if not authentication_status:
    sign_up()
elif authentication_status:
    threads = asyncio.run(get_threads())
    identical_user = asyncio.run(get_users())
    if len(st.session_state.messages) == 0:
        st.success("Chat with me!")

    # Sidebar
    with st.sidebar:
        Authenticator.logout(":red[Logout]")
        st.subheader("Chats")

        # Help Agent to use the right tools
        st.session_state.selected_topic = st.selectbox(
            "select a topic:",
            ("general help", "coding", "sql", "psychology"),
            index=0
        )

        for thread in threads:
            with st.container(border=False):
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(thread["name"], use_container_width=True, key=f'thread_{thread["id"]}'):
                        get_messages(thread["id"])
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f'delete_{thread["id"]}', type="primary"):
                        st.write(f'Delete Thread: {thread["id"]}')
                        threads = asyncio.run(delete_thread(thread["id"]))
                        st.rerun()

        chat_name = st.text_input(label="Create a new Chat", placeholder="Enter a Chat name")

        if st.button(label="create new Chat"):
            if chat_name:
                threads = create_thread(chat_name)
                st.rerun()
            else:
                st.error("Please enter a chat name.")

    # Chat Logic: https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        if not st.session_state.selected_thread_id:
            new_thread = asyncio.run(auto_create_thread(prompt))
            st.session_state.selected_thread_id = new_thread['id']
            threads = asyncio.run(get_threads())

        status = asyncio.run(add_message({"role": "user", "content": prompt}))
        if status != 200:
            st.warning("Could not save message")
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner("Thinking..."):
                identical_user = identical_user[0]
                question = (
                    f'I am a student (this is my id: {identical_user["id"]}) and need help about this topic: {st.session_state.selected_topic}'
                    f'Here is my prompt: {prompt}')
                answer = get_ai_answer(question)
                full_response = st.write(answer)
        status = asyncio.run(add_message({"role": "assistant", "content": answer}))
        if status != 200:
            st.warning("Could not save message")
