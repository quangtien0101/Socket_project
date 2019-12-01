#!/usr/bin/python3
import socket
import sys
import subprocess

def main():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "127.0.0.1"
    port = 8888

    #subprocess.call(['gnome-terminal','-e','python3 client_chat.py'])

    try:
        soc.connect((host, port))
    except:
        print("Connection error")
        sys.exit()

    print("Enter 'quit' to exit")
    message = input("-> ")



    #encrypt message truoc khi gui

    while message != 'quit':
        soc.sendall(message.encode("utf8"))

        if "--chat--" in message:
            print("Opening chat services!")
            subprocess.call(['gnome-terminal','-e','python3 client_chat.py'])

        if "--download" in message:

            parsing = message.split()
            items = parsing[1:]
            for i in items:
                filename = i
                Download_process(filename, soc)



        else:
        	response = soc.recv(5120).decode("utf8")
        	if response == "-":
        		pass
        	else:
        		print(response)
        		        
	        
        message = input("-> ")

    soc.send(b'--quit--')

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


if __name__ == "__main__":
    main()