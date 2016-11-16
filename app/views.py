"""Views from the app"""

import json
import random
from flask import render_template
from app import app


@app.route('/')
@app.route('/index')
def index():
    """Base page"""
    with open('app/static/peeps/peeps.json') as peeps_file:
        peeps = json.load(peeps_file)
        peep = random.choice(peeps)

    preambles = (
        "Did you guess it?",
        "I bet you got it...",
        "Did I stump you?",
        "Obviously,",
        "Oh right,"
        "You're too good,"
        "Hope you're having fun!"
        "Say my name."
        "Who am I?"
        "Whaddaya know,"
        )
    answer_preamble = random.choice(preambles)

    return render_template(
        'index.html', peep=peep, answer_preamble=answer_preamble)
