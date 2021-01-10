"""SQLAlchemy models."""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect to the database and create all tables."""
    db.app = app
    db.init_app(app)
    db.create_all()

class User(db.Model):
    """User info."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)

    bucket_list = db.relationship("Dive_site", secondary="bucket_list_sites")
    dive_journal = db.relationship(
        "Journal_entry",
        back_populates="user",
        cascade="all, delete, delete-orphan",
        single_parent=True,
    )

    def __repr__(self):
        """Display id, username, and email."""
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user and hash password."""
        hashed_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")

        user = User(username=username, email=email, password=hashed_pwd)

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`. Returns user object if valid, false if not valid."""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Dive_site(db.Model):
    """Dive site."""

    __tablename__ = "dive_sites"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.Text, nullable=False)

    journal_entries = db.relationship("Journal_entry")


class Bucket_list_site(db.Model):
    """Dive site in user's bucket list."""

    __tablename__ = "bucket_list_sites"

    id = db.Column(db.Integer, primary_key=True)
    dive_site_id = db.Column(
        db.Integer, db.ForeignKey("dive_sites.id", ondelete="CASCADE"), nullable=False
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )


class Journal_entry(db.Model):
    """Dive journal entry."""

    __tablename__ = "journal_entries"

    id = db.Column(db.Integer, primary_key=True)
    dive_site_id = db.Column(
        db.Integer, db.ForeignKey("dive_sites.id", ondelete="CASCADE"), nullable=False
    )
    notes = db.Column(db.Text)
    description = db.Column(db.Text)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    user = db.relationship("User")
    dive_site = db.relationship("Dive_site")
