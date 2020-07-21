from flask_login import UserMixin
from database import get_users

class User(UserMixin):
    def __init__(self, id, name, email, profile_pic, inventory):
        self.id = id
        self.name = name
        self.email = email
        self.profile_pic = profile_pic
        self.inventory = inventory

    def to_dict(self):
        return {
            'id': self.id,
            'name' : self.name,
            'email' : self.email,
            'profile_pic' : self.profile_pic,
            'inventory' : self.inventory
        }

    def parse_inventory(inventory):
        return [Shoe.from_dict(shoe_dict) for shoe_dict in inventory]

    def get(user_id):
        user_dict = get_users().document(user_id).get().to_dict()
        if user_dict == None:
            return None
        user = User(user_id, user_dict["name"], user_dict["email"], user_dict['profile_pic'], User.parse_inventory(user_dict['inventory']))
        return user

    @staticmethod
    def create(google_user):
        users_ref = get_users()
        users_ref.document(google_user.id).set(google_user.to_dict())
        return google_user

class Shoe(object):
    def __init__(self, name, size, quantity, price_bought, price_sold, date_bought, date_sold, status):
        self.name = name
        self.size = size
        self.quantity = quantity
        self.price_bought = price_bought
        self.price_sold = price_sold
        self.date_bought = date_bought
        self.date_sold = date_sold
        self.status = status

    def to_dict(self):
        return {
            'name': self.name,
            'size' : self.size,
            'quantity' : self.quantity,
            'price_bought' : self.price_bought,
            'price_sold' : self.price_sold,
            'date_bought' : self.date_bought,
            'date_sold' : self.date_sold,
            'status' : self.status,
        }

    def from_dict(shoe_dict):
        return Shoe(shoe['name'], shoe_dict['size'], shoe_dict['quantity'], shoe_dict['price_bought'], shoe_dict['price_sold'], shoe_dict['date_bought'], shoe_dict['date_sold'], shoe_dict['status'])
