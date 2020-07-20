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
        users_ref.document(id).set(google_user.to_dict())
        return google_user

class Shoe(object):
    def __init__(self, shoe_name, quantity, purchase_price, size):
        self.shoe_name = shoe_name
        self.quantity = quantity
        self.purchase_price = purchase_price
        self.size = size


    def to_dict(self):
        return {
            'shoe_name': self.shoe_name,
            'quantity' : self.quantity,
            'purchase_price' : self.purchase_price,
            'size' : self.size,
        }

    def from_dict(shoe_dict):
        shoe = Shoe(shoe['shoe_name'], shoe_dict['quantity'], shoe_dict['purchase_price'], shoe_dict['size'])
        return shoe
