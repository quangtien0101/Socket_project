import socket
import select
import sys

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if len(sys.argv) != 4:
    print "python chat_client.py IP_address port_number name"
    exit()
IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
server.connect((IP_address, Port))
name = str(sys.argv[3])
server.send(name)

while True:
    sockets_list = [sys.stdin, server]
    read_sockets,write_socket, error_socket = select.select(sockets_list, [], [])
    for socks in read_sockets:
        if socks == server:
            message = socks.recv(2048)
            print message
        else:
            #sys.stdout.write("<You>: ")
            message = sys.stdin.readline()
            server.send(message)
            print('\n')
            #sys.stdout.write(message)
            #sys.stdout.flush()
server.close()
