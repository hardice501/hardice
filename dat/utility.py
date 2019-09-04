import csv
from hashlib import sha256
import os

def Write_file(file,Data) :
    with open(file,'a',encoding='utf-8') as f :
        writer = csv.writer(f,delimiter=',',quotechar='|',quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerow(Data)

def Write_file_list(file,Data) :
        with open(file,'a',encoding='utf-8') as f :
                for data in Data :
                        f.write(str(data)+"\n")

def Open_file(file) :
    data = list()
    with open(file,'r',encoding='utf-8',errors='ignore') as f :
        reader = csv.reader(f)
        for line in reader :            
            data.append(line)

    return data

def Edit_file(file,search_data,edit_data,index) :
        data = Open_file(file)
        new_data = list()
        for d in data :
                if search_data in d :
                        d[index] = edit_data
                new_data.append(d)
        with open(file,'w',encoding='utf-8') as f :
                writer = csv.writer(f,delimiter=',',quotechar='|',quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
                for d in new_data :
                        writer.writerow(d)
        
def file_len(file):
    with open(file) as f:
        i = 0
        for l in f:
            i+=1
        return i

def Delete_file(file,delete_data) :
    data = Open_file(file)
    new_data = list()
    for d in data :
        if delete_data in d :
                continue
        new_data.append(d)
    with open(file,'w',encoding='utf-8') as f :
        writer = csv.writer(f,delimiter=',',quotechar='|',quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        for d in new_data :
                writer.writerow(d)

def getUserPath(location ,HashData) :
        Str = ""
        temp = int(location/2)
        mul = 0
        Treepath = list()
        for i in range(1,16) :
                if location %2 == 0  :
                        Str =  "1" + Str
                else :
                        Str = "0"+Str
                mul += pow(2,16-i)
                midHashValue = str(HashData[location]).split()
                Treepath.append(midHashValue[1])
                Treepath.append(midHashValue[2])
                Treepath.append(midHashValue[3].replace("']",""))
                if i == 1 :
                        leafNodeHashValue = list()
                        if location % 2== 0 :
                                leafNodeHashValue = str(HashData[location+1]).split()
                        else :
                                leafNodeHashValue = str(HashData[location-1]).split()
                        Treepath.append(leafNodeHashValue[1])
                        Treepath.append(leafNodeHashValue[2])
                        Treepath.append(leafNodeHashValue[3].replace("']",""))

                location = mul + temp
                
                if i == 16-1 :
                        pass
                else :
                        temp = int(temp/2)
        return int(Str,2),Treepath

def Hash(input) :
    return int(sha256(str(input).encode()).hexdigest(),16)
