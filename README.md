# Dive Atlas
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/4b0a3366dcff40f7be1ad3bf0fe24d30)](https://app.codacy.com/gh/blakes24/dive-atlas?utm_source=github.com&utm_medium=referral&utm_content=blakes24/dive-atlas&utm_campaign=Badge_Grade_Settings)
[![Coverage Status](https://coveralls.io/repos/github/blakes24/dive-atlas/badge.svg?branch=main)](https://coveralls.io/github/blakes24/dive-atlas?branch=main)
[![Maintainability](https://api.codeclimate.com/v1/badges/a773a8e737909036574e/maintainability)](https://codeclimate.com/github/blakes24/dive-atlas/maintainability)

[https://dive-atlas.herokuapp.com/](https://dive-atlas.herokuapp.com/)

## Description
This app helps scuba divers find new dive sites around the world and keep a record of their favorite spots.

## Setup Instructions
- Clone the repository `https://github.com/blakes24/dive-atlas.git`

- Go to [https://account.mapbox.com/auth/signup/](https://account.mapbox.com/auth/signup/) and sign up to get a Mapbox access token 

- Create a .env file in the main directory that contains:
	- `DEV_DATABASE_URL=postgres:///your_database_name`
	- `DATABASE_URL=postgres:///your_database_name`
	- `TEST_DATABASE_URL=postgres:///your_database_name`
	- `SECRET_KEY=yourSecretKeyHere`

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

### Resources
- Divestes API: [http://api.divesites.com/docs/](http://api.divesites.com/docs/)
- Mapbox API: [https://docs.mapbox.com/api/](https://docs.mapbox.com/api/)
