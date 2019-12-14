#!/usr/bin/python3
import socket
import sys
import subprocess
import os
import traceback
from termios import tcflush, TCIFLUSH
from cryptography.fernet import Fernet
from getpass import getpass
import affineCipher

file = open('secret_key.key', 'rb')
KEY = file.read() # The key will be type bytes
file.close()
encryption_f = Fernet(KEY)

def main():
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "127.0.0.1"
    port = 8888
    username =""
    #subprocess.call(['gnome-terminal','-e','python3 client_chat.py'])

    try:
        connection.connect((host, port))
    except:
        print("Connection error")
        sys.exit()

    print("Enter 'quit' to exit")
   # subprocess.call(['gnome-terminal','-e','python3 client_chat.py'])
    #tcflush(sys.stdin, TCIFLUSH)
    sending_flag = True

    message = input(">> ")

    sending_flag = Allow_to_send(message)

    is_login = False
    while not is_login:
        

        if "--login" in message:
            if len(message.split()) != 3:
                print("Invalid argments")
                pass
            print("You want to login")
            print("UserName: "+message.split()[2])
            password = getpass('Password: ')
            print(password)
            request_login = message + " -p "+password
            #print(request_login)
            connection.sendall(request_login.encode("utf8"))

            response = connection.recv(2048).decode("utf8")
            if "OK" in response:
                username = response[3:]
                print("Welcome " + username)
                username = response[3:]
                is_login = True
            else:
                print(response)
                username = ""
        else:
            print("command: '--login -u username'")
                        
            
        message = input(">> ")
        sending_flag = Allow_to_send(message)




    while message != 'quit':
        if sending_flag == True:
            connection.sendall(message.encode("utf8"))
            print("Message sent to server")
            


        if "--login" in message:
            print("You want to login")
            print("UserName: "+message.split()[2])
            password = getpass('Password: ')
            print(password)
            request_login = message + " -p "+password
            print(request_login)
            connection.sendall(request_login.encode("utf8"))

            response = connection.recv(2048).decode("utf8")
            if "OK" in response:
                username = response[3:]
                print("Welcome " + username)
                username = response[3:]
            else:
                print(response)
                username = ""

        elif "--help" in message:
            print_commands()

        elif "--change_password" in message:
            change_password(username, connection)

        elif "--change_info" in message:
            change_user_info(username, connection)
        #reset the sending flag
        elif "--chat" in message:
            # "--chat Putin"
            if "--encrypt" in message:
                parsing = message.split()
                if len(parsing) !=3:
                    print('INvalid command')
                else:
                    connection.sendall(message.encode('utf8'))
                    port = connection.recv(2048).decode('utf8')
                    print("Opening chat services with encryption")
                    process = subprocess.Popen("gnome-terminal -x python chat_client.py 127.0.0.1 " +port +" "+username+" True", stdout=subprocess.PIPE,stderr=None,shell=True)

            else:
                #print(message)
                parsing = message.split()
                if len(parsing) !=2 :
                    print("Invalid commands")
                else:
                    connection.sendall(message.encode('utf8'))
                    port = connection.recv(2048).decode('utf8') 
                    print("Port#: " + port)   
                    print("Opening chat services!")
                    process = subprocess.Popen("gnome-terminal -x python chat_client.py 127.0.0.1 " +port+" "+username+" False", stdout=subprocess.PIPE,stderr=None,shell=True)

                    tcflush(sys.stdin, TCIFLUSH)

        elif "--list --room" in message:
            print("Retriving chat room:")
            response = connection.recv(4096).decode('utf8')
            if response == "Null":
                print("Thre is 0 room")
                continue

            rooms = response.split(';')
            #print(names)
            for i in rooms:
                if i == "":
                    continue
                print (i)

        elif "--join --room" in message:
            print("Enter the owner's room available")
            owner = input()
            message = "--join --room " + username + " " + owner
            connection.sendall(message.encode('utf8'))
            response = connection.recv(2048).decode('utf8')
            if "ERR" in response:
                print(response)
            elif "OK" in response:
                parse = response.split('!')
                print(parse)
                p = parse[-1]
                print("port#:"+p)
                print("Opening chat services!")
                process = subprocess.Popen("gnome-terminal -x python chat_client.py 127.0.0.1 " +p+" "+username+" False", stdout=subprocess.PIPE,stderr=None,shell=True)

                



        elif "--download" in message:

            parsing = message.split()
            items = parsing[1:]
            for i in items:
                filename = i
                Download_process(filename, connection)

        elif "--upload" in message:
            #usage: --upload --change_name file1 file2
            if "--change_name" in message:
                print("Name change!")
                parsing = message.split()
                if len(parsing) < 4:
                    print("Invalid argument numbers")
                    pass
                else:
                    Upload_process(connection)

            #upload a file with encryption
            #usage: --upload --encrypt Hello.txt
            elif "--encrypt" in message:
                if ".txt" not in message:
                    print("Can not encrypt non txt files")
                else:
                    print("encrypt message before send")
                    parsing = message.split()
                    if len(parsing) != 3:
                        print ("Invalid argument numbers")
                        pass
                    else:
                        print("Begining uploading with encryption")
                        Upload_process(connection,True)

            #normal multi-file upload
            else:
                parsing = message.split()
                items = parsing[1:]
                for i in items:
                    filename = i
                    Upload_process(connection)

                

        elif "--list --server" in message:
        	os.system("ls /home/wayne/qt/Project_socket/File_folder")
        elif "--list --local" in message:
        	os.system("ls /home/wayne/qt/Project_socket/Download")

        elif "--list --online" in message:
            print("List of online users:")
            response = connection.recv(4096).decode('utf8')
            names = response.split(',')
            #print(names)
            for i in names:
                if i == "":
                    pass
                print (i)

        elif "--list --info" in message:
            response = connection.recv(4096).decode("utf8")
            info = response.split(',')
            print("Your username: " + username)
            print("DOB: " + info[0])
            print("Your note: " + info[1])

        else:
            response = connection.recv(2048).decode("utf8")
            if response == "-":
                pass
            else:
                print(response)
            
            print("'--help' to show options")
            
        message = input(">> ")
        sending_flag = Allow_to_send(message)


    connection.send(b'--quit--')
       
