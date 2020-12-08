import os

from flask import Flask, render_template, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User
from forms import UserAddForm

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

@app.errorhandler(Exception)
def server_error():
    """Display error page."""
    db.session().rollback()
    return render_template('error.html'), 500