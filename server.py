#!/usr/bin/python3
import socket
import sys
import traceback
from threading import Thread
import subprocess
import os
from termios import tcflush, TCIFLUSH

def main():
    start_server()


def start_server():
    host = "127.0.0.1"
    port = 8888         # arbitrary non-privileged port

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   # SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state, without waiting for its natural timeout to expire
    #print("Socket created")

    try:
        soc.bind((host, port))
    except:
        print("Bind failed. Error : " + str(sys.exc_info()))
        sys.exit()

    soc.listen(5)       # queue up to 5 requests
    print("File server now listening on {}:{} ...".format(host, port))
    subprocess.call(['gnome-terminal','-e','python3 server_chat.py'])
    tcflush(sys.stdin, TCIFLUSH)



    # infinite loop- do not reset for every requests
    while True:
        connection, address = soc.accept()
        ip, port = str(address[0]), str(address[1])
        print("Connected with " + ip + ":" + port)

        try:
            Thread(target=client_thread, args=(connection, ip, port)).start()
        except:
            print("Thread did not start.")
            traceback.print_exc()

    soc.close()


def client_thread(connection, ip, port, max_buffer_size = 2048):
    is_active = True

    while is_active:
        print("Waiting for incomming transmission...")
        client_input = receive_input(connection, max_buffer_size)

        if "--QUIT--" in client_input:
            print("Client is requesting to quit")
            connection.close()
            print("Connection " + ip + ":" + port + " closed")
            is_active = False
        

        elif "--download" in client_input:
            print ("Host request to download")
            #connection.sendall("you request to download".encode("utf8"))
            # send the request download file
            download_file(connection, ip, port, client_input) 
        

        elif "--upload" in client_input:
            print ("Host request to upload")
            upload_file(connection, ip, port, client_input)
            
        

        else:
            print("Processed result: {}".format(client_input))
            connection.sendall("-".encode("utf8"))


def receive_input(connection, max_buffer_size):
    client_input = connection.recv(max_buffer_size)
    client_input_size = sys.getsizeof(client_input)

    if client_input_size > max_buffer_size:
        print("The input size is greater than expected {}".format(client_input_size))

    decoded_input = client_input.decode("utf8")
    result = process_input(decoded_input)

    return result


def process_input(input_str):
    print("Processing the input received from client")

    return "Hello " + str(input_str)

def download_file (connection, ip, port, client_input):
    parsing = client_input.split()

    #separte the items need to be download from the command (--download Hello.txt goobye.csv)
    items = parsing[2:]
    for i in items:
        print(i)
        Download_Process(connection)
    
def Download_Process(sock):
    filename = sock.recv(2048).decode('utf8')
    print(filename)
    filename = "/home/wayne/qt/Project_socket/File_folder/"+filename

    if os.path.isfile(filename):
        sock.send(("EXISTS " + str(os.path.getsize(filename))).encode('utf8'))             
        userResponse = sock.recv(2048).decode('utf8')
        if userResponse[:2] == 'OK':
            with open(filename, 'rb') as f:
                i = 0
                bytesToSend = f.read(2048)
                sock.send(bytesToSend)

                print("sent!" + str(i))
                i = i + 1
                while i<100000:
                    bytesToSend = f.read(2048)
                    sock.send(bytesToSend)
                    print("sent" + str(i))
                    i = i + 1


            f.close()
    else:
        sock.send("ERR ".encode('utf8'))

    print("Finish Retriving")

def upload_file(connection, ip, port, client_input):
    parsing = client_input.split()
    items = parsing[2:]
    for i in items:
        print(i)
        Upload_process(i, connection)


def Upload_process(filename, connection):
    if filename != 'q':
        connection.send(filename.encode('utf8'))
        print("sending "+filename)
        data = connection.recv(2048).decode('utf8')
        print("data: " + data)
        if data[:6] == 'EXISTS':
            filesize = int(data[6:])
            message = 'Y'
            if message == 'Y':
                connection.send("OK".encode('utf8'))
                f = open('/home/wayne/qt/Project_socket/File_folder/'+filename, 'wb')
                data = connection.recv(2048)
                totalRecv = len(data)
                f.write(data)
                while totalRecv < filesize:
                    data = connection.recv(2048)
                    totalRecv += len(data)
                    f.write(data)
                    print ("{0:.2f}".format((totalRecv/float(filesize))*100)+ "% Done")
                print ("upload complete!")
                f.close()
        else:
            print ("File Does Not Exist!")


if __name__ == "__main__":
    main()
