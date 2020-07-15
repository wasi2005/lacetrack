import firebase_admin
import os
from firebase_admin import credentials
from firebase_admin import firestore

import ast

firebase_credentials = ast.literal_eval(os.environ['FIREBASE_CREDENTIALS'])
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)
db = firestore.client()

def get_users():
    return db.collection('users')
