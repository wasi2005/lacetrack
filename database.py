import firebase_admin
import os
from firebase_admin import credentials
from firebase_admin import firestore

# from ast import literal_eval

def get_users():
    firebase_credentials = eval(os.environ['FIREBASE_CREDENTIALS'])
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    return db.collection('users')
