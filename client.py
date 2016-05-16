import sys
import os
import socket
import pickle
import logging
from threading import Thread
from getpass import getpass
import NetworkConnector


BUF_SIZE = 32768

def SendData(client_socket, to_user, file_name):
    message = "sendfile "+to_user+" "+file_name+" "
    fr = open(file_name, 'rb')
    data = fr.read(1024)
    print data
    fr.close()
    message +=data
    print message
    print "Send success!"
    client_socket.sendall(pickle.dumps(message))

def RecvData(to_user,file_name,file_data):
    # Receive file info
    fw = open(file_name, 'wb')
    fw.write(file_data)
    fw.close()    
    print "Receive "+file_name

def Account(id):
    fn = id + ".txt"
    logging.basicConfig(format = '%(asctime)s: %(message)s',
                        level = logging.INFO,
                        filename = fn, 
                        filemode = 'w')

def updateCheck(client_socket):
    message = pickle.loads(client_socket.recv(BUF_SIZE))
    if message == []:
        pass
    else:
        print(message)

def login(client_socket):
    id = raw_input("Account : ")
    pw = getpass(prompt="Password : ")
    message = id + ':' + pw
    client_socket.sendall(message)
    
    if client_socket.recv(1) :
        updateCheck(client_socket)
        return (True, id)
    else:
        return (False, None)

def talkMode(client_socket, to_user):
    loop = True
    while loop:
        message = raw_input()
        
        if message == "exit":
            break
        else:
            message = "send" + " " + to_user + " " + message
            client_socket.sendall(pickle.dumps(message))

def handle_recv(client_socket):
    while True:
        message = pickle.loads(client_socket.recv(BUF_SIZE))
	message_split = message.split(' ')
        if message == 'logout':
            sys.exit()
            os.exit()
	elif message_split[0]=="sendfile":
	    RecvData(message_split[1],message_split[2],message_split[3])
        else:    
            print(message)

def handle_send(client_socket, id):
    while True:
        message = raw_input()
        message_split = message.split(":") 

        if message_split[0] == "exit":
            sys.exit()
        elif message_split[0] == "talk" and len(message_split) == 2:
            talkMode(client_socket, message_split[1])
	elif message_split[0]=="sendfile":
	    SendData(client_socket, message_split[1], message_split[2])
        elif message_split[0] == "logout" and len(message_split) == 1:
            client_socket.sendall(pickle.dumps(message))
            sys.exit()
            os.exit()
        else:
            client_socket.sendall(pickle.dumps(message))

def main():
    client_socket = NetworkConnector.client_init("127.0.0.1", 10067)
    
    (login_success, id) = login(client_socket)
    if login_success: 
        print("Hi {}".format(id))
        Thread(target=handle_recv, args=(client_socket, )).start()
        Thread(target=handle_send, args=(client_socket, id)).start()
    else:   
        print("Wrong account or password!")

if __name__ == '__main__':
    main()