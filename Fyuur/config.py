import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
DBNAME = 'fyuur'
uname = 'postgres'
password ='desmond25'
url='localhost:5432'
# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = f'postgresql://{uname}:{password}@{url}/{DBNAME}'
SQLALCHEMY_TRACK_MODIFICATIONS = False
