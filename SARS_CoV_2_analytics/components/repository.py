import datetime, logging, os, time


logger = logging.getLogger()


PATH = ('SARS_CoV_2_analytics/data/COVID-19/csse_covid_19_data/'         
       'csse_covid_19_time_series/'
       'time_series_covid19_confirmed_US.csv')


def get_timestamp():
    path = 'SARS_CoV_2_analytics/data/timestamp'
    if not os.path.exists(path):
        set_timestamp()
    with open(path) as fhand:
        try:
            timestamp = float(fhand.read())
        except ValueError as error:
            set_timestamp()
            timestamp = float(fhand.read())
    return timestamp


def set_timestamp():
    path = 'SARS_CoV_2_analytics/data/timestamp'
    timestamp = (
            datetime.datetime.utcnow() + datetime.timedelta(hours=24
                )).timestamp()
    with open(path, 'w') as fhand:
        fhand.write(str(timestamp))


def get_now():
    return datetime.datetime.utcnow().timestamp()


def record_update():
    with open('SARS_CoV_2_analytics/data/record', 'w'
            ) as fhand_des, open(PATH) as fhand_src:
        r = fhand_src.read()
        fhand_des.write(r)


def get_repo():
    if not os.path.exists('SARS_CoV_2_analytics/data/COVID-19'):
        #os.chdir('SARS_CoV_2_analytics/data')
        os.system('git clone https://github.com/CSSEGISandData/COVID-19.git '
                  'SARS_CoV_2_analytics/data/COVID-19')
        #os.chdir('../../')
        wait_on_clone()
    elif get_now() >= get_timestamp():
        #os.chdir('SARS_CoV_2_analytics/data/COVID-19')
        os.system('git pull origin master '
                  'SARS_CoV_2_analytics/data/COVID-19')
         
        #os.chdir('../../../')
        wait_on_update()
    else:
        logger.info('get_repo : conditional case not met.')
    record_update()
    set_timestamp()


def wait_on_clone():
    while not os.path.exists(PATH):
        logger.info('Waiting for clone.')
        time.sleep(.3)


def wait_on_update():
    count = 0
    with open('SARS_CoV_2_analytics/data/record') as old:
        old = old.read()
        while count < 90:
            with open(PATH) as new:
                if old == new.read():
                    count += 1
                    time.sleep(.3)
                    continue
                else:
                    break


def main():
    get_repo()


if __name__ == '__main__':
    main()
