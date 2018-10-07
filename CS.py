import socket
import select
import sys
import os
import time


def parseText(i):
    i = i.rstrip()
    return i.split(" ")


def receiveMessage(bfS, mode):
    msg = ''

    if mode == 0:           #TCP
        temp = sokkas[0].recv(bfSize)
        msg += temp
        while(temp):
            temp = sokkas[0].recv(bfSize)
            msg += temp

    elif mode == 1:         #UDP
        print("receive with UDP protocol")

    return parseText(msg)


def sendMessage(msg, mode):
    if mode == 0:           #TCP
        sokkas[0].sendall(msg)
    elif mode == 1:         #UDP
        print("send with UDP protocol")


def registerUser():
    pass
    

def deleteUser():
    pass
    

def backupUser():
    pass
    

def restoreUser():
    pass


def dirlistUser():
    pass


def filelistUser():
    pass


def dirDeleteUser():
    pass


def registerBS():
    pass


def deleteBS():
    pass


def cmDebug():
    pass


def cmDebug():
    global debbug
    debbug = not debbug


argc   = len(sys.argv)
csName = socket.gethostname()
csPort = 58049

print(csName)

commandsTCP = { 'AUT': registerUser  ,
                'DLU': deleteUser    ,
                'BCK': backupUser    ,
                'RST': restoreUser   ,
                'LSD': dirlistUser   ,
                'LSF': filelistUser  ,
                'DEL': dirDeleteUser }

commandsUDP = { 'REG': registerBS,
                'UNR': deleteBS  }


if (argc != 1 and argc != 3):
    print("Incorrect number of arguments. Ex: python CS.py [-p CSport]")
    exit(-1)

if argc == 3:
    if sys.argv[1] == '-p':
        csPort = int(sys.argv[3])
    else:
        print('Wrong request format. Ex: python CS.py [-p CSport]')
        exit(-1)

sokkaTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sokkaTCP.bind((csName,csPort))
sokkaTCP.listen(5)

sokkaUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sokkaUDP.bind((csName, csPort))

sokkas = [sokkaTCP, sokkaUDP]

while(True):
    # we wait until a socket its ready to be read
    inputread = select.select(sokkas, [], [])   # we dont have a socket for outputing and for exceptions.
                                                # its always the same socket
    for sokka in inputread:
        if sokka == sokkaTCP:   # client requested something
            ClientAddr = sokkaTCP.accept()
            pid = os.fork()
            if pid == 0:
                print('ola sou o filho')
                msg = receiveMessage(128, 0)
                try:
                    commandsTCP[msg[0]]()
                except KeyError:
                    sendMessage('ERR', 0)
                exit(0) # After 
        
        elif sokka == sokkaUDP:
            print('Ola sou o udp e nao devia de estar a falar')
