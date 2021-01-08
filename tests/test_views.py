"""View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest tests/test_views.py

from app import app

from unittest import TestCase

from models import db, User, Dive_site, Bucket_list_site, Journal_entry

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

    def test_delete_user(self):
        """Does it delete the user?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = self.u.id

            resp = c.post("/user/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("User Deleted", html)

    def test_delete_user_logged_out(self):
        """Does it redirect userif they are logged out?"""
        with self.client as c:
            resp = c.post("/user/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    ##### Test dive site views #####

    def setup_dive_sites(self):
        """Setup for dive site tests."""
        site1 = Dive_site(
            name="Site1",
            id=1,
            lng=20,
            lat=10,
            description="Not real.",
            location="somewhere",
        )

        db.session.add(site1)
        db.session.commit()

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

    def test_show_site(self):
        """Does it display site details?"""
        self.setup_dive_sites()

        with self.client as c:
            resp = c.get("/sites/1", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="text-center">Site1</h1>', html)

    def test_show_site_api(self):
        """Does it get site info from api, add to database, and display details?"""
        self.setup_dive_sites()

        with self.client as c:
            resp = c.get("/sites/17251", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(Dive_site.query.all()), 2)
            self.assertIn('<h1 class="text-center">Treasure Island</h1>', html)

    def test_show_site_logged_out(self):
        """Does it display logged out site details view?"""
        self.setup_dive_sites()

        with self.client as c:
            resp = c.get("/sites/1", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p><a href="/login">Sign in</a> to add a review </p>', html)
            self.assertNotIn(
                '<button class="dropdown-item" id="bucket-list-add" data-id="1">Add to bucket list</button>',
                html,
            )

    def test_show_site_logged_in(self):
        """Does it display logged in site details view?"""
        self.setup_dive_sites()

        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = self.u.id

            resp = c.get("/sites/1", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                '<button class="dropdown-item" id="bucket-list-add" data-id="1">Add to bucket list</button>',
                html,
            )
            self.assertNotIn(
                '<p><a href="/login">Sign in</a> to add a review </p>', html
            )

    ##### Test bucket list views #####

    def setup_bucket_list(self):

        site1 = Dive_site(
            name="Site1",
            id=1,
            lng=20,
            lat=10,
            description="Not real.",
            location="somewhere",
        )
        site2 = Dive_site(
            name="Site2", id=2, lng=50, lat=30, description="Fake", location="someplace"
        )
        db.session.add_all([site1, site2])
        db.session.commit()

        bl_site = Bucket_list_site(dive_site_id=1, user_id=self.u.id)
        db.session.add(bl_site)
        db.session.commit()

    def test_show_bucket_list(self):
        """Does it display user's bucket list?"""
        self.setup_bucket_list()

        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = self.u.id

            resp = c.get("/bucketlist", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Site1</a>", html)
            self.assertNotIn("Site2</a>", html)

    def test_bucket_list_unauthorized(self):
        """Does it redirect the user if they are not logged in?"""
        self.setup_bucket_list()

        with self.client as c:
            resp = c.get("/bucketlist", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    def test_bucket_list_add(self):
        """Does it add a site to the user's bucket list?"""
        self.setup_bucket_list()

        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = self.u.id

            resp = c.post("/bucketlist", json={"id": 2})
            data = resp.json

            self.assertEqual(data, {"message": "Site added to bucket list"})

    def test_add_existing(self):
        """Does it prevent user from adding duplicates to bucket list?"""
        self.setup_bucket_list()

        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = self.u.id

            resp = c.post("/bucketlist", json={"id": 1})
            data = resp.json

            self.assertEqual(
                data, {"message": "This site is already in your bucket list."}
            )

    def test_bucket_list_delete(self):
        """Does it delete a site from user's bucket list?"""
        self.setup_bucket_list()

        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = self.u.id

            resp = c.post("/bucketlist/1/delete")
            data = resp.json

            self.assertEqual(data, {"message": "Deleted"})
            self.assertEqual(len(Bucket_list_site.query.all()), 0)

    ##### Test dive journal views #####

    def setup_dive_journal(self):

        site1 = Dive_site(
            name="Site1",
            id=1,
            lng=20,
            lat=10,
            description="Not real.",
            location="somewhere",
        )
        site2 = Dive_site(
            name="Site2", id=2, lng=50, lat=30, description="Fake", location="someplace"
        )
        db.session.add_all([site1, site2])
        db.session.commit()

        entry = Journal_entry(dive_site_id=1, user_id=self.u.id, rating=3, notes="ok")
        db.session.add(entry)
        db.session.commit()

    def test_show_dive_journal(self):
        """Does it display user's dive journal?"""
        self.setup_dive_journal()

        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = self.u.id

            resp = c.get("/journal", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Site1</a>", html)
            self.assertNotIn("Site2</a>", html)

    def test_show_journal_unauthorized(self):
        """Does it redirect the user if they are not logged in?"""
        self.setup_dive_journal()

        with self.client as c:
            resp = c.get("/journal", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    def test_journal_add_form(self):
        """Does it display form to add site to dive journal?"""
        self.setup_dive_journal()

        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = self.u.id

            resp = c.get("/journal/2/add", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Description (public)", html)

    def test_journal_duplicate(self):
        """Does it prevent user from adding duplicates to dive journal?"""
        self.setup_dive_journal()

        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = self.u.id

            resp = c.get("/journal/1/add", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Site already in dive journal.", html)

    def test_journal_add(self):
        """Does it add site to dive journal?"""
        self.setup_dive_journal()

        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = self.u.id

            resp = c.post(
                "/journal/2/add",
                data={"description": "dive site", "notes": "cool", "rating": 4},
                follow_redirects=True,
            )
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Site added to dive journal.", html)

    def test_journal_add_unauthorized(self):
        """Does it redirect the user if they are not logged in?"""
        self.setup_dive_journal()

        with self.client as c:
            resp = c.post(
                "/journal/2/add",
                data={"description": "dive site", "notes": "cool", "rating": 4},
                follow_redirects=True,
            )
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    def test_journal_details(self):
        """Does it show journal details page?"""
        self.setup_dive_journal()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = self.u.id

            resp = c.get("/journal/1", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="text-center">Site1</h1>', html)
            self.assertIn('<p>ok</p>', html)

    def test_journal_detail_unauthorized(self):
        """Does it redirect the user if they are not logged in?"""
        self.setup_dive_journal()

        with self.client as c:
            resp = c.get("/journal/1", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    def test_journal_delete(self):
        """Does it delete a dive journal entry?"""
        self.setup_dive_journal()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = self.u.id

            resp = c.post("/journal/1/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Site deleted.', html)
            self.assertNotIn('Site1', html)

    def test_journal_delete_unauthorized(self):
        """Does it redirect the user if they are not logged in?"""
        self.setup_dive_journal()

        with self.client as c:
            resp = c.post("/journal/1/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    def test_journal_edit_form(self):
        """Does it display form to edit dive journal?"""
        self.setup_dive_journal()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = self.u.id

            resp = c.get("/journal/1/edit", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Description (public)', html)
            self.assertIn('ok</textarea>', html)

    def test_journal_edit_unauthorized(self):
        """Does it redirect the user if they are not logged in?"""
        self.setup_dive_journal()

        with self.client as c:
            resp = c.get("/journal/1/edit", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    def test_journal_edit(self):
        """Does it edit dive journal?"""
        self.setup_dive_journal()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = self.u.id

            resp = c.post("/journal/1/edit", data={"description":"meh", "notes":"so so", "rating":3}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Site updated.', html)
            self.assertIn('<p>so so</p>', html)
            self.assertNotIn('ok', html)

    def test_error_handler(self):
        """Does it display error page?"""
        with self.client as c:
            # "/" route should not work with post
            resp = c.post("/")

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 500)
            self.assertIn("Looks like something went wrong.", html)
