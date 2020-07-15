from components.states import StatesTimeSeries as States
from components.regression import best_fit as line
from matplotlib import pyplot as plt
from statistics import mean
from math import log
import numpy as np
import pathlib
import time
import os


if os.path.exists('SARS_CoV_2_analytics/data/regressions.txt'):
    os.remove('SARS_CoV_2_analytics/data/regressions.txt')


# NOTE ### find the best fit line ####
#                                    #
FIT_TYPE = ''                        #
#                                    #
######################################


# NOTE ### bounding parameters ####
#                                 #
#exponent = 2                     #
#                                 #
###################################


# NOTE ##### Reference Functions ###################################
#                                                                   #
# Quadratic                                                         #
#f = lambda n: n**exponent; BOUND_TYPE = 'quadratic'                #
#                                                                   #
# Log Linear                                                        #
#f = lambda n: n * log(n or n + 1); BOUND_TYPE = 'log linear'       #
#                                                                   #
# Linear                                                            #
f = lambda n: n; BOUND_TYPE = 'linear'                             #
#                                                                   #
# Logarithmic                                                       #
#f = lambda n: log(n or n + 1); BOUND_TYPE = 'logarithmic           #
#                                                                   #
#####################################################################


# NOTE ### Witnesses ####
#                       #
C = 200                 #
#                       #
#########################


class Plot:

    def __init__(self, state, best_fit): # best_fit function, ex. linear regression

        self.__plt = plt

        # data
        self.__X           = []
        self.__Y           = []
        self.__upper_bound = []

        # additional metadata
        self.__best_fit    = best_fit # a function
        self.__fit_type    = ''
        self.__error       = float('inf')
        self.__line        = []
        self.__legend      = []
        self.__f           = ''

        # compositors
        self.__state     = state
        self.style       = Style(       self.__state, self.__plt, self.__legend)
        self.metadata    = PlotMetadata(self.__state, self,       self.__legend, 
                self.__error, self.__f)
        
    def generate_plots(self, type='cumulative', show=False):
        if   type == 'cumulative':
            self.analytic()
            title = 'Cumulative Confirmed Cases'
            self.synthetic(True)
            line = True
        elif type == 'daily':
            self.analytic2()
            title = 'Daily Confirmed Cases'
            self.synthetic()
            line = False
        elif type == 'deaths':
            if self.__state.deaths_time_series:
                self.analytic3()
                title = 'Cumulative Deaths'
                self.synthetic()
                line = True
            else:
                return None
        elif type == 'daily_deaths':
            if self.__state.daily_deaths_time_series:
                self.analytic4()
                title = 'Daily Deaths'
                self.synthetic()
                line = False
            else:
                return None

        self.plot(line=line)
        #self.metadata.lockdown()
        #self.metadata.masks()
        #self.metadata.ease()
        self.style.set_style(title)
        self.save(type)
        if show:
            plt.show()
        plt.close()

    def plot(self, line=True):
        self.__plt.bar(self.__X, self.__Y,     color='magenta',   label='data',
                align='center', alpha=0.66)
        if line:
            self.__plt.plot(self.__X, self.__line, color='darkcyan',  label='best_fit',  
                    linewidth=3)
            self.__legend.append(f'{self.__fit_type}')
            global FIT_TYPE
            FIT_TYPE = self.__fit_type

    def save(self, type):
        name      = pathlib.Path(self.__state.name + '_' + type
            ).with_suffix('.png')
        #directory = 'SARS_CoV_2_analytics/data/plots'
        directory = 'static/plots'
        target    = os.path.join(directory, name)
        facecolor = self.__plt.axes().figure.get_facecolor()
        if not os.path.exists(directory):
            os.mkdir(directory)
        elif os.path.isfile(directory):
            fname = directory
            os.remove(fname)
            os.mkdir(directory)
        self.__plt.savefig(target, facecolor=facecolor)

    def analytic(self):
        ''' process analytic data for cumulative confirmed cases. '''
        self.__X  = np.array(list(map(lambda n: n.date,      self.__state.time_series)))
        self.__Y  = np.array(list(map(lambda n: n.confirmed, self.__state.time_series)))
        self.metadata._X  = self.__X

    def analytic2(self):
        ''' Same as above, but for confirmed cases daily. '''
        self.__X = np.array(list(map(lambda n: n.date,      self.__state.daily_time_series)))
        self.__Y = np.array(list(map(lambda n: n.confirmed, self.__state.daily_time_series)))
        self.metadata._X  = self.__X

    def analytic3(self):
        ''' process analytic data for deaths. '''
        self.__X = np.array(list(map(lambda n: n.date,      self.__state.deaths_time_series)))
        self.__Y = np.array(list(map(lambda n: n.deaths,    self.__state.deaths_time_series)))
        self.metadata._X = self.__X

    def analytic4(self):
        ''' process analytic data for daily deaths. '''
        self.__X = np.array(list(map(lambda n: n.date,      self.__state.daily_deaths_time_series)))
        self.__Y = np.array(list(map(lambda n: n.deaths,    self.__state.daily_deaths_time_series)))
        self.metadata._X = self.__X

    def synthetic(self, record=False):
        ''' generate synthetic data '''
        X = range(len(self.__X))
        self.__upper_bound   = np.array([C       * abs(f(x)) for x in X])
        self.__line, self.__fit_type, self.__f, self.__error = self.__best_fit(
            self.__X, self.__Y)
        Y = max([sorted(self.__Y), sorted(self.__line)],
            key=lambda t: t[-1])
        self.metadata._f     = self.__f
        self.metadata._Y     = Y
        self.metadata._error = self.__error
        self.style._fit_type = self.__fit_type
        global REGRESSION
        global ERROR
        REGRESSION = self.__f
        ERROR = self.__error

        if record:
            with open('SARS_CoV_2_analytics/data/regressions.txt', 'a'
                ) as fhand:
                fhand.write(f'{self.__state.name} : {self.__f}\n\n')


