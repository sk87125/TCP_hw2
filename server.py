import sys
import socket
import pickle
import logging
from threading import Thread
import NetworkConnector
import os


BUF_SIZE = 32768
server_addr = ("127.0.0.1", 10067)
accounts = {"John": "123", "Marry": "321", "Lydia": "1234567"}
offline_message={'John':[], 'Marry':[], 'Lydia':[]}
online_user = {}


def Account(id):
    file_n = id + ".txt"
    logging.basicConfig(format = '%(asctime)s: %(message)s',
                        level = logging.INFO,
                        filename = file_n,
                        filemode = 'w')


def list_message(connection,id):
    txtname=id+".txt"
    message=""
    if not os.path.exists(txtname):
        f=open(txtname,"w")
        f.close()
	print "build txt success"
    else:
         fileIN = open(txtname,"r")
         line = fileIN.readline()
         while line:
             line=line.strip()
	     print line
             if line in online_user:
		 print "online"
                 message = message+line+" is online\n"
		 #connection.sendall(pickle.dumps(message))		 
             else:
		 print "offline"
                 message = message+line+" is offline\n"
		 #connection.sendall(pickle.dumps(message))
             line=fileIN.readline()
         connection.sendall(pickle.dumps(message))
    	 fileIN.close()


def send_message(connection, from_user, to_user, message):
    message_temp = message

    if to_user in online_user:
        message = "You say : " + message
        online_user[from_user].sendall(pickle.dumps(message))
        message = from_user + " says : " + message_temp
        online_user[to_user].sendall(pickle.dumps(message))
        logging.info(message)
    else:
        message = from_user + " says : " + message
        offline_message[to_user].append(message)


def broadcast_message(connection, from_user, message):
    message = from_user + " yelled : " + message

    for i in accounts:
        if i in online_user:
            online_user[i].sendall(pickle.dumps(message))

def updateCheck(connection, id):
    if id in offline_message:
        connection.sendall(pickle.dumps(offline_message[id]))


def loginCheck(connection):
    message = connection.recv(BUF_SIZE)
    id= message.split(':')[0]
    pw= message.split(':')[1]
    if id in accounts and accounts[id] == pw:
        print("{} login success!".format(id))
        connection.sendall("1")
	print("success~")
        online_user[id] = connection
        updateCheck(connection, id)
        return (True, id)

    else :
        print("{} login fail!".format(id))
        connection.sendall("0")
        connection.close()
    pass

def logout(connection, id):
    message = "Goodbye " + id
    connection.sendall(pickle.dumps(message))
    connection.sendall(pickle.dumps("logout"))
    online_user.pop(id)

def addfriend(id,fdname):
    txtname=id+".txt"
    f=open(txtname,"a")
    f.write(fdname+"\n")
    f.close()

def delfriend(id,fdname):
    txtname=id+".txt"
    f=open(txtname,"r")
    line = f.readline()
    fdlist = []
    while  line:
        line=line.strip()
	fdlist.append(line)
        line = f.readline()
    if fdname in fdlist:
	fdlist.remove(fdname)
	f.close()
    os.remove(txtname)
    f=open(txtname,"w")
    for i in fdlist:
        f.write(i +"\n")
    #f.write(fdname+"\n")
    f.close()

def RecvData(connection,id,to_user,file_name,file_data):
    # Receive file info
    fw = open(file_name, 'wb')
    fw.write(file_data)
    fw.close()

def SendData(to_user, file_name):
    message = "sendfile "+to_user+" "+file_name+" "
    fr = open(file_name, 'rb')
    data = fr.read(1024)
    print data
    fr.close()
    message +=data
    print message
    print "Send success!"
    online_user[to_user].sendall(pickle.dumps(message))



def handle_request(connection):
    (login_success, id) = loginCheck(connection)

    if login_success:
        while True:
            message = pickle.loads(connection.recv(BUF_SIZE))
	    print message
            #file_data = message
            message_split = message.split(' ')
	    message_len = len(message_split)
            inst = message_split[0].lower()
            if inst == "list":
		 list_message(connection,id)
            elif inst == "send" and message_len == 3:
                send_message(connection, id, message_split[1], message_split[2])
            elif inst == "talk" and message_len == 2:
                pass
            elif inst == "broadcast" and message_len == 2:
                broadcast_message(connection, id, message_split[1])
            elif inst == "logout" and message_len == 1:
                logout(connection, id)
	    elif inst == "addfriend":
		addfriend(id,message_split[1])#TOM
		list_message(connection,id)
	    elif inst == "delfriend":
		delfriend(id,message_split[1])#TOM
		list_message(connection,id)
	    elif inst == "sendfile":
		RecvData(connection,id,message_split[1],message_split[2],message_split[3])
		SendData(message_split[1],message_split[2])
            else:
                connection.sendall(pickle.dumps("error"))
                print("error")


def handle_conversation(connection, address):
    try:
        while True:
            handle_request(connection)
    except EOFError:
        print('Client socket to {} has closed'.format(address))
    except Exception as e:
        print('Client {} error: {}'.format(address, e))
    finally:
        connection.close()


def accept_connections(server_socket):
    while True:
        connection, address = server_socket.accept()
        print("Accept connection: {}".format(address))
        Thread(target=handle_conversation, args=(connection, address)).start()


def main():
    server_socket = NetworkConnector.server_init(server_addr)
    accept_connections(server_socket)


if __name__ == '__main__':
    main()

