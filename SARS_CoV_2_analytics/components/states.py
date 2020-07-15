from components.repository import get_repo
from collections import namedtuple
import pandas as pd
import os


DataPoint  = namedtuple('DataPoint',  ['date', 'confirmed'])
DataPoint2 = namedtuple('DataPoint2', ['date', 'deaths'])


class ReadOnlyError(Exception):
    
    def __init__(self):
        super(ReadOnlyError, self).__init__('property is read-only access.')


class State:

    def __init__(self, 
            
            name, 
            lockdown, 

            ease_restrictions_I, 
            ease_restrictions_II, 
            ease_restrictions_III, 
            ease_restrictions_IV,

            mandatory_face_mask, 
            masks_enforced):

        self.__name                        = name
        self.__lockdown                    = lockdown

        self.__ease_restrictions_I         = ease_restrictions_I
        self.__ease_restrictions_II        = ease_restrictions_II
        self.__ease_restrictions_III       = ease_restrictions_III
        self.__ease_restrictions_IV        = ease_restrictions_IV

        self.__mandatory_face_mask         = mandatory_face_mask
        self.__masks_enforced              = masks_enforced

        self.__confirmed_cases_time_series = []
        self.__daily_confirmed_time_series = []
        self.__deaths_time_series          = []
        self.__daily_deaths_time_series    = []

    def __repr__(self):
        return self.name

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, val):
        raise ReadOnlyError()

    @property
    def lockdown(self):
        return self.__lockdown

    @lockdown.setter
    def lockdown(self, val):
        raise ReadOnlyError()

    @property
    def ease_restrictions_I(self):
        return self.__ease_restrictions_I

    @ease_restrictions_I.setter
    def ease_restrictions_I(self, val):
        raise ReadOnlyError()

    @property
    def ease_restrictions_II(self):
        return self.__ease_restrictions_II

    @ease_restrictions_II.setter
    def ease_restrictions_II(self, val):
        raise ReadOnlyError()

    @property
    def ease_restrictions_III(self):
        return self.__ease_restrictions_III

    @ease_restrictions_III.setter
    def ease_restrictions_III(self, val):
        raise ReadOnlyError()

    @property
    def ease_restrictions_IV(self):
        return self.__ease_restrictions_IV

    @ease_restrictions_IV.setter
    def ease_restrictions_IV(self, val):
        raise ReadOnlyError()

    @property
    def mandatory_face_mask(self):
        return self.__mandatory_face_mask

    @mandatory_face_mask.setter
    def mandatory_face_mask(self, val):
        raise ReadOnlyError()

    @property
    def masks_enforced(self):
        return self.__masks_enforced

    @masks_enforced.setter
    def masks_enforced(self, val):
        raise ReadOnlyError
    
    @property
    def time_series(self):
        return self.__confirmed_cases_time_series

    @time_series.setter
    def time_series(self, val):
        raise ReadOnlyError()

    @property
    def daily_time_series(self):
        return self.__daily_confirmed_time_series

    @daily_time_series.setter
    def daily_time_series(self, val):
        raise ReadOnlyError

    @property
    def deaths_time_series(self):
        return self.__deaths_time_series

    @deaths_time_series.setter
    def deaths_time_series(self, val):
        raise ReadOnlyError

    @property
    def daily_deaths_time_series(self):
        return self.__daily_deaths_time_series

    @daily_deaths_time_series.setter
    def daily_deaths_time_series(self, val):
        raise ReadOnlyError


class States(list):

    def __init__(self):
        self.__data_frames = {}
        self.__directory = ('SARS_CoV_2_analytics/data/COVID-19/'
                            'csse_covid_19_data/'
                            'csse_covid_19_daily_reports_us')
        self.__metadata = pd.read_csv(
            'SARS_CoV_2_analytics/data/states.csv')
        self.__initialize()

    def __repr__(self):
        return str([state.name for state in self])

    def __initialize(self):
        self.__load_states()
        self.__load_csse()
        self.__combine()
        self.__sort()
        #self.__clear()

    def __load_states(self):
        ''' Load states.csv metadata. '''
        for state in self.__metadata.iterrows():
            self.append(State(*state[1].values))
        
    def __load_csse(self):
        ''' Load csse daily reports us. '''
        for csv in os.listdir(self.__directory):
            try:
                date = csv.split('.')[0].replace('-', '/')[:8]
                self.__data_frames[date] = pd.read_csv(os.path.join(
                    self.__directory, csv))
            except pd.errors.EmptyDataError as README:
                pass
            except AttributeError as whoops:
                break

    def __combine(self):
        ''' Combine metadata with csse data. '''
        for state in self:
            for date in self.__data_frames.keys():
                try:
                    row = self.__data_frames[date][
                            self.__data_frames[date][
                                'Province_State'] == state.name]
                    data_point = DataPoint(date, row['Confirmed'].values[0])
                    state.time_series.append(data_point)
                except AttributeError as whoops:
                    break
        
    def __sort(self):
        ''' Sort state time series data. '''
        for state in self:
            state.time_series.sort()
    
    def __clear(self):
        ''' We are finished with these. '''

        # data attributes.
        del self.__data_frames
        del self.__directory
        del self.__metadata

        # methods.
        del __class__.__initialize
        del __class__.__load_states
        del __class__.__load_csse
        del __class__.__combine
        del __class__.__sort
        del __class__.__clear


