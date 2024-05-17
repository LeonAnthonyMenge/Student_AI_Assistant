import json
from typing import Optional, Dict, List
from colorama import Fore, Style
import requests
from chainlit.step import StepDict
from literalai.helper import utc_now
import chainlit.data as cl_data
import chainlit as cl

now = utc_now()

create_step_counter = 0

thread_history = []  # type: List[cl_data.ThreadDict]
deleted_thread_ids = []  # type: List[str]
class CustomDataLayer(cl_data.BaseDataLayer):
    async def get_user(self, identifier: str):
        print(f'INFO: Method get_user() was called with identifier: {identifier}')
        res = requests.get(f'http://localhost:4000/user/{identifier}')
        data = res.json()['data']
        print(type(data), '   :   ', data)
        user = cl.PersistedUser(id=data['id'], createdAt=data['createdAt'], identifier=identifier)
        print(f'INFO: Method get_user() will return user: {user}')
        return user

    async def create_user(self, user: cl.User):
        print('INFO: Method create_user() was called')
        user = cl.PersistedUser(id=user.metadata['id'], createdAt=now, identifier=user.identifier)
        print(f'INFO: Method create_user() will return user: {user}')
        return user

    async def update_thread(
        self,
        thread_id: str,
        name: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
    ):
        print('INFO: update_thread() was called')
        user = cl.user_session.get('user')
        thread = next((t for t in thread_history if t["id"] == thread_id), None)
        if thread:
            print('Thread did already exist')
            if name:
                print(name)
                thread["name"] = name
        else:
            print('else')
            new_thread = {
                    "id": thread_id,
                    "name": name,
                    "createdAt": utc_now(),
                    "userId": user.id,
                    "userIdentifier": user.identifier,
                    'steps': []
                }
            res = requests.post('http://localhost:4000/thread', json=new_thread)
            print(new_thread)
            thread_history.append(new_thread)
            print('appended')


    @cl_data.queue_until_user_message()
    async def create_step(self, step_dict: StepDict):
        print(f'{Fore.BLUE}INFO: create_step() was called for {step_dict}{Style.RESET_ALL}')

        global create_step_counter
        create_step_counter += 1

        thread = next(
            (t for t in thread_history if t["id"] == step_dict.get("threadId")), None
        )
        json_string = json.dumps(step_dict)
        if thread:
            thread["steps"].append(step_dict)
            x = requests.post('http://localhost:4000/step', json_string)
            print(f'{Fore.BLUE}INFO: create_step() performed post request and got: {x.status_code}{Style.RESET_ALL}')

    async def update_step(self, step_dict: StepDict):
        print(f'{Fore.RED}INFO: update_step() was called for {step_dict}{Style.RESET_ALL}')
    async def get_all_threads(self):
        print('INFO: get_all_threads() was called')
        user = cl.user_session.get('user')
        print(user)
        res = requests.get(f'http://localhost:4000/thread/{user.id}')
        print('response:  ' + res.text)
        global thread_history
        thread_history = res.json()

    async def list_threads(
        self, pagination: cl_data.Pagination, filter: cl_data.ThreadFilter
    ) -> cl_data.PaginatedResponse[cl_data.ThreadDict]:
        print('INFO: list_threads() was called')
        return cl_data.PaginatedResponse(
            data=[t for t in thread_history if t["id"] not in deleted_thread_ids],
            pageInfo=cl_data.PageInfo(
                hasNextPage=False, startCursor=None, endCursor=None
            ),
        )

    async def get_thread(self, thread_id: str):
        print('INFO: get_thread() was called')
        thread = next((t for t in thread_history if t["id"] == thread_id), None)
        print(f'INFO: get_thread() will return: {thread}')
        return thread

    async def delete_thread(self, thread_id: str):
        print(f'INFO: delete_thread() was called for: {thread_id}')
        res = requests.delete(f'http://localhost:4000/thread/delete/{thread_id}')
        deleted_thread_ids.append(thread_id)

    async def get_thread_author(self, thread_id: str):
        return "admin"