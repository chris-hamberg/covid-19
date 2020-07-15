from SARS_CoV_2_analytics.components.repository import get_repo
from SARS_CoV_2_analytics.application import main as application
from threading import Thread
import datetime, os


TIMESTAMP = os.path.join(
    'SARS_CoV_2_analytics', 'data', 'timestamp')
PLOTS     = os.path.join('static', 'plots')


class Application(Thread):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Application, cls).__new__(cls)
        return cls.instance

    def __init__(self, daemon=True, *args, **kwargs):
        super().__init__(daemon=daemon, *args, **kwargs)

    def run(self):
        get_repo()
        application()

        #try:
        #    timestamp = get_timestamp()
        #    assert timestamp
        #except AssertionError:
            #for fname in os.listdir(PLOTS):
            #    name = os.path.join(PLOTS, fname)
            #    os.remove(name)
        #    application()

        #if datetime.datetime.utcnow() > timestamp:
            #for fname in os.listdir(PLOTS):
            #    name = os.path.join(PLOTS, fname)
            #    os.remove(name)
        #    application()

        #elif len(os.listdir(PLOTS)) == 0:
        #    application()


def get_timestamp():
    try:
        with open(TIMESTAMP) as timestamp:
            timestamp = float(timestamp.read())
        timestamp = datetime.datetime.fromtimestamp(timestamp)
        return timestamp
    except FileNotFoundError:
        return None
    except ValueError:
        return None
