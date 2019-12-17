#!/usr/bin/python3
import socket
import sys
import traceback
from threading import Thread
import subprocess
import os
from termios import tcflush, TCIFLUSH

from cryptography.fernet import Fernet
import Load_credentials
import Write_credentials
import affineCipher
import random
from _socket import gethostbyname
#load KEY and Credential
file = open('secret_key.key', 'rb')
KEY = file.read() # The key will be type bytes
file.close()
decrypt_f = Fernet(KEY)

credentials = Load_credentials.Load()

online_users = {}

chat_room = {}

#HOST_ADDRESS = gethostbyname()
def main():
    start_server()


def start_server():
    host = "127.0.0.1"
    port = 8888        


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
    #subprocess.Popen("gnome-terminal -x python chat_server.py 127.0.0.1 12345", stdout=subprocess.PIPE,stderr=None,shell=True)
    #tcflush(sys.stdin, TCIFLUSH)




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
    
    #Wait for the client to be authenticate first
    Wait_for_authentication = True
    username = ""
    while Wait_for_authentication:
        print("Waiting for user authentication...")
        client_input = receive_input(connection, max_buffer_size)
        if "--login" in client_input:
            print("User is try to login")
            # l = {"obama": ["yobama", "1/2/1970", "Bruh!"]}
            #check for the username("--login -u Obama -p Bruh!")
            print(client_input)
            parsing = client_input.split()
            if len(parsing) != 6:
                connection.sendall("Invalid argument numbers!".encode('utf8'))
                pass
            if parsing[2] != '-u' and parsing[4] != '-p' and parsing[1] != '--login':
                connection.sendall('Invalid arguments for username and password'.encode('utf8'))
                pass
            
            else:
                username = parsing[3]
                print(username)
                password = parsing[5]
                print(password)
                
                for u in credentials:
                    print(u +":"+credentials[u][0])
                    if (username == u):
                        if (credentials[u][0].strip('\n') == password):
                            connection.sendall(("OK "+username).encode('utf8'))
                            Wait_for_authentication = False
                            break

                if Wait_for_authentication == True:
                    connection.sendall("ERR! Wrong username or password!".encode('utf8'))



            
        else:
            if Wait_for_authentication == False:
                break
            print("Processed result: {}".format(client_input))
            connection.sendall("-".encode("utf8"))
    

    is_active = True
    online_users.update({username: ip}) 
    while is_active:
        print("Waiting for incomming transmission...")
        client_input = receive_input(connection, max_buffer_size)

        if "--QUIT--" in client_input:
            print("Client is requesting to quit")
            connection.close()
            print("Connection " + ip + ":" + port + " closed")
            is_active = False
            del online_users[username]
        
        elif "--change_password" in client_input:
            change_password(client_input,connection,username)

        elif "--change_info" in client_input:
            change_info(client_input, connection, username)
        elif "--download" in client_input:
            print ("Host request to download")
            #connection.sendall("you request to download".encode("utf8"))
            # send the request download file
            download_file(connection, ip, port, client_input) 
        

        elif "--upload" in client_input:
            print ("Host request to upload")
            if "--change_name" in client_input:
                print("Host request to change name when upload")
                parsing = client_input.split()
                if len(parsing) < 5:
                    print("Invalid argument number")
                    pass
                else:
                    filename = parsing[3]
                    newfilename = parsing[4]
                    Upload_process(filename,connection,newfilename)

            elif "--encrypt" in client_input:
                print("Host request to encrypt message during uploading - Server will decrypt the message")
                parsing = client_input.split()
                if len(parsing) != 4:
                    print("Invalid argument number")
                    pass
                else:
                    filename = parsing[3]
                    Upload_process(filename,connection,"default",True)

            else:
                upload_file(connection, ip, port, client_input)
            
        elif "--list --online" in client_input:
            print("Host request to get the online users")

            users = ""
            for i in online_users:
                print(i)
                users = users + i + ","

            print(users)
            connection.sendall(users.encode('utf8'))

        elif "--list --info" in client_input:
            print("User want to know his/her info")
            info = credentials[username]
            s = info[1] + "," + info[2]
            
            connection.sendall(s.encode('utf8'))

        elif "--list --room" in client_input:
            print("Host request to get available room")
            room = ""
            if len(chat_room) == 0:
                print("There is 0 room")
                connection.sendall("Null".encode('utf8'))
            else:
                for i in chat_room:
                    print(i)
                    print(chat_room[i])
                    room = room + str(chat_room[i]) +";"
                print(room)
                connection.sendall(room.encode('utf8'))

        elif "--list --server" in client_input:
            #message = os.system("cd /File_folder && ls")
            proc = subprocess.Popen("cd File_folder && ls", shell=True, stdout=subprocess.PIPE, )
            message=proc.communicate()[0]
            #output = output.decode('utf8')
            #message = output.split('\n')
            connection.sendall(message)
        elif "--chat" in client_input:
            parsing = client_input.split()
            print(parsing)
            name = parsing[-1]
            port = random.randrange(35358,36000,1)
            print (port)
            chat_room.update({port:[username,name]})
            
            connection.sendall(str(port).encode('utf8'))
            subprocess.Popen("gnome-terminal -x python chat_server.py 127.0.0.1 "+str(port), stdout=subprocess.PIPE,stderr=None,shell=True)

        elif "--join --room" in client_input:
        #    "--join --room U-request Owner's room"
            parsing = client_input.split()
            if len(parsing) != 5:
                print("Invalid arguments in join room")
                connection.sendall("ERR! owners name is wrong!")
            else:
                f = True
                owners = parsing[4]
                user = parsing[3]
                l = [owners]
                l.append(user)
                for p in chat_room:
                    if l == chat_room[p]:
                        connection.sendall(("OK!"+str(p)).encode('utf8'))
                        f= False
                        break
                if f == True:
                    connection.sendall("ERR! The given name or the room is incorrect!")
            #print(parsing)
            
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


