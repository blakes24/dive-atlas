"""View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest tests/test_views.py

from app import app

from unittest import TestCase

from models import db, User

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///dive_test"


db.create_all()

# Don't have WTForms use CSRF

app.config["WTF_CSRF_ENABLED"] = False


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

        u2 = User.signup(
            email="tester22@test.com",
            username="tester22",
            password="password22",
        )
        db.session.add(u2)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()

    ##### Test main page views #####

    def test_signup(self):
        """Can user sign up?"""
        with self.client as c:
            resp = c.post(
                "/signup",
                data={
                    "username": "testyuser",
                    "email": "testy@test.com",
                    "password": "testyuser",
                },
                follow_redirects=True,
            )
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testyuser</a>", html)

    def test_signup_invalid_name(self):
        """Will user get warning if username or email already exists?"""
        with self.client as c:
            resp = c.post(
                "/signup",
                data={
                    "username": "testuser",
                    "email": "testy@test.com",
                    "password": "testyuser",
                },
                follow_redirects=True,
            )
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Username/email already exists", html)

    def test_signup_invalid_email(self):
        """Will user get warning for invalid email?"""
        with self.client as c:
            resp = c.post(
                "/signup",
                data={
                    "username": "testuser",
                    "email": "testy",
                    "password": "testyuser",
                },
                follow_redirects=True,
            )
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Invalid email address.", html)

    def test_signup_invalid_password(self):
        """Will user get warning for invalid password?"""
        with self.client as c:
            resp = c.post(
                "/signup",
                data={"username": "testuser", "email": "testy", "password": "t"},
                follow_redirects=True,
            )
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Field must be at least 8 characters long.", html)

    def test_login(self):
        """Can user log in?"""

        with self.client as c:
            resp = c.post(
                "/login",
                data={"username": "testuser", "password": "password"},
                follow_redirects=True,
            )
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser</a>", html)

    def test_login_invalid(self):
        """Does user get error message for invalid credentials?"""

        with self.client as c:
            resp = c.post(
                "/login",
                data={"username": "testuser", "password": "wrongpwd"},
                follow_redirects=True,
            )
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Invalid credentials.", html)

    def test_logout(self):
        """Can user log out?"""

        # change the session to mimic logging in
        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = self.u.id

            resp = c.get("/logout", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("You have been logged out.", html)

    def test_home_logged_out(self):
        """Does it display logged out navbar?"""

        with self.client as c:
            resp = c.get("/", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<a class="nav-link" href="/login">Sign In</a>', html)
            self.assertNotIn(
                '<a class="nav-link" href="/bucketlist">Bucket List</a>', html
            )

    def test_home_logged_in(self):
        """Does it display logged in navbar?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = self.u.id

            resp = c.get("/", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                '<a class="nav-link" href="/bucketlist">Bucket List</a>', html
            )
            self.assertNotIn('<a class="nav-link" href="/login">Sign In</a>', html)

    def test_edit_user(self):
        """Does it edit a user's info?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = self.u.id

            resp = c.post(
                "/user/edit",
                data={
                    "username": "testuser2",
                    "email": "test@test.com",
                    "password": "password",
                },
                follow_redirects=True,
            )
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser2</a>", html)

    def test_edit_user_invalid(self):
        """Does it show an error message if user tries to edit profile with wrong password?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = self.u.id

            resp = c.post(
                "/user/edit",
                data={
                    "username": "testuser2",
                    "email": "test@test.com",
                    "password": "wrongpwd",
                },
                follow_redirects=True,
            )
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Invalid credentials.", html)

    def test_edit_user_duplicate(self):
        """Does it show an error message if user tries to change to taken username/email?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = self.u.id

            resp = c.post(
                "/user/edit",
                data={
                    "username": "tester22",
                    "email": "test@test.com",
                    "password": "password",
                },
                follow_redirects=True,
            )
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Username or email is already taken.", html)

    def test_edit_logged_out(self):
        """Does it redirect user if not logged in?"""
        with self.client as c:

            resp = c.get(
                "/user/edit",
                follow_redirects=True,
            )
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    def test_site_search_term(self):
        """Does it return results from the API when given a search term?"""
        with self.client as c:
            resp = c.post("/sites/search", json={"mode": "search", "str": "pinnacle"})

            res = resp.get_data(as_text=True)

            self.assertIn("true", res)
            self.assertIn("pinnacle", res)
            self.assertIn('"We found', res)

    def test_site_search_coord(self):
        """Does it return results from the API when given coordinates?"""
        with self.client as c:
            resp = c.post(
                "/sites/search",
                json={"mode": "sites", "lat": 32, "lng": -117, "dist": 100},
            )

            res = resp.get_data(as_text=True)

            self.assertIn("true", res)
            self.assertIn('"32"', res)
            self.assertIn('"-117"', res)

    def test_error_handler(self):
        """Does it display error page?"""
        with self.client as c:
            # "/" route should not work with post
            resp = c.post("/")

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 500)
            self.assertIn("Looks like something went wrong.", html)
