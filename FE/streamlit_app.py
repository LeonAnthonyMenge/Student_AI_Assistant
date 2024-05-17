import json

import requests
import streamlit as st
import streamlit_authenticator as stauth
import asyncio
from streamlit_signup_test import sign_up, get_users


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
    with info:
        st.error('Incorrect Password or username')

if not authentication_status:
    sign_up()
else:
    async def get_threads():
        res = requests.get(f"http://localhost:4000/threads/{email}")
        return json.loads(res.content)

    async def create_thread(chat_name):
        pass

    threads = asyncio.run(get_threads())
    st.success("logged in")


    with st.sidebar:
        Authenticator.logout("Logout")
        for thread in threads:
            st.link_button(label=thread["name"], url=f'?thread_id={thread['id']}')
        chat_name = st.text_input(label="Chat name", placeholder="Enter a Chat name")
        st.button(label="create new Chat", on_click=create_thread(chat_name))