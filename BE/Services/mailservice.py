from imbox import Imbox
import datetime
import chromadb
import uuid
import bcrypt
import email
from BE.Database.SqlLite import models
from BE.Database.chromadb.chroma_database import add_data
from bs4 import BeautifulSoup
from BE.Database.SqlLite.database import SessionLocal, engine
import base64

models.Base.metadata.create_all(bind=engine)
mail_server = 'mail.htw-berlin.de'
db = SessionLocal()


def initialize():
    users = db.query(models.User).all()
    for user in users:
        try:
            add_mails_to_db(user)
            print(f'Added: {user.htw_mail}')
        except Exception as e:
            print(e)


def get_content(msg):
    text = ''
    if msg.is_multipart():
        for part in msg.get_payload():
            text = text + get_content(part)
    else:
        if msg.get_content_type() == "text/plain":
            text = msg.get_payload(decode=True)
        if msg.get_content_type() == "text/html":
            soup = BeautifulSoup(msg.get_payload(decode=True))
            text = soup.text
    return str(text)


def add_mails_to_db(user):
    try:
        pw = base64.b64decode(user.htw_password).decode()
        e_mail = user.htw_mail

        imbox = Imbox(mail_server, username=e_mail, password=pw, ssl=True, ssl_context=None, starttls=False)
        inbox_messages_received_after = imbox.messages(date__gt=datetime.date(2024, 5, 15))

        doc_list = []
        id_list = []
        metadata_list = []

        for i in range(len(inbox_messages_received_after)-1):
            if i % 100 == 0:
                print(i)
            try:
                message = email.message_from_string(inbox_messages_received_after[i][1].raw_email)
                metadata = {
                    'sender': message['From'],
                    'recipient': message['To'] if message['To'] else '',
                    'cc': message['Cc'] if message['Cc'] else '',
                    'bcc': message['Bcc'] if message['Bcc'] else '',
                    'subject': message['Subject'] if message['Subject'] else '',
                    'date': message['Date'] if message['Date'] else ''
                }
                if metadata['date'] not in user.mail_list and metadata['date'] != '':
                    user.add_mail_timestamp(metadata['date'])
                    metadata_list.append(metadata)
                    content = get_content(message)
                    doc_list.append(content)
                    id_list.append(str(uuid.uuid4()))
                else:
                    print(f'Already in: {message["Message-ID"]}')
            except Exception as e:
                print(f'Error processing message {i}: {e}')
        add_data(doc_list, metadata_list, id_list, user.id)

    except Exception as e:
        print(f'An error occurred in add_mails_to_db: {e}')

# results = collection.query(
#    query_texts=["Informationen zum Praktikum"],
#    n_results=10
# )
