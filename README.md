# Dive Atlas
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/4b0a3366dcff40f7be1ad3bf0fe24d30)](https://app.codacy.com/gh/blakes24/dive-atlas?utm_source=github.com&utm_medium=referral&utm_content=blakes24/dive-atlas&utm_campaign=Badge_Grade_Settings)
[![Coverage Status](https://coveralls.io/repos/github/blakes24/dive-atlas/badge.svg?branch=main)](https://coveralls.io/github/blakes24/dive-atlas?branch=main)
[![Maintainability](https://api.codeclimate.com/v1/badges/a773a8e737909036574e/maintainability)](https://codeclimate.com/github/blakes24/dive-atlas/maintainability)

## Description
This app helps scuba divers find new dive sites around the world and keep a record of their favorite spots.

## Setup Instructions
- Clone the repository

- Go to [https://account.mapbox.com/auth/signup/](https://account.mapbox.com/auth/signup/) and sign up to get a Mapbox access token 

- Create a .env file in the main directory that contains:
	- `DATABASE_URL=postgres:///your_database_name`
	- `SECRET_KEY=yourSecretKeyHere`

- Do the following in the Terminal:
	- `python3 -m venv venv`
	- `source venv/bin/activate`
	- `pip install -r requirements.txt`
	- `createdb <your_database_name>`
	- `python seed.py`
	- `flask run`

- To run a file containing unittests, use following command:
	- `FLASK_ENV=production python -m unittest <name-of-python-file>`

### Resources
- Divestes API: [http://api.divesites.com/docs/](http://api.divesites.com/docs/)
- Mapbox API: [https://docs.mapbox.com/api/](https://docs.mapbox.com/api/)