class StatesTimeSeries(States):

    def __init__(self):
        self.__data_frame  = None
        self.__data_frame2 = None
        self._States__directory = ('SARS_CoV_2_analytics/data/COVID-19/'
                                   'csse_covid_19_data/'
                                    'csse_covid_19_time_series/')
        self._States__metadata  = pd.read_csv(
            'SARS_CoV_2_analytics/data/states.csv')
        self.__initialize()

    def __repr__(self):
        return super().__repr__()

    def __initialize(self):
        self.__load_states()
        self.__load_csse()
        self.__combine()
        self.__sort()
        #self.__clear()

    def __load_states(self):
        super()._States__load_states()
        
    def __load_csse(self):
        get_repo()
        fname   = 'time_series_covid19_confirmed_US.csv'
        fname2  = 'time_series_covid19_deaths_US.csv'
        target  = os.path.join(self._States__directory, fname)
        target2 = os.path.join(self._States__directory, fname2)
        self.__data_frame = pd.read_csv(target)
        self.__data_frame2 = pd.read_csv(target2)

    def __combine(self):
        for state in self:

            timeseries = self.__data_frame[
                self.__data_frame['Province_State'] == state.name
            ]

            timeseries2 = self.__data_frame2[
                self.__data_frame2['Province_State'] == state.name
            ]

            init2 = init = True
            do    =  do2 = False
            for date in timeseries.columns[11:]:

                confirmed_cases = sum(timeseries[date])
                deaths          = sum(timeseries2[date])

                if confirmed_cases > 10: do = True
                if deaths >= 1: do2 = True

                abnormal_date2 = abnormal_date = date
                date = '/'.join([str(number).zfill(2) for number in date.split('/')])

                if do:
                    if init:
                        init = False
                        initial_date = prev_date
                    datapoint = DataPoint(date, confirmed_cases)
                    state.time_series.append(datapoint)
                prev_date = abnormal_date

                if do2:
                    if init2:
                        init2 = False
                        initial_date2 = prev_date2
                    if deaths == 0:
                        deaths = prev_deaths
                    datapoint2 = DataPoint2(date, deaths)
                    state.deaths_time_series.append(datapoint2)
                prev_deaths = deaths
                prev_date2  = abnormal_date2

            if do2:
                self.__construct_daily_deaths(state, initial_date2, timeseries)
            if do:
                self.__construct_daily(state, initial_date, timeseries)

    def __construct_daily_deaths(self, state, initial_date, timeseries):
        initial_count = sum(
            timeseries[timeseries['Province_State'] == state.name][
                initial_date
            ]
        )
        backwards = list(reversed(state.deaths_time_series))
        for i in range(len(backwards)):
            date = backwards[i].date
            try:
                daily = backwards[i].deaths - backwards[i + 1].deaths
                if daily < 0:
                    daily = 0
            except IndexError:
                daily = backwards[i].deaths - initial_count
                if daily < 0:
                    daily = 0
            datapoint = DataPoint2(date, daily)
            state.daily_deaths_time_series.append(datapoint)
        state.daily_deaths_time_series.reverse()
        state.daily_deaths_time_series.sort()
        
    def __construct_daily(self, state, initial_date, timeseries):
        initial_count = sum(
            timeseries[timeseries['Province_State'] == state.name][
                initial_date])
        backwards = list(reversed(state.time_series))
        for i in range(len(backwards)):
            date  = backwards[i].date
            try:
                daily = backwards[i].confirmed - backwards[i + 1].confirmed
                if daily < 0:
                    daily = 0
            except IndexError:
                daily = backwards[i].confirmed - initial_count
                if daily < 0:
                    daily = 0
            datapoint = DataPoint(date, daily)
            state.daily_time_series.append(datapoint)
        state.daily_time_series.reverse()
        state.daily_time_series.sort()

    def __sort(self):
        super()._States__sort()        

    def __clear(self):

        # data attributes
        del self.__data_frame
        del self._States__directory
        del self._States__metadata

        # methods
        del __class__.__initialize
        del __class__.__load_states
        del __class__.__load_csse
        del __class__.__combine
        del __class__.__sort
        del __class__.__clear

        # inherited methods
        del States._States__initialize
        del States._States__load_states
        del States._States__load_csse
        del States._States__combine
        del States._States__sort
        del States._States__clear
        

if __name__ == '__main__':
    states = StatesTimeSeries()
