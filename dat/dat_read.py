import numpy as np
import os

path = os.getcwd()
array = np.fromfile('{}/cipher0.dat'.format(path))
print(array)