import numpy as np
import os

path = os.getcwd()
array = np.fromfile('{}/dat/cipher0.dat'.format(path), dtype=float)
print(array[0])