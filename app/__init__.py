"""Application."""

import os
import requests
import logging
import reverse_geocode

from flask import Flask, render_template, flash, redirect, session, g, request
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from models import  User, db, connect_db, Dive_site, Bucket_list_site, Journal_entry
from forms import UserAddForm, LoginForm, JournalSiteForm

from dotenv import load_dotenv
from config import config


app = Flask(__name__)


def create_app(config_name):
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    connect_db(app)
    return app

# attach routes and custom error pages here
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
    return render_template('index.html')


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


@app.route("/user/edit", methods=["GET", "POST"])
def edit_profile():
    """Update profile for current user."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = UserAddForm(obj=g.user)

    if form.validate_on_submit():
        user = User.authenticate(g.user.username, form.password.data)

        if user:
            try:
                user.username = (form.username.data,)
                user.email = (form.email.data,)

                db.session.commit()

                flash("Profile Updated", "success")
                return redirect("/")

            except IntegrityError:
                db.session().rollback()
                flash("Username or email is already taken.", "danger")
                return redirect("/user/edit")

        flash("Invalid credentials.", "danger")

    return render_template("user-form.html", form=form, user_id=g.user.id)


@app.route("/user/delete", methods=["POST"])
def delete_user():
    """Delete user."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    session.pop("user_id", None)

    db.session.delete(g.user)
    db.session.commit()
    flash("User Deleted", "danger")

    return redirect("/")


@app.route("/sites/search", methods=["POST"])
def get_sites():
    """Send request to api to get list of dive sites based on provided search parameters."""
    params = request.json

    res = requests.get("http://api.divesites.com", params=params)

    data = res.json()

    return data


@app.route("/sites/<int:site_id>")
def show_site(site_id):
    """Show site details"""
    site = Dive_site.query.get(site_id)

    if not site:
        res = requests.get(
            "http://api.divesites.com", params={"mode": "detail", "siteid": site_id}
        )

        data = res.json()
        lat = float(data["site"]["lat"])
        lng = float(data["site"]["lng"])
        coords = [(lat, lng)]
        loc = reverse_geocode.search(coords)
        location = f"{loc[0]['city']}, {loc[0]['country']}"

        new_site = Dive_site(
            id=site_id,
            name=data["site"]["name"],
            lng=lng,
            lat=lat,
            description=data["site"]["description"],
            location=location,
        )

        db.session.add(new_site)
        db.session.commit()

        return render_template("site-detail.html", site=new_site)

    return render_template("site-detail.html", site=site)


@app.route("/bucketlist", methods=["GET", "POST"])
def add_bucketlist_site():
    """Add site to user's bucket list."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    if request.method == "POST":
        dive_site_id = request.json["id"]
        site = Dive_site.query.get(dive_site_id)
        if site in g.user.bucket_list:
            return {"message": "This site is already in your bucket list."}
        bl_site = Bucket_list_site(dive_site_id=dive_site_id, user_id=g.user.id)
        db.session.add(bl_site)
        db.session.commit()
        return {"message": "Site added to bucket list"}

    sites = g.user.bucket_list

    return render_template("bucket-list.html", sites=sites)


@app.route("/bucketlist/<int:site_id>/delete", methods=["POST"])
def delete_bucketlist_site(site_id):
    """Deletes a site from bucket list and returns deleted message."""
    site = Bucket_list_site.query.filter(
        Bucket_list_site.user_id == g.user.id, Bucket_list_site.dive_site_id == site_id
    ).first()

    db.session.delete(site)
    db.session.commit()

    return {"message": "Deleted"}


@app.route("/journal")
def show_dive_journal():
    """Show sites in users dive journal."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    sites = g.user.dive_journal

    return render_template("dive-journal.html", sites=sites)


@app.route("/journal/<int:site_id>/add", methods=["GET", "POST"])
def add_journal_site(site_id):
    """Add site to user's dive journal."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = JournalSiteForm()
    site = Dive_site.query.get(site_id)
    entry = Journal_entry.query.filter(
        Journal_entry.user_id == g.user.id, Journal_entry.dive_site_id == site_id
    ).first()
    if entry in g.user.dive_journal:
        flash("Site already in dive journal.", "danger")
        return redirect(f"/sites/{site_id}")

    if form.validate_on_submit():
        description = form.description.data
        notes = form.notes.data
        rating = form.rating.data

        entry = Journal_entry(
            dive_site_id=site_id,
            description=description,
            notes=notes,
            rating=rating,
            user_id=g.user.id,
        )
        db.session.add(entry)
        db.session.commit()

        flash("Site added to dive journal.", "success")
        return redirect("/")

    return render_template("journal-form.html", form=form, site=site)


@app.route('/journal/<int:entry_id>')
def show_journal_detail(entry_id):
    """Show dive journal site detail."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    entry = Journal_entry.query.get_or_404(entry_id)

    return render_template('journal-detail.html', entry=entry)

@app.route('/journal/<int:entry_id>/delete', methods=["POST"])
def remove_site(entry_id):
    """Delete a dive site from journal."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    entry = Journal_entry.query.get(entry_id)
    db.session.delete(entry)
    db.session.commit()

    flash("Site deleted.", "danger")
    return redirect('/journal')

@app.route('/journal/<int:entry_id>/edit', methods=["GET", "POST"])
def edit_journal(entry_id):
    """Edit dive journal entry."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    entry = Journal_entry.query.get_or_404(entry_id)
    form = JournalSiteForm(obj=entry)

    if form.validate_on_submit():
        form.populate_obj(entry)
        db.session.add(entry)
        db.session.commit()
        flash("Site updated.", "success")
        return redirect(f'/journal/{entry.id}')

    return render_template('journal-form.html', form=form, site=entry.dive_site)

@app.errorhandler(Exception)
def server_error(e):
    """Display error page. Log error message with stack trace."""
    app.logger.error("An error occured", e)
    db.session().rollback()
    return render_template("error.html"), 500
