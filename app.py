import sys
sys.path.insert(0, 'SARS_CoV_2_analytics')

from SARS_CoV_2_analytics.application import States
from application_thread import get_timestamp
from application_thread import Application
from collections import namedtuple
from flask import render_template
from flask import url_for
from flask import Flask
import generate_html
import urllib.parse
import datetime
import os


PLOTS  = os.path.join('static', 'plots')
app    = Flask(__name__)
states = States()
thread = Application()


def timestamp():
    timestamp = get_timestamp()
    if timestamp:
        format = '%r UTC on %A %D'
        timestamp = timestamp.strftime(format)
    return timestamp or '(information not available)'


Plot = namedtuple('Plot', ['type', 'image', 'rank'])


@app.route('/')
def index():

    stamp = timestamp()
    date = datetime.datetime.utcnow()
    date -= datetime.timedelta(days=1)
    #date += datetime.timedelta(days=1)

    global thread
    if thread.isAlive():
        pass
    elif (
            timestamp() == '(information not available)' 
            ) or (
            date.timestamp() >= get_timestamp().timestamp()
            ) or (
            len(os.listdir('static/plots')) <= 188
            ):

        thread = Application()
        thread.start()

    return render_template('index.html', states=states, timestamp=stamp)


@app.route('/<name>')
def state(name):
    plots     = [plot for plot in os.listdir(PLOTS) if name in plot]
    plots     = [os.path.join(PLOTS, plot) for plot in plots]
    plots     = [urllib.parse.quote(plot) for plot in plots]
    stamp     = timestamp()
    page      = f'{name}.html'

    temp = []
    for image in plots:
        type = " ".join(image.split('_')[1:])
        type = type.split('.')[0].title()
        if   type == 'Cumulative':
            type = 'Cumulative Confirmed Cases'
            rank = 0
        elif type == 'Daily':
            type = 'Daily Confirmed Cases'
            rank = 1
        elif type == 'Deaths':
            type = 'Cumulative Deaths'
            rank = 2
        else:
            rank = 3
        temp.append(Plot(type, image, rank))
    plots = temp
    plots.sort(key=lambda p: p.rank)

    return render_template(page, timestamp=stamp, plots=plots, name=name)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
