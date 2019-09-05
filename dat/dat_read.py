import os
import subprocess

path = os.getcwd()

dat_process = subprocess.Popen(["xxd", "-p", '{}/cipher0.dat'.format(path)], stdout=subprocess.PIPE)
dat_string = dat_process.communicate()[0]
print(dat_string)