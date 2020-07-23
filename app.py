
 #  _                                      _
 # (_)  _ __ ___    _ __     ___    _ __  | |_   ___
 # | | | '_ ` _ \  | '_ \   / _ \  | '__| | __| / __|
 # | | | | | | | | | |_) | | (_) | | |    | |_  \__ \
 # |_| |_| |_| |_| | .__/   \___/  |_|     \__| |___/
 #                 |_|

import json
import os

from flask import Flask, render_template, redirect, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests

# Internal Imports
from database import get_users
from models import User, Shoe


 #                          __   _
 #   ___    ___    _ __    / _| (_)   __ _
 #  / __|  / _ \  | '_ \  | |_  | |  / _` |
 # | (__  | (_) | | | | | |  _| | | | (_| |
 #  \___|  \___/  |_| |_| |_|   |_|  \__, |
 #                                   |___/

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = ("https://accounts.google.com/.well-known/openid-configuration")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", None)

login_manager = LoginManager()
login_manager.init_app(app)

client = WebApplicationClient(GOOGLE_CLIENT_ID)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

 #                         _
 #  _ __    ___    _   _  | |_    ___   ___
 # | '__|  / _ \  | | | | | __|  / _ \ / __|
 # | |    | (_) | | |_| | | |_  |  __/ \__ \
 # |_|     \___/   \__,_|  \__|  \___| |___/

@app.route('/')
def index():
    return render_template("index.html", user = current_user)

@app.route("/portal")
def portal():
    if current_user.is_authenticated:
        return render_template("portal.html", user = current_user)
    else:
        return redirect('/')

@app.route("/login")
def login():

    # Request Simulation
    # -----------------------------------
    #  +-- lace-track.herokuapp.com/login
    #  +-- auth.google.com/authorization_endpoint?scope=openid&scope=email&scope=profile&redirect_uri=lace-track.herokuapp.com/login/callback
    #  +-- lace-track.herokuapp.com/login/callback?code=3838388
    #  +-- auth.google.com/token_endpoint?redirect_url=lace-track.herokuapp.com/login/callback&code=3838388&authorization_response=lace-track.herokuapp.com/login/callback?code=3838388
    #  +-- lace-track.herokuapp.com/login/callback?token_openid=kdnhkjfghZdfkjgxkd&token_email=kdnhkjfghZdfkjgxkd&token_profile=fijfjfjiijf
    #  +-- auth.google.com/userinfo_endpoint?token_openid=kdnhkjfghZdfkjgxkd&token_email=kdnhkjfghZdfkjgxkd&token_profile=fijfjfjiijf
    #  +-- lace-track.herokuapp.com/login/callback?sub=657&email=wasi.shams.ahmed@gmail.com&picture=wasi.jpeg&users_name=wahmed937

    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/login/callback")
def callback():

    code = request.args.get("code")

    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response = request.url,
        redirect_url = request.base_url,
        code = code
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    google_user = User(
        id = unique_id,
        name = users_name,
        email = users_email,
        profile_pic = picture,
        inventory = []
    )

    lacetrack_user = User.get(google_user.id)

    if lacetrack_user == None:
        lacetrack_user = User.create(google_user)

    login_user(lacetrack_user)

    return redirect(url_for("portal"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/add-shoe", methods=["POST"])
@login_required
def add_shoe():
    name = request.form['name']
    size = request.form['size']
    quantity = request.form['quantity']
    price_bought = request.form['price_bought']
    date_bought = request.form["date_bought"]

    shoe = Shoe(name, size, quantity, price_bought, 0, date_bought, "--/--/--", "0")
    current_user.add_shoe(shoe)

    return redirect(url_for("portal"))

if __name__ == "__main__":
    app.run()