class PlotMetadata:

    def __init__(self, state, plt, legend, error, f):
        self._state  = state
        self._X      = []
        self._Y      = []
        self._plt    = plt
        self._legend = legend
        self._error  = error
        self._f      = f
        self._vert   = 0.6 # figtext starting y-axis position.

    def lockdown(self):

        if isinstance(self._state.lockdown, str):

            date  = self._state.lockdown[:-2]

            def _plot():
                xlock = [date] * len(self._X)
                self._plt._Plot__plt.plot(xlock, self._Y, color='blue',
                    label='lockdown', linewidth=3)
                self._legend.append('Lock Down')

            def _write():
                self._plt._Plot__plt.figtext(0.14, self._vert,
                    f'Lock Down : {date}', fontsize=11, color='cyan')
                self._vert -= 0.03
            
            try:
                deaths_time_series = all(self._plt._Plot__Y == np.array([
                    d for _, d in self._state.deaths_time_series
                ]))
            except TypeError:
                deaths_time_series = False

            try:
                daily_deaths_time_series = all(self._plt._Plot__Y == np.array([
                    d for _, d in self._state.daily_deaths_time_series
                ]))
            except TypeError:
                daily_deaths_time_series = False
            
            if deaths_time_series:
                # We are traversing the deaths time series
                if date < self._state.deaths_time_series[0].date:
                    # the date isn't on the x-axis
                    _write()
                else:
                    _plot()
            elif daily_deaths_time_series:
                # We are traversing the daily deaths time series
                if date < self._state.daily_deaths_time_series[0].date:
                    # the date isn't on the x-axis
                    _write()
                else:
                    _plot()
            else:
                _plot()
            
    def masks(self):

        def __plot_date():
            face_mask = self._state.mandatory_face_mask
            if isinstance(self._state.mandatory_face_mask, float):
                face_mask = '       Null'
            elif '/' in self._state.mandatory_face_mask:
                face_mask = face_mask[:-2]
                xmask = [face_mask] * len(self._X)
                self._plt._Plot__plt.plot(xmask, self._Y, '--', color='royalblue',
                        label='masks', linewidth=3)
                self._legend.append('Face Masks')
            elif face_mask == 'TRUE':
                face_mask = '       True'
            else:
                face_mask = '       Null'
            self._plt._Plot__plt.figtext(0.14, self._vert,
                    f'Face Masks : {face_mask}', fontsize=11, color='cyan')
            self._vert -= 0.03

        def __write_enforced():
            if isinstance(self._state.mandatory_face_mask, float):
                value = 'Null'
            elif self._state.masks_enforced == float('nan'):
                value = 'Null'
            else:
                value = 'True'
            self._plt._Plot__plt.figtext(0.14, self._vert, 
                    f'Masks Enforced : {value}', 
                    fontsize=11, color='cyan')
            self._vert -= 0.03

        if self._state.mandatory_face_mask:
            __plot_date()
            __write_enforced()
            
    def ease(self):

        NUMERALS = ('I', 'II', 'III', 'IV')

        def __get_easements():
            easements = []
            for n in NUMERALS:
                string = getattr(self._state, f'ease_restrictions_{n}')
                string = str(string)[:-2]
                if string in self._X:
                    easements.append(string)
            return easements

        def __plot(xease, string):
            self._plt._Plot__plt.plot(xease, self._Y, color='red',
                    label=string, linewidth=3)
            self._legend.append(string)

        for e, easement in enumerate(__get_easements()):
            string = f'Eased Restrictions {NUMERALS[e]}'
            try:
                xease = [easement] * len(self._X)
                __plot(xease, string)
            except (ValueError, TypeError):
                pass


