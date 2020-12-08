"""View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest tests/test_views.py

from app import app

from unittest import TestCase

from models import db, User

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///dive_test"


db.create_all()

# Don't have WTForms use CSRF

app.config['WTF_CSRF_ENABLED'] = False


class ViewTestCase(TestCase):
    """Test views."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="password",
        )
        u.id = 1111
        db.session.add(u)
        db.session.commit()

        u = User.query.get(1111)
        self.u = u

    def tearDown(self):
        db.session.rollback()

    ##### Test main page views #####

    def test_signup(self):
        """Can user sign up?"""
        with self.client as c:
            resp = c.post("/signup", data={"username":"testyuser",
                                    "email":"testy@test.com",
                                    "password":"testyuser"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testyuser</a>', html)

    def test_signup_invalid_name(self):
        """Will user get warning if username or email already exists?"""
        with self.client as c:
            resp = c.post("/signup", data={"username":"testuser",
                                    "email":"testy@test.com",
                                    "password":"testyuser"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Username/email already exists', html)

    def test_signup_invalid_email(self):
        """Will user get warning for invalid email?"""
        with self.client as c:
            resp = c.post("/signup", data={"username":"testuser",
                                    "email":"testy",
                                    "password":"testyuser"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Invalid email address.', html)

    def test_signup_invalid_password(self):
        """Will user get warning for invalid password?"""
        with self.client as c:
            resp = c.post("/signup", data={"username":"testuser",
                                    "email":"testy",
                                    "password":"t"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Field must be at least 8 characters long.', html)