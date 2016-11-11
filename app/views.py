from flask import render_template, flash, redirect
from app import app
import json
import random

@app.route('/')
@app.route('/index')
def index():
    with open('app/static/peeps/peeps.json') as f:
        peeps = json.load(f)
        peep = random.choice(peeps)
    return render_template('index.html',
                           peep = peep)