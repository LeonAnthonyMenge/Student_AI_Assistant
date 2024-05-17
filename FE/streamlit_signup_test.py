import json

import requests
import streamlit as st
import re
import streamlit_authenticator as stauth
from fastapi import status
import asyncio


def validate_email(email):
    """
    Check Email Validity
    :param email:
    :return True if email is valid else False:
    """
    pattern = "^[a-zA-Z0-9-_]+@htw-berlin.de"

    if re.match(pattern, email):
        return True
    return False


def validate_username(username):
    """
    Checks Validity of userName
    :param username:
    :return True if username is valid else False:
    """

    pattern = "^[a-zA-Z0-9]*$"
    if re.match(pattern, username):
        return True
    return False

async def get_users():
    res = requests.get('http://localhost:4000/user')
    users = json.loads(res.content)
    return users
async def add_user(email: str, username: str, password: str, htw_password: str):
    body = {
        "username": username,
        "htw_mail": email,
        "password": password,
        "htw_password": htw_password
    }
    res = requests.post("http://localhost:4000/user/registrate", json=body)
    print(res.status_code)
    return res.status_code


def sign_up():
    with (st.form(key='signup', clear_on_submit=True)):
        st.subheader(':green[Sign Up]')
        email = st.text_input(':blue[HTW-Email]', placeholder='Enter Your Email')
        username = st.text_input(':blue[Username]', placeholder='Enter Your Username')
        htw_password = st.text_input(':blue[HTW-Password]', placeholder='Enter Your HTW-Password', type='password')
        password1 = st.text_input(':blue[Password]', placeholder='Enter Your Password', type='password')
        password2 = st.text_input(':blue[Confirm Password]', placeholder='Confirm Your Password', type='password')

        valid_email = False
        valid_username = False
        valid_password = False

        if email:
            if not validate_email(email):
                st.warning("E-Mail address is not valid")
            else:
                valid_email = True
        if username:
            if not validate_username(username):
                st.warning("Username not valid")
            else:
                valid_username = True

        if password1 and password2:
            if not password1 == password2:
                st.warning("Passwords are not equal")
            if len(password1) > 8:
                valid_password = True
            else:
                st.warning("Password is to short")

        if valid_email and valid_username and valid_password:
            hashed_password = stauth.Hasher([password2]).generate()
            hashed_htw_password = stauth.Hasher([htw_password]).generate()
            status_code = asyncio.run(add_user(email, username, hashed_password[0], hashed_htw_password[0]))
            if status_code == 200:
                st.success('Account created successfully!!')
            elif status_code == 409:
                st.warning("User does already exist")
            else:
                st.warning("An Error occurred")

        btn1, bt2, btn3, btn4, btn5 = st.columns(5)

        with btn3:
            st.form_submit_button('Sign Up')