def Allow_to_send(message):
    if "--chat" in message:
        return False
    elif "--list --local" in message:
    	return False
    elif "--list --server" in message:
        return False
    elif "--login" in message:
        return False
    elif "--help" in message:
        return False
    elif "--change_password" in message:
        return False
    elif "--change_info" in message:
        return False
    elif "--join --room" in message:
        return False
    else:
        return True 

def Download_process(filename, s):
    if filename != 'q':
        s.send(filename.encode('utf8'))
        data = s.recv(2048).decode('utf8')
        if data[:6] == 'EXISTS':
            filesize = int(data[6:])
            message = input("File exists, " + str(filesize) +"Bytes, download? (Y/N)? -> ")
            if message.upper() == 'Y':
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


def Upload_process(Connection, encrypt = False):

    filename = Connection.recv(2048).decode('utf8')
    print("receving " +filename)
    name = filename
    filename = "/home/wayne/qt/Project_socket/Download/" + filename
    print("the path is " + filename)

    if os.path.isfile(filename):
        if encrypt == True:
            create_encrypted_file(name)




        Connection.send(("EXISTS " + str(os.path.getsize(filename))).encode('utf8'))
        print("Uploading...")
        userResponse = Connection.recv(2048).decode('utf8')
        if userResponse[:2] == 'OK':
            f = 1 # init a dumb variable for f
            if encrypt == True:
                f = open("/home/wayne/qt/Project_socket/Download/Encrypted/" + name, 'rb')
            else:
                f = open(filename, 'rb')

            i = 0
            bytesToSend = f.read(2048)

                

            Connection.send(bytesToSend)

            print("sent!" + str(i))
            i = i + 1
            while i<10000:
                bytesToSend = f.read(2048)

                Connection.send(bytesToSend)
                print("sent" + str(i))
                i = i+1


            f.close()
    else:
        Connection.send("ERR ".encode('utf8'))
        print("The file " + name + " doesn't exist!")

    print("Finish Retriving")

def create_encrypted_file(filename):
    if ".txt" not in filename:
        print("Cannot encrypt non txt file")
        
    else:
        file_directory = "/home/wayne/qt/Project_socket/Download/Encrypted/" + filename
        f_in =  open('/home/wayne/qt/Project_socket/Download/' + filename, "r")
        f_out = open(file_directory, 'w')
        message = f_in.read()
        f_in.close()
        encrypted_message = affineCipher.execute("encrypt", message)
        f_out.write(encrypted_message)

        
        f_out.close()
        print ("Done making a new encrypted copy!")

def print_commands():
    print("'--list --local' to show files on server folder")
    print("'--list --server' to show files on local folder")
    print("'--list --info' to show users information")
    print("'--list --online' to show online users")
    print("'--download filename1 filename2 ...' to download one or multiple files from server")
    print("'--upload --change_name file_name alternative_name' to upload file to server with alternative name")
    print("'--upload --encrypt file1.txt' to upload file with txt format to server")
    print("'--upload file1 file2 file3 ...' to upload one or multiple files to server")
    print("'--change_password' to change your password")
    print("'--change_info' to change your information")
    print("'--chat' to open the chat room")

def change_password(username, connection):
    current_pass = getpass("Enter your current password: ")
    new_password = getpass("Enter your new password: ")
    confirm_password = getpass("Confirm your new password: ")

    if new_password != confirm_password:
        print("Wrong password confirmation")
    else:
        request = "--change_password -u " + username + " -p " + current_pass + " -np " + new_password
        connection.sendall(request.encode('utf8'))
        response = connection.recv(2048).decode('utf8')
        print(response)
        if "OK" in response:
            print("Change password successfully!")
        else:
            print("Current password is not correct!")

def change_user_info(username, connection):
    current_pass = getpass("Enter your current password: ")

    dob = input("Enter your new DOB: ")
    Notes = input ("Enter your new note: ")

    request = "--change_info -u " + username + " -p " + current_pass + " -dob " + dob + " -n " + Notes
    connection.sendall(request.encode('utf8'))
    response = connection.recv(2048).decode('utf8')
    if "OK" in response:
        print("Change info successfully!")
    else:
        print("Current password is not correct!")

if __name__ == "__main__":
    main()