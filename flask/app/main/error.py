from flask import render_template
from . import main

@main.errorhandler(404)
def pag_not_find(e):
    return render_template('404.html'), 404
@main.errorhandler(500)
def pag_not_find(e):
    return render_template('500.html'), 500
