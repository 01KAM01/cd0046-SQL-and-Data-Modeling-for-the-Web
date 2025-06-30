import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# DONETODO IMPLEMENT DATABASE URL
# usually would remove the password but left it as this is just a leaning exercise only
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:abc@127.0.0.1:5432/kamalFyyurNatwest'
SQLALCHEMY_TRACK_MODIFICATIONS = False # suppressing to reduce overhead
# disabling CSRF
WTF_CSRF_ENABLED = False