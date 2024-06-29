import base64
from datetime import datetime
import json

import requests
from rpds import List

from BE.Database.SqlLite import models
from BE.Database.SqlLite.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

def get_moodle_token(user: models.User) -> str:
    print(user.username)
    print(user.htw_password)
    htw_password = base64.b64decode('Mk1hbDEwSG9jaDE1Lg=='.encode('utf-8'))
    res = requests.get(
        f'https://moodle.htw-berlin.de/login/token.php?username={user.username}&password={htw_password.decode()}&service=moodle_mobile_app')
    return str(res.json()['token'])

def moodle_exercises(user_id: str):
    db = SessionLocal()
    user = db.query(models.User).filter(models.User.id == user_id).first()
    print(user)
    token = get_moodle_token(user)
    course_ids_names = get_course_ids(token)
    open_tasks = []
    for course_id, course_name in course_ids_names:
        moodle_call = f'https://moodle.htw-berlin.de/webservice/rest/server.php?wstoken={token}&wsfunction=core_course_get_contents&moodlewsrestformat=json&courseid={course_id}'
        res = requests.get(moodle_call)

        try:
            courses = res.json()
        except ValueError as e:
            print(f"Error parsing JSON: {e}")
            continue


        for course in courses:
            if isinstance(course, dict) and 'modules' in course:
                for course_entry in course['modules']:
                    if 'customdata' in course_entry and 'duedate' in course_entry['customdata']:
                        duedate = json.loads(course_entry['customdata'])['duedate']
                        if duedate:  # Check if duedate is not None or 0
                            timestamp = datetime.fromtimestamp(int(duedate), tz=None)
                            if datetime.now() < timestamp:
                                exercise_name = course_entry['name']
                                open_tasks.append(
                                    f'Coursename: {course_name}, time_left: {timestamp - datetime.now()}, exercise_name: {exercise_name}')
    return open_tasks


def get_user_id(token: str) -> str:
    res = requests.get(
        f"https://moodle.htw-berlin.de/webservice/rest/server.php?moodlewsrestformat=json&wsfunction=core_webservice_get_site_info&wstoken={token}")
    res_json = json.loads(res.content)
    return res_json['userid']


# get course ids -> List
def get_course_ids(token: str) -> List:
    user_id = get_user_id(token)
    res = requests.get(
        f"https://moodle.htw-berlin.de/webservice/rest/server.php?moodlewsrestformat=json&wsfunction=core_enrol_get_users_courses&wstoken={token}&userid={user_id}")

    courses = res.json()
    course_ids = []
    for course in courses:
        course_ids.append((course['id'], course['fullname']))
    return course_ids

