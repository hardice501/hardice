import subprocess
import os

def dat_read(path):
    dat_process = subprocess.Popen(["xxd", "-p", '{}'.format(path)], stdout=subprocess.PIPE)
    dat_string = dat_process.communicate()[0]
    return dat_string

if __name__ == '__main__':
    path = os.getcwd()+'/dat/CRS.dat'
    data = dat_read(path)
    process = subprocess.Popen(["intkey", "set", "{}".format(data)])
    output = process.communicate()
    print(output)