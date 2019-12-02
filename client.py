#!/usr/bin/python3
import socket
import sys
import subprocess
import os
import traceback
from termios import tcflush, TCIFLUSH


def main():
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "127.0.0.1"
    port = 8888

    #subprocess.call(['gnome-terminal','-e','python3 client_chat.py'])

    try:
        connection.connect((host, port))
    except:
        print("Connection error")
        sys.exit()

    print("Enter 'quit' to exit")
    subprocess.call(['gnome-terminal','-e','python3 client_chat.py'])
    tcflush(sys.stdin, TCIFLUSH)
    message = input("-> ")
    



    #encrypt message truoc khi gui

    while message != 'quit':
        connection.sendall(message.encode("utf8"))

        if "start-chat" in message:
            print("Opening chat services!")
            subprocess.call(['gnome-terminal','-e','python3 client_chat.py'])
            tcflush(sys.stdin, TCIFLUSH)

        elif "--download" in message:

            parsing = message.split()
            items = parsing[1:]
            for i in items:
                filename = i
                Download_process(filename, connection)

        elif "--upload" in message:
            parsing = message.split()
            items = parsing[1:]
            for i in items:
                filename = i
                Upload_process(connection)



        else:
        	response = connection.recv(2048).decode("utf8")
        	if response == "-":
        		pass
        	else:
        		print(response)
        		        
	        
        message = input("-> ")

    connection.send(b'--quit--')

def Download_process(filename, s):
    if filename != 'q':
        s.send(filename.encode('utf8'))
        data = s.recv(2048).decode('utf8')
        if data[:6] == 'EXISTS':
            filesize = int(data[6:])
            message = input("File exists, " + str(filesize) +"Bytes, download? (Y/N)? -> ")
            if message == 'Y':
                s.send("OK".encode('utf8'))
                f = open('/home/wayne/qt/Project_socket/Download/'+filename, 'wb')
                data = s.recv(2048)
                totalRecv = len(data)
                f.write(data)
                while totalRecv < filesize:
                    data = s.recv(2048)
                    totalRecv += len(data)
                    f.write(data)
                    print ("{0:.2f}".format((totalRecv/float(filesize))*100)+ "% Done")
                print ("Download Complete!")
                f.close()
        else:
            print ("File Does Not Exist!")


def Upload_process(Connection):
    filename = Connection.recv(2048).decode('utf8')
    print("receving " +filename)
    name = filename
    filename = "/home/wayne/qt/Project_socket/Download/" + filename
    print("the path is " + filename)

    if os.path.isfile(filename):
        Connection.send(("EXISTS " + str(os.path.getsize(filename))).encode('utf8'))
        print("Uploading...")
        userResponse = Connection.recv(2048).decode('utf8')
        if userResponse[:2] == 'OK':
            with open(filename, 'rb') as f:
                i = 0
                bytesToSend = f.read(2048)
                Connection.send(bytesToSend)

                print("sent!" + str(i))
                i = i + 1
                while i<100000:
                    bytesToSend = f.read(2048)
                    Connection.send(bytesToSend)
                    print("sent" + str(i))
                    i = i+1


            f.close()
    else:
        Connection.send("ERR ".encode('utf8'))
        print("The file " + name + " doesn't exist!")

    print("Finish Retriving")

if __name__ == "__main__":
    main()