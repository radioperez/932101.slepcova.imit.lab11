import random
import numpy as np
from numpy.random import default_rng
import scipy.stats
import matplotlib.pyplot as plt

a = 0
sigma = 1
N_TRIALS = 10

OBSERVED = default_rng().normal(a, sigma, size=N_TRIALS)

x = np.linspace(min(OBSERVED), max(OBSERVED), N_TRIALS)
EXPECTED = scipy.stats.norm.pdf(x, a, sigma)

hist, _ = np.histogram(OBSERVED)
FREQUENCY = [stat / N_TRIALS for stat in hist]
print(EXPECTED, FREQUENCY)
plt.show()
