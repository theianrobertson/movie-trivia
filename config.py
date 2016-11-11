import os
basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True
with open('key.secret') as f:
    SECRET_KEY = f.read()

