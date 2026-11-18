import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

x = np.array([0, 1, 2, 3], dtype=float)
y = np.array([93.75, 86.96, 84.22, 77.57], dtype=float)

def decay_func(x, a, b):
    return a * np.exp(-b*x)

params, covariance = curve_fit(decay_func, x, y)
a, b = params

x_fit = np.linspace(0, 4, 100)
y_fit = decay_func(x_fit, a, b)

def cycle_ratio():
    return decay_func(4, a, b) / y[-1]

