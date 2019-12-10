#!/usr/bin/python3
def Load():
    f = open("Credentials.csv","r")
    usrname, password, DOB, Note = f.readline().split(',')
    credentials = {}
    while usrname != "<Eof>" and password != "<Eof>":
        usrname, password, DOB, Note = f.readline().split(',')
        credentials.update({usrname:[password, DOB, Note]})
    f.close()


    return credentials

