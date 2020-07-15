from flask_login import UserMixin
from database import get_users

class User(UserMixin):
    def __init__(self, id, name, email, profile_pic):
        self.id = id
        self.name = name
        self.email = email
        self.profile_pic = profile_pic

    def to_dict(self):
        return {
            'id': self.id,
            'name' : self.name,
            'email' : self.email,
            'profile_pic' : self.profile_pic
        }

    @staticmethod
    def get(id):
        user_dict = get_users().document(id).to_dict()
        user = User(id, user_dict["name"], user_dict["email"], user_dict['profile_pic'])
        return user

    @staticmethod
    def create(id, name, email, profile_pic):
        users_ref = get_users()
        users_ref.document().set(User(id, name, email, profile_pic).to_dict())
