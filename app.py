 #  _                         _                           _
 # | |   __ _    ___    ___  | |_   _ __    __ _    ___  | | __
 # | |  / _` |  / __|  / _ \ | __| | '__|  / _` |  / __| | |/ /
 # | | | (_| | | (__  |  __/ | |_  | |    | (_| | | (__  |   <
 # |_|  \__,_|  \___|  \___|  \__| |_|     \__,_|  \___| |_|\_\
 #
 # wasi ahmed


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
from database import init_db_command
from models import User

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
app.secret_key = os.urandom(24)

login_manager = LoginManager()
login_manager.init_app(app)

client = WebApplicationClient(GOOGLE_CLIENT_ID)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

 #                         _
 #  _ __    ___    _   _  | |_    ___   ___
 # | '__|  / _ \  | | | | | __|  / _ \ / __|
 # | |    | (_) | | |_| | | |_  |  __/ \__ \
 # |_|     \___/   \__,_|  \__|  \___| |___/


# When someone goes to lace-track.herokuapp.com/ --> index() gets executed
@app.route('/')
def index():
    return render_template("index.html")

@app.route("/portal")
def portal():
    if current_user.is_authenticated:
        return (
            "<p>Hello, {}! You're logged in! Email: {}</p>"
            "<div><p>Google Profile Picture:</p>"
            '<img src="{}" alt="Google profile pic"></img></div>'
            '<a class="button" href="/logout">Logout</a>'.format(
                current_user.name, current_user.email, current_user.profile_pic
            )
        )
    else:
        return '<a class="button" href="/login">Google Login</a>'

@app.route("/login")
def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in your db with the information provided
    # by Google
    user = User(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    )

    # Doesn't exist? Add it to the database.
    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email, picture)

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("index"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run()