def Upload_process(filename, connection, newfilename = "default", decrypt = False):
    if newfilename == "default":
        newfilename = filename
    if filename != 'q':
        connection.send(filename.encode('utf8'))
        print("asking for the file "+filename)
        data = connection.recv(2048).decode('utf8')
        print("data: " + data)
        if data[:6] == 'EXISTS':
            filesize = int(data[6:])
            message = 'Y'
            if message == 'Y':
                connection.send("OK".encode('utf8'))
                f = open('/home/wayne/qt/Project_socket/File_folder/'+newfilename, 'wb')
                data = connection.recv(2048)
                totalRecv = len(data)
                print("About to write")


                f.write(data)
                while totalRecv < filesize:
                    data = connection.recv(2048)

                    # if decrypted == True:
                    #     encrypt_file = data
                    #     data = decrypt_f.decrypt(encrypt_file)
                    #     print("Decrypted")

                    totalRecv += len(data)
                    f.write(data)
                    print ("{0:.2f}".format((totalRecv/float(filesize))*100)+ "% Done")
                print ("upload complete!")
                f.close()


                if decrypt == True:
                    decrypt_file(newfilename)
                create_encrypted_file(newfilename)
                
        else:
            print ("File Does Not Exist!")

def create_encrypted_file(filename):
    if ".txt" not in filename:
        print("Cannot encrypt non txt file")
        
    else:
        file_directory = "/home/wayne/qt/Project_socket/File_folder/Encrypted/" + filename
        f_in =  open('/home/wayne/qt/Project_socket/File_folder/' + filename, "r")
        f_out = open(file_directory, 'w')
        message = f_in.read()
        f_in.close()
        encrypted_message = affineCipher.execute("encrypt", message)
        f_out.write(encrypted_message)

        
        f_out.close()

def decrypt_file(filename):
    if ".txt" not in filename:
        print("Cannot decrypt non txt file")
        
    else:
        file_directory = "/home/wayne/qt/Project_socket/File_folder/" + filename
        f_in =  open('/home/wayne/qt/Project_socket/File_folder/' + filename, "r")
        
        message = f_in.read()
        f_in.close()
        f_out = open(file_directory, 'w')
        encrypted_message = affineCipher.execute("decrypt", message)
        f_out.write(encrypted_message)

        
        f_out.close()

def change_password(client_input, connection, usrname):
    #check for credentials
    #credentials[usrname][0]
    print(client_input)
    parsing = client_input.split()
    if len(parsing) != 8:
        connection.sendall("Invalid argument numbers!".encode('utf8'))
        pass
    elif parsing[2] != '-u' and parsing[4] != '-p' and parsing[1] != '--login' and parsing[6] != '-np':
        connection.sendall('Invalid arguments for username and password'.encode('utf8'))
        pass
    elif parsing[3] != usrname:
        connection.sendall("Invalid username!").encode('utf8')
    else:
        username = parsing[3]
        print(username)
        password = parsing[5]
        print(password)
        
        new_password = parsing[7]
        print(new_password)

        for u in credentials:
            print(u +":"+credentials[u][0])
            if (username == u):
                if (credentials[u][0].strip('\n') == password):
                    connection.sendall(("OK").encode('utf8'))

                    #write a new password
                    info = credentials[usrname]
                    DOB, Note = info[1], info[2]
                    credentials.update({usrname: [new_password, DOB, Note]})
                    print("Change password successfuly!")
                    Write_credentials.Write(credentials)
                    break

def change_info(client_input, connection, usrname):
    print(client_input)
    parsing = client_input.split()
    #if len(parsing) != 10:
    #    connection.sendall("Invalid argument numbers!".encode('utf8'))
    if parsing[2] != '-u' and parsing[4] != '-p' and parsing[1] != '--login' and parsing[6] != '-dob':
        connection.sendall('Invalid arguments'.encode('utf8'))
    elif parsing[3] != usrname:
        connection.sendall("Invalid username!").encode('utf8')
    else:
        username = parsing[3]
        print(username)
        password = parsing[5]
        print(password)
        
        DOB = parsing[7]
        print(DOB)

        Note = ""
        n = parsing[9:]

        for i in n:
            Note += i
            Note += " "

        print (Note)
        for u in credentials:
            #print(u +":"+credentials[u][0])
            if (username == u):
                if (credentials[u][0].strip('\n') == password):
                    connection.sendall(("OK ").encode('utf8'))

                    #write a new password
                    info = credentials[usrname]
                    credentials.update({usrname: [password, DOB, Note]})
                    print("Change INFO successfuly!")
                    Write_credentials.Write(credentials)
                    break


if __name__ == "__main__":
    main()
