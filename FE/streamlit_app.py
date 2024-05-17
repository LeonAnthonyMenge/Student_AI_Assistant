import json
import requests
import streamlit as st
import streamlit_authenticator as stauth
import asyncio
from streamlit_signup_test import sign_up, get_users


async def get_threads():
    res = requests.get(f"http://localhost:4000/threads/{email}")
    return json.loads(res.content)


def create_thread(chat_name):
    body = {
        "name": chat_name,
        "userId": email
    }
    res = requests.post('http://localhost:4000/thread', json=body)
    print(res.text)
    # Aktualisieren der Threads nach dem Erstellen eines neuen Threads
    return asyncio.run(get_threads())

# Laden der Benutzer
users = asyncio.run(get_users())
emails = []
usernames = []
passwords = []

for user in users:
    emails.append(user['htw_mail'])
    usernames.append(user['username'])
    passwords.append(user['password'])

# Erstellen der Authentifizierungs-Credentials
credentials = {'usernames': {}}
for index in range(len(emails)):
    credentials['usernames'][usernames[index]] = {'name': emails[index], 'password': passwords[index]}

# Initialisieren des Authentifikators
Authenticator = stauth.Authenticate(credentials, cookie_name='Streamlit', key="abcd", cookie_expiry_days=5)

# Login-Authentifizierung
email, authentication_status, username = Authenticator.login(':green[Login]', 'main')

info, info1 = st.columns(2)

if not authentication_status:
    sign_up()
elif authentication_status:
    # Threads abrufen und anzeigen
    threads = asyncio.run(get_threads())
    st.success("logged in")

    with st.sidebar:
        Authenticator.logout("Logout")
        for thread in threads:
            st.button(label=thread["name"], key=f"thread-{thread['id']}")

        chat_name = st.text_input(label="Chat name", placeholder="Enter a Chat name")

        # Überprüfen, ob der Button geklickt wurde, und dann den Thread erstellen
        if st.button(label="create new Chat"):
            if chat_name:
                threads = create_thread(chat_name)
                st.rerun()  # Um die Seite zu aktualisieren und die neuen Threads anzuzeigen
            else:
                st.error("Please enter a chat name.")
