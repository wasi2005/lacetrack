from flask_login import UserMixin
from database import get_users

class User(UserMixin):
    def __init__(self, id_, name, email, profile_pic):
        self.id = id_
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

class Shoe(object):
    def __init__(self, shoe_name, quantity, purchase_price, size, breakeven_price):
        self.shoe_name = shoe_name
        self.quantity = quantity
        self.purchase_price = purchase_price
        self.size = size
        self.breakeven_price = breakeven_price

    def to_dict(self):
        return {
            'shoe_name': self.shoe_name,
            'quantity' : self.quantity,
            'purchase_price' : self.purchase_price,
            'size' : self.size,
            'breakeven_price' : self.breakeven_price
        }

    def from_dict(shoe_dict):
        shoe = Shoe(self.shoe_name, self.quantity, self.purchase_price, self.size, self.breakeven_price)
        return shoe
