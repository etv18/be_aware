"""Pages are an empty shell: the script of the page asks the controllers (JSON) for the data and draws it."""
from flask import render_template


def page(nav, script, title, **params):
    """`script` is the file in static/js/pages (without .js). `params` become data-attributes of #app."""
    return render_template('page.html', nav=nav, script=script, title=title, params=params)
