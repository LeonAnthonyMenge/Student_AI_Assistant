import asyncio

import requests

from BE.Database.SqlLite import models


def get_moodle_token(user: models.User):
    res = requests.get(f'https://moodle.htw-berlin.de/login/token.php?username={user.username}&password={user.htw_password}&service=Moodle_student')
    print(str(res.json()['token']))
    return None

async def get_messages(moodle_domain: str, moodle_token: str):
    """
     Retrieve a list of messages sent and received by a user (conversations, notifications or both)
    """
    moodle_url = moodle_domain + "/webservice/rest/server.php"
    params = {
        "useridto": 0,
        "useridfrom": 0,
        "type": "both",
        "read": 1,
        "newestfirst": 1,
        "limitfrom": 0,
        "limitnum": 20,
        "wstoken": moodle_token,
        "wsfunction": "core_message_get_messages",
        "moodlewsrestformat": "json"
    }

    r = requests.post(moodle_url, data=params)
    content = r.json()
    print(str(content))
    return content

