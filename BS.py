import socket
import select
import sys
import os
import time


# ----------------------------- Overall Functions -----------------------------
#  -  Text
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


#  -  Messages Exchange
def receiveMessage():
    global addrCS

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
        msg, addrCS = sokkaUDP.recvfrom(1024)

    print('Recebi por ' + mode + ': ' + msg)

    return parseText(msg)


def sendMessage(msg):
    if mode == 0:           #TCP
        connection.sendall(msg)
    elif mode == 1:         #UDP
        sokkaUDP.sendto(msg, addrCS)    # Its only possible to send a message
                                        # after receiving one, meanig that
                                        # addrBS != None

    print('Enviei por ' + mode + ': ' + msg)


#  -  Auxiliary
# -----------------------------------------------------------------------------


# ----------------------------- Command Functions -----------------------------
#  -  Interaction with User -> mode: 0
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
    msg      = 'User ' + usName + ': '


    if os.path.isfile(filename):
        f = open(filename, 'r')
        passSaved = f.read()
        if passSaved == usPass:
            print(msg + 'Access Permited')
            sendMessage('AUR OK\n')
        else:
            print(msg + 'Access Denied')
            sendMessage('AUR NOK\n')
    else:
        f = open(filename, 'w')
        f.write(usPass)
        f.close()
        print(msg + 'Created')
        sendMessage('AUR NEW\n')


def uploadUser():
    pass
    

def checkoutUser():
    pass
    


#  -  Interaction with CS -> mode: 1
def registerBS():
    msg = 'REG ' + str(socket.gethostbyname(bsName)) + ' ' + str(bsPort)
    sendMessage(msg)
    print('Trying to regist')
    
    msg = receiveMessage()
    if msg[1] == 'OK':
        print('Registration permited')
        return
    elif msg[1] == 'NOK':
        print('Registration Denied\nTrying again...')
        registerBS()
    elif msg[1] == 'ERR':   # this is not supose to happen
        print('Protocol message has a sintax error')


def filelist():
    pass

def registerNewUser():
    pass

def deleteDir():
    pass

# -----------------------------------------------------------------------------


# --------------------------------- main --------------------------------------
argc   = len(sys.argv)
bsName = socket.gethostname()
bsPort = 59000
csName = socket.gethostname()
csPort = 58049

commandsTCP = { 'AUT': authenticateUser,
                'UPL': uploadUser      ,
                'RSB': checkoutUser    }

commandsUDP = { 'REG': registerBS     ,
                'LSF': filelist       ,
                'LSU': registerNewUser,
                'DLB': deleteDir      }

commands = [commandsTCP, commandsUDP]


if (argc != 1 and argc != 3 and argc != 5 and argc != 7):
    print("Incorrect number of arguments. Ex: python BS.py [-b BSport] [-n CSname] [-p CSport]")
    exit(-1)

for i in range(argc):
    if sys.argv[i] == '-b':
        bsPort = int(sys.argv[i+1])
    elif sys.argv[i] == '-n':
        csName = sys.argv[i+1]
    elif sys.argv[i] == '-p':
        csPort = int(sys.argv[i+1])

print('BSname: ' + bsName + '\nBSport: ' + str(bsPort) + '\nConnected to:')
print('\tCSname: ' + csName + '\n\tCSport: ' + str(csPort))


sokkaTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sokkaTCP.bind((bsName, bsPort))
sokkaTCP.listen(5)

sokkaUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sokkaUDP.bind((bsName, bsPort))

sokkas = [sokkaTCP, sokkaUDP]

addrCS = (socket.gethostbyname(csName), csPort)

try:
    mode = 1
    registerBS()

    while(True):
        # we wait until a socket its ready to be read
        inputread, outputready, exceptionsready = select.select(sokkas, [], [])

        for sokka in inputread:
            if sokka == sokkaTCP:   # Client requested something
                mode = 0
                connection, clientAddr = sokkaTCP.accept()

            elif sokka == sokkaUDP: # CS requested something
                mode = 1

            #pid = os.fork()
            #if pid == 0:

            i_command = receiveMessage()
            try:
                commands[mode][i_command[0]]()
            except:
                sendMessage('ERR\n')
            #    exit(0) # After child process request
                
except:
    print('\nShuting down server correctly...')
    sokkaTCP.shutdown(socket.SHUT_RDWR)
    sokkaTCP.close()
    sokkaUDP.close()