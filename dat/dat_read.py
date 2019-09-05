import os
import subprocess

def dat_read(path):
    dat_process = subprocess.Popen(["xxd", "-p", '{}'.format(path)], stdout=subprocess.PIPE)
    dat_string = dat_process.communicate()[0]
    return dat_string