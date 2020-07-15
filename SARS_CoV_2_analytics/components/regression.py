from statistics import mean
from statistics import StatisticsError
import numpy as np
import scipy.optimize


def best_fit(X, Y):

    logarithmic = *_, error1 = logarithmic_regression(X, Y)
    linear      = *_, error2 = linear_regression(     X, Y)
    quadratic   = *_, error3 = quadratic_regression(  X, Y)

    errors = [(logarithmic, error1), (linear, error2), (quadratic, error3)]
    error  = max(errors, key=lambda t: t[-1])

    print(f'logarithmic: {error1}    linear: {error2}    quadratic: {error3}')
    
    return error[0]


def logarithmic_regression(X, Y):
    '''
    https://stackoverflow.com/questions/49944018/
    fit-a-logarithmic-curve-to-data-points-and-extrapolate-out-in-numpy
    '''

    X = np.arange(len(X), dtype=np.float)
    
    X[0] = 1

    regression = lambda X, a, b: a + b*np.log(X)

    def fit(X, Y):
        sum_Y    = np.sum(Y)
        sum_logx = np.sum(np.log(X))
        b = (X.size * np.sum( Y * np.log(X)) - sum_Y * sum_logx) / (
             X.size * np.sum( np.log(X) ** 2 ) - sum_logx ** 2
        )
        a = (sum_Y - b * sum_logx) / X.size
        return a, b

    regression_line = regression(X, *fit(X, Y))
    error    = coefficent_of_determination(regression_line, Y)
    function = 'f(n) = a + b log(n)'

    return regression_line, 'Logarithmic Regression', function, error
    

def linear_regression(X, Y):
    ''' https://pythonprogramming.net/ '''
    X1 = X
    X  = np.array([i for i in range(len(X))])
    
    m  = (
            ((mean(X) * mean(Y)) - mean(X * Y)) / 
            ((mean(X)**2) - mean(X*X))
            
        )
    b  = mean(Y) - m*mean(X)

    regression_line = np.array([(m*x)+b for x in X])
    error = coefficent_of_determination(regression_line, Y)
    m = str(m)
    m = m.split('.')
    m = '.'.join([m[0], m[1][:1]])
    m = float(m)
    b = str(b)
    b = b.split('.')
    b = '.'.join([b[0], b[1][:1]])
    b = float(b)
    function = f'$f\\langle n \\rangle \\approx {m} n + \\langle {b} \\rangle$'
    return regression_line, 'Linear Regression', function, error


def quadratic_regression(X, Y):
    X = np.array([i for i in range(len(X))])
    a, b, c = np.polyfit(X, Y, 2)
    f = lambda n: a * n ** 2 + b * n + c
    regression_line = [f(n) for n in X]
    error = coefficent_of_determination(regression_line, Y)
    function = f'$f \\langle n \\rangle \\approx {a}n^2 + {b}n + \\langle{c}\\rangle$'
    return regression_line, 'Quadratic Regression', function, error


def coefficent_of_determination(regression_line, Y):
    '''
    https://www.wallstreetmojo.com/r-squared-formula/

    https://pythonprogramming.net/
    r-squared-coefficient-of-determination-machine-learning-tutorial/
    ?completed=/how-to-program-best-fit-line-machine-learning-tutorial/
    '''
    try:
        assert len(Y) == len(regression_line)
        indices = range(len(Y))
        error   = np.array([0] * len(indices))
        total   = np.array([0] * len(indices))
        for idx in indices:
            total[idx] = Y[idx] - mean(Y)
            error[idx] = regression_line[idx] - Y[idx]
        total = sum(total ** 2)
        error = sum(error ** 2)
        r2 = 1 - (error / total)
        return round(r2, 2)
    except AssertionError as failure:
        return float('-inf')
