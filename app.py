import os
import requests

from flask import Flask, render_template, flash, redirect, session, g, request
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User
from forms import UserAddForm, LoginForm

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "shhhItsASecret123")
toolbar = DebugToolbarExtension(app)

connect_db(app)


@app.before_request
def add_user_to_g():
    """If logged in, add user to Flask g."""
    if session.get("user_id") is not None:
        g.user = User.query.get(session["user_id"])

    else:
        g.user = None


@app.route("/")
def home():
    """Render home page."""
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Render AddUserForm form and creates a new user."""
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
            )
            db.session.commit()
            session["user_id"] = user.id
            flash(f"Welcome {user.username}!", "success")

            return redirect("/")

        except IntegrityError:
            db.session().rollback()
            flash("Username/email already exists", "danger")
            return render_template("signup.html", form=form)

    return render_template("signup.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            session["user_id"] = user.id
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", "danger")

    return render_template("/login.html", form=form)


@app.route("/logout")
def logout():
    """Handle logout of user."""

    session.pop("user_id", None)

    flash("You have been logged out.", "success")
    return redirect("/")


@app.route("/sites/search", methods=["POST"])
def get_sites():
    """Send request to api to get list of dive sites based on provided search parameters"""
    params = request.json

    res = requests.get("http://api.divesites.com", params=params)

    data = res.json()

    return data


@app.errorhandler(Exception)
def server_error():
    """Display error page."""
    db.session().rollback()
    return render_template("error.html"), 500
