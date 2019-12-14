#!/usr/bin/python3
def Write(credentials):
    f = open("Credentials.csv", "w")
    f.writelines("UserName,Password,DOB,Note\n")
    for u in credentials:
        f.writelines(u+","+credentials[u][0]+','+credentials[u][1]+","+credentials[u][2]+"\n")
    
    #f.writelines("<Eof>,<Eof>,<Eof>,<Eof>")
    f.close