class Style:

    def __init__(self, state, plt, legend):

        # Data
        self.__state    = state

        # API
        self.__ax       = plt.gca()
        self.__suptitle = plt.suptitle
        self.__legend   = plt.legend
        self.__leg_list = legend
        self.__setp     = plt.setp
        self.__xticks   = plt.xticks
        self.__yticks   = plt.yticks
        self.__ylabel   = plt.ylabel
        self.__figtext  = plt.figtext
        self.__gcf      = plt.gcf

        # Styling
        self.__title_color   = 'cyan'
        self.__legend_color  = 'grey'
        self.__legend_alpha  = 0.2
        self.__legend_text   = 'darkgrey'
        self.__tick_rotation = 20
        self.__xtick_color   = 'lightgrey'
        self.__ytick_color   = 'grey'
        self.__ylabel_color  = 'cyan'
        self.__border_color  = 'black'
        self.__plot_bg_color = '#111111'
        self.__spine_color   = 'darkcyan'                                

    def set_style(self, title='Confirmed Cases'):
        self.__set_title(title)
        self.__set_legend()
        self.__set_ticks()
        self.__set_labels(title)
        self.__set_facecolors()
        self.__set_spines()
        self.__set_subtitle()
        self.__set_size()

    def __set_title(self, title):
        self.__suptitle(
            f'{title} in {self.__state.name} has a {FIT_TYPE.split(" ")[0]} '
            f'Best Fit Function\n'
            f'{REGRESSION}\n'
            f'with Coefficient of Determination : ${ERROR}$',
            color=self.__title_color)
                #f'with constant witnesses $C = {C}$, $C\\prime = {C_PRIME}$, '
                #f'and $k = {k}$'), color=self.__title_color)

    def __set_legend(self):
        leg = self.__legend(self.__leg_list, facecolor=self.__legend_color, 
            framealpha=self.__legend_alpha, loc=0)
        self.__setp(leg.get_texts(), color=self.__legend_text)

    def __set_ticks(self):
        self.__xticks(color=self.__xtick_color, rotation=self.__tick_rotation)
        self.__yticks(color=self.__ytick_color)

    def __set_labels(self, title):
        self.__ylabel(f'{title}', color=self.__ylabel_color)
        for idx, label in enumerate(self.__ax.axes.xaxis.get_ticklabels()):
            if idx%10:
                label.set_visible(False)

    def __set_facecolors(self):
        self.__ax.figure.set_facecolor(self.__border_color)
        self.__ax.patch.set_facecolor( self.__plot_bg_color)

    def __set_spines(self):
        self.__ax.spines['bottom'].set_color(self.__spine_color)
        self.__ax.spines['left'  ].set_color(self.__spine_color)
        self.__ax.spines['top'   ].set_color(self.__spine_color)
        self.__ax.spines['right' ].set_color(self.__spine_color)

    def __set_subtitle(self):
        self.__figtext(0.5, 0.01, 
                'dataset: systems.jhu.edu/research/public-health/ncov/',
                wrap=True, ha='center', fontsize=10, color=self.__title_color)

    def __set_size(self):
        self.__gcf().set_size_inches(13, 6.5)


def main():
    for state in States():
        print(state.name)
        plot = Plot(state, line)
        plot.generate_plots('cumulative', False)
        plot = Plot(state, line)
        plot.generate_plots('daily', False)
        plot = Plot(state, line)
        plot.generate_plots('deaths', False)
        plot = Plot(state, line)
        plot.generate_plots('daily_deaths', False)


if __name__ == '__main__':
    main()
