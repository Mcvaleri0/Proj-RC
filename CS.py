import socket
import select
import sys
import os
import time


# ----------------------------- Overall Functions -----------------------------
#  -  Text and Input
def parseText(i):
    i = i.rstrip()
    return i.split(" ")


#  -  Verification
def isNumber(s):
    try:
        int(s)
        return True
    except:
        return False


# - 
def receiveMessage(bfS, mode):
    msg = ''

    if mode == 0:           #TCP
        cmd = connection.recv(3)
        if cmd == 'BCK': bfS = 1200
        else: bfS = 32

        msg = connection.recv(bfS)
        msg = cmd + msg
        #while(temp):
        #    temp = connection.recv(bfS)
        #    msg += temp

    elif mode == 1:         #UDP
        print("receive with UDP protocol")

    print('Recebi: ' + msg)

    return parseText(msg)


def sendMessage(msg, mode):
    if mode == 0:           #TCP
        connection.sendall(msg)
    elif mode == 1:         #UDP
        print("send with UDP protocol")


def authenticateUser():
    if (len(i_command) != 3        or
        len(i_command[1]) != 5     or
        len(i_command[2]) != 8     or
        not isNumber(i_command[1]) or
        not i_command[2].isalnum()):
        raise ValueError

    usName   = i_command[1]
    usPass   = i_command[2]
    filename = 'user_' + usName + '.txt'

    if os.path.isfile(filename):
        f = open(filename, 'r')
        passSaved = f.read()
        if passSaved == usPass:
            sendMessage('AUR OK\n', 0)
        else:
            sendMessage('AUR NOK\n', 0)
    else:
        f = open(filename, 'w')
        f.write(usPass)
        f.close()
        print('New User: ' + usName)
        sendMessage('AUR NEW\n', 0)


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

commandsTCP = { 'AUT': authenticateUser  ,
                'DLU': deleteUser        ,
                'BCK': backupUser        ,
                'RST': restoreUser       ,
                'LSD': dirlistUser       ,
                'LSF': filelistUser      ,
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

try:
    while(True):
        # we wait until a socket its ready to be read
        inputread, outputready, exceptionsready = select.select(sokkas, [], [])   # we dont have a socket for outputing and for exceptions.
                                                    # its always the same socket
        for sokka in inputread:
            if sokka == sokkaTCP:   # client requested something
                connection, clientAddr = sokkaTCP.accept()
                #pid        = os.fork()

                #if pid == 0:
                #    print('ola sou o filho')
                i_command = receiveMessage(128, 0)

                try:
                    commandsTCP[i_command[0]]()
                except:
                    sendMessage('ERR\n', 0)
                #    exit(0) # After 

            elif sokka == sokkaUDP:
                print('Ola sou o udp e nao devia de estar a falar')
except:
    print('\nShuting down server correctly')
    sokkaTCP.shutdown(socket.SHUT_RDWR)
    sokkaTCP.close()
    sokkaUDP.close()