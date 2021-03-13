# Dive Atlas

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/4b0a3366dcff40f7be1ad3bf0fe24d30)](https://app.codacy.com/gh/blakes24/dive-atlas?utm_source=github.com&utm_medium=referral&utm_content=blakes24/dive-atlas&utm_campaign=Badge_Grade_Settings)
[![Coverage Status](https://coveralls.io/repos/github/blakes24/dive-atlas/badge.svg?branch=main)](https://coveralls.io/github/blakes24/dive-atlas?branch=main)
[![Maintainability](https://api.codeclimate.com/v1/badges/a773a8e737909036574e/maintainability)](https://codeclimate.com/github/blakes24/dive-atlas/maintainability)

[https://dive-atlas.herokuapp.com/](https://dive-atlas.herokuapp.com/)

## Description

This app helps scuba divers discover new dive sites and keep a record of past dives.

### Features

**All users can:**

- Use the interactive world map to search for dive sites
- View dive site descriptions and reviews

**Registered users can:**

- Save dive sites they want to visit in the future to their Bucket List
- Review dive sites and view reviews from other users
- Keep track of their favorite dives in their Dive Journal

## Setup Instructions

- Clone the repository `https://github.com/blakes24/dive-atlas.git`

- Go to [https://account.mapbox.com/auth/signup/](https://account.mapbox.com/auth/signup/) and sign up to get a Mapbox access token

- Create a .env file in the main directory that contains:

  - `DEV_DATABASE_URL=postgres:///your_database_name`
  - `DATABASE_URL=postgres:///your_database_name`
  - `TEST_DATABASE_URL=postgres:///your_database_name`
  - `SECRET_KEY=yourSecretKeyHere`
    - `MAIL_SERVER=smtp.your_email_server`
    - `MAIL_USERNAME=your_email_username`
    - `MAIL_PASSWORD=your_email_password`
    - `SECURITY_PASSWORD_SALT=hard_to_guess_string`

- Set up a virtual environment:

  - `python3 -m venv .env`
  - `source .env/bin/activate`

- Install project requirements:

  - `pip3 install -r requirements.txt`

- Create a local Database(I used postgresql for this project)

  - `createdb <your_database_name>`

- Seed test data:

  - `python3 seed.py`

- Run the application:

  - `python3 run.py`

- Got to the browser and access the application on:
  - `localhost:5000`
- To run tests, use the command below:
  - `FLASK_ENV=production python -m unittest <name-of-python-file>`

## Endpoints

### User

- `/signup` **GET**: shows form **POST**: creates an account
- `/login` **GET**: shows form **POST**: logs in user
- `/logout` **POST**: logs out user
- `/user/edit` **GET**: shows edit form **POST**: updates user info
- `/user/delete` **POST**: deletes user
- `/confirm` **GET**: asks user to confirm email
- `/resend` **GET**: resends confirmation email
- `/confirm/<token>` **GET**: confirms user account if token is valid

### Searching for dive sites

- `/` **GET**: shows homepage where users can search for dive sites
- `/sites/search` **POST**: shows list of dive sites based on search criteria
- `/sites/<int:site_id>` **GET**: displays additional details about a dive site

### Features For Authorized Users

- `/bucketlist` **GET**: shows bucket list **POST**: adds dive site to bucket list
- `/bucketlist/delete` **POST**: removes dive site from bucket list
- `/journal` **GET**: shows list of dive sites in journal
- `/journal/<int:site_id>` **GET**: shows details about dive site
- `/journal/<int:site_id>/add` **GET**: shows add form **POST**: adds dive site to dive journal
- `/journal/<int:site_id>/edit` **GET**: shows edit form **POST**: updates information about dive site
- `/journal/<int:site_id>/delete` **POST**: removes dive site from dive journal

## Tech Stack

### Backend

- Python
- PostgreSQL
- Flask
- SQLAlchemy

### Frontend

- JavaScript
- Ajax
- HTML
- CSS
- Bootstrap 4
- Mapbox GL JS

### Resources

- Divestes API: [http://api.divesites.com/docs/](http://api.divesites.com/docs/)
- Mapbox API: [https://docs.mapbox.com/api/](https://docs.mapbox.com/api/)
