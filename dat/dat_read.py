import subprocess
import os
from Crypto.Hash import SHA256 # pycryptodome 라이브러리 설치 필요

def dat_read(path):
    dat_process = subprocess.Popen(["xxd", "-p", '{}'.format(path)], stdout=subprocess.PIPE)
    dat_string = dat_process.communicate()[0]
    return dat_string


if __name__ == '__main__':
    path = os.getcwd()+'/dat/CRS.dat'
    data = dat_read(path)
    digest = SHA256.new()
    digest.update(data)
    CRS_sha256 = digest.hexdigest()
    print(CRS_sha256)
    process = subprocess.Popen(["intkey", "set", "{}".format(CRS_sha256.encode())])
    output = process.communicate()