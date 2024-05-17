import json
import random
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


async def get_threads():
    res = requests.get(f"{base_url}/threads/{email}")
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

def get_ai_answer(prompt):
    body = {
        "content": prompt,
        "role": "",
        "thread_id": ""
    }
    res = requests.post(f'{base_url}/chat', json=body)
    answer = json.loads(res.content)['text'].split()

    for word in answer:
        yield word + " "
        time.sleep(0.05)


def create_thread(chat_name):
    body = {
        "name": chat_name,
        "userId": email
    }
    res = requests.post(f'{base_url}/thread', json=body)
    print(res.text)
    return asyncio.run(get_threads())


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
    if len(st.session_state.messages) == 0:
        st.success("Chat with me!")

    # Sidebar
    with st.sidebar:
        Authenticator.logout(":red[Logout]")
        st.subheader("Chats")
        for thread in threads:
            if st.button(label=thread["name"], use_container_width=True):
                get_messages(thread["id"])
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
        status = asyncio.run(add_message({"role": "user", "content": prompt}))
        if status != 200:
            st.warning("Could not save message")
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner("Thinking..."):
                full_response = st.write_stream(get_ai_answer(prompt))
        status = asyncio.run(add_message({"role": "assistant", "content": full_response}))
        if status != 200:
            st.warning("Could not save message")
