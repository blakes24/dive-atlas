"""Model tests."""

# to run these tests use:
#
#    python -m unittest tests/test_models.py

from app import app

from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Dive_site


app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///dive_test"


# Create tables
db.create_all()


class ModelTestCase(TestCase):
    """Test models."""

    def setUp(self):
        """Create test client, add sample data."""
        User.query.delete()

        u = User.signup(
            email="testy@test.com",
            username="testyuser",
            password="password",
        )
        u.id = 1111
        db.session.add(u)
        db.session.commit()

        u = User.query.get(1111)
        self.u = u

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""
        u = User(email="test@test.com", username="testuser", password="HASHED_PASSWORD")

        db.session.add(u)
        db.session.commit()

        # repr should display id, username, and email
        self.assertEqual(f"{u}", f"<User #{u.id}: {u.username}, {u.email}>")

    def test_signup(self):
        """Does signup method create a new user?"""
        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="password",
        )

        db.session.add(u)
        db.session.commit()

        # u should display id, username, and email
        self.assertEqual(f"{u}", f"<User #{u.id}: {u.username}, {u.email}>")
        # should not be created missing args
        self.assertRaises(Exception, User.signup, email="test@test.com")
        self.assertRaises(Exception, User.signup, "test2@test.com", "", "")

    def test_signup_unique(self):
        """Does signup raise error if email/username is not unique?"""
        User.signup(
            email="test@test.com",
            username="testuser",
            password="password",
        )
        User.signup(
            email="test@test.com",
            username="testuser",
            password="password",
        )

        self.assertRaises(exc.IntegrityError, db.session.commit)

    def test_authenticate_valid(self):
        """Does authentication work?"""

        u = User.authenticate("testyuser", "password")

        # authenticate should return the user
        self.assertEqual(u, self.u)

    def test_invalid_username(self):
        """Does invalid username fail?"""

        u = User.authenticate("wrong", "password")

        # authenticate should return false
        self.assertNotEqual(u, self.u)
        self.assertFalse(u)

    def test_invalid_password(self):
        """Does invalid username fail?"""

        u = User.authenticate("testyuser", "nope")

        # authenticate should return false
        self.assertNotEqual(u, self.u)
        self.assertFalse(u)

    def test_dive_site_model(self):
        """Does Dive_site modal work?"""
        site = Dive_site(
            name="Test-site",
            id=22,
            lng=20,
            lat=10,
            description="Not real.",
            location="city, country",
        )

        db.session.add(site)
        db.session.commit()

        self.assertEqual(site.name, "Test-site")
        self.assertEqual(site.lng, 20)
        self.assertEqual(site.lat, 10)
        self.assertEqual(site.description, "Not real.")
        self.assertEqual(site.location, "city, country")
        self.assertEqual(len(Dive_site.query.all()), 1)

    def test_dive_site_missing(self):
        """Does it raise an error if its missing required arguments?"""
        site = Dive_site(name="Test-site", id=22, lat=10, description="Not real.")

        db.session.add(site)
        self.assertRaises(exc.IntegrityError, db.session.commit)
