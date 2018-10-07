import socket
import sys
import os
import time



debbug = False



# ----------------------------- Overall Functions -----------------------------
#  -  Text and Input
def parseText(i):
    i = i.rstrip()
    return i.split(" ")


def parse_and_createFiles(f, folderName):
    fileinfo = f.split(" ", 2)  # removing the first 2 parameters
    n        = int(fileinfo[1]) # number of files
    fileinfo = fileinfo[2:]     # files data
    filenames = []

    for i in range(n):
        fileinfo  = fileinfo[0].split(' ', 4)   # files info
        filename  = fileinfo[0]                 # file name
        filenames.append(filename)              # add file name to list of file names
        data_size = int(fileinfo[3])            # file size
        data      = fileinfo[4][:data_size]     # file data
        
        f = open("./" + folderName + "/" + filename, 'w') # saving the file
        f.write(data)
        f.close()

        fileinfo[0] = fileinfo[4][data_size+1:] # Passing to the next file
    
    return filenames 


def getInput():
    global i_command

    i_command = raw_input('> ')
    i_command = parseText(i_command)


def isNumber(s):
    try:
        int(s)
        return True
    except:
        return False


def recvMsg(bfS):
    msg = sokka.recv(bfS)
    return parseText(msg)


def recvAll(bfSize):
    msg = ''
    temp = sokka.recv(bfSize)
    msg += temp

    while(temp):
        temp = sokka.recv(bfSize)
        msg += temp
    return parseText(msg)


#  -  Verification
def loggedin():
    if(not logged):
        print("A user is already logged in")
        return False
    else:
        return True


def properArgumentCount(count, example):
    if(len(i_command) - 1 == count):
        return True
    else:
        print("Invalid command. Ex: " + example)
        return False


#  -  Connection
def sendAut():
    return contactServer(autMsg, 8, 0)


def verifyAut():
    ans = sendAut()

    if ans[1] != 'OK':
        print('Autorizacao negada')
        return False
    return True


def connectToServer(ip, port):
    global sokka

    try:
        sokka = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sokka.connect((ip, port))

    except socket.error:
        print("Err - Connection lost please try again later")
        sokka.close()
        exit(-1)


def switchConnection(n_ip, n_port):
    global sokka

    c_info = sokka.getsockname()

    try:
        sokka.close()
        connectToServer(n_ip,n_port)
        return True

    except:
        print('Could not connect to server. Reconnecting with previous. Please try again later')
        connectToServer(c_info[0],c_info[1])
        return False


def contactServer(msg, bfS, mode):
    if debbug: print(msg)

    sokka.sendall(msg)
    if mode == 0:
        a = recvMsg(bfS)
        if debbug: print(a)
        return a
    elif mode == 1:
        a = recvAll(bfS)
        if debbug: print(a)
        return a

#  -  Auxiliary
def uploadToBS(folderName, nFiles, infoFiles):
    if verifyAut():
        msg = 'UPL ' + folderName + ' ' + nFiles

        for i in range(0, len(infoFiles), 4):
            f = open(folderName + '/' + infoFiles[i], 'r')
            data = f.read()
            f.close()

            msg += ' ' + infoFiles[i]     #Filename
            msg += ' ' + infoFiles[i+1]   #Date
            msg += ' ' + infoFiles[i+2]   #Time
            msg += ' ' + infoFiles[i+3]   #Size
            msg += ' ' + data             #Data

        msg += "\n"

        msg = contactServer(msg, 8, 0)

        if msg[1] == 'OK': return True
        else:              return False


def downloadFromBs(folderName):
    if verifyAut():
        msg = 'RSB ' + folderName + '\n'

        sokka.sendall(msg)
        msg = ''
        temp = sokka.recv(256)
        msg += temp

        while(temp):
            temp = sokka.recv(256)
            msg += temp

        # Err check
        if   msg[1] == 'EOF':
            print('Request cannot be answered') # No BS available
            return False
        elif msg[1] == 'ERR':
            print('Bad request') # this is not suposed to happen
            return False

        if not os.path.isdir(folderName):
            os.makedirs("./" + folderName)

        return parse_and_createFiles(msg, folderName)

# -----------------------------------------------------------------------------


# ----------------------------- Command Functions -----------------------------
def cmLogin():
    global autMsg
    global logged

    if not logged:
        if not properArgumentCount(2, "login 'username' 'pass'"): return

        if (not isNumber(i_command[1]) or (len(i_command[1]) != 5)):
            print("O username tem que ser 5 digitos")
            return

        if ((len(i_command[2]) != 8) or (not i_command[2].isalnum())):
            print("A passe tem de ser 8 caracteres alfanumericos")
            return

        # usName = i_command[1]
        # usPass = i_command[2]
        autMsg = 'AUT ' + i_command[1] + ' ' + i_command[2] + '\n'
        ans = sendAut()

        if ans[1] == 'NEW':
            logged = True
            print("User '" + i_command[1] + "' created")
        elif ans[1] == 'OK':
            logged = True
            print('Login successful')
        elif ans[1] == 'NOK':
            print('Invalid password')
        else:
            print('Error - Try again later')
    else:
        print('There is already a user logged in')


def cmDelUser():
    global autMsg
    global logged

    if not loggedin(): return

    if verifyAut():
        ans = contactServer('DLU\n', 8, 0)

        if ans[1] == 'OK':
            autMsg = '\n'
            logged = False
            print("Deletion successful")
        elif ans[1] == 'NOK':
            print('Deletion insuccessful - please delete all your backedup files')
        else:
            print('Error - Try again later')


def cmBackup():
    global sokka

    if not loggedin(): return
    if not properArgumentCount(1,"backup dir_name"): return

    if verifyAut():
        #Verify directory exists
        if os.path.isdir(i_command[1]) and len(i_command[1]) < 20 and ' ' not in i_command[1]:
            #Create list (files) of the names of the files in the directory
            files = [f for f in os.listdir(i_command[1]) if os.path.isfile(os.path.join(i_command[1], f))]
            N = len(files)

            #If there's an appropriate number of files
            if N != 0 and N <= 20:
                for f in files:
                    if len(f) > 20 and ' ' in f:
                        print('File names should not contain spaces and should have less than 20 characters')
                        return

                #Create the message for the server
                msg = 'BCK ' + i_command[1] + ' ' + str(N)

                #Adds the info of each file to the string with its name
                for i in range(N):
                    dt = str(time.strftime('%d.%m.%Y %H:%M:%S', time.gmtime(os.path.getmtime(os.path.join(i_command[1], files[i])))))
                    sz = str(os.path.getsize(os.path.join(i_command[1], files[i])))
                    files[i] += ' ' + dt + ' ' + sz
                    msg += ' ' + files[i]

                msg += '\n'
                msg = contactServer(msg, 80, 1)

                # Err check
                if   msg[1] == 'EOF':
                    print('Request cannot be answered') # No BS available
                    return
                elif msg[1] == 'ERR':
                    print('Bad request') # this is not suposed to happen
                    return

                # close old socket and establish new one with BS
                switchConnection(msg[1], int(msg[2]))

                # upload zone
                bsIP   = msg[1]
                bsPort = msg[2]
                N      = msg[3]
                msg    = msg[4:]

                if uploadToBS(i_command[1], N, msg): 
                    print('backup to: ' + bsIP + ' ' + bsPort)
                    m = 'completed - ' + i_command[1] + ':'
                    for i in range(0, len(msg), 4):
                        m += ' ' + msg[i]
                    print(m)
                else:
                    print('Backup unsuccessful')

                switchConnection(csName, csPort)

            else:
                print('Number of files not suported. Only 20 files suported per folder')
        else:
            print('Error - Invalid directory name.\nDirectory name should not contain spaces and should have less than 20 characters or directory does not exit')


def cmRestore():
    if not loggedin(): return
    if not properArgumentCount(1,"restore dir_name"): return

    if len(i_command[1]) >= 20 or ' ' in i_command[1]:
        print("Directory names should not contain spaces and should have less than 20 characters")
        return

    if verifyAut():
        ans = contactServer("RST " + i_command[1] + "\n", 32, 0)

        # Err check
        if   ans[1] == 'EOF':
            print('Request cannot be answered') # No BS available
            return
        elif ans[1] == 'ERR':
            print('Bad request') # this is not suposed to happen
            return

        bsIP   = ans[1]
        bsPort = ans[2]

        switchConnection(bsIP, int(bsPort))

        filenames = downloadFromBs(i_command[1])

        if filenames == False: 
            print('Restore unsuccessful')
        else:
            print('restore from: ' + bsIP + ' ' + bsPort)
            m = 'success - ' + i_command[1] + ':'
            for f in filenames:
                m += ' ' + f 
            print(m)

        switchConnection(csName, csPort)


def cmDirList():
    if not loggedin(): return

    if verifyAut():
        ans = contactServer('LSD\n', 32, 1)

        if ans[0] != 'ERR':
            N = int(ans[1])

            if N != 0:
                print('Folders saved:')
                for i in range(2, N+2):
                    print('\t- ' + ans[i])
            else:
                print('There are no directories saved or request was unsuccessful')
        else:
            print('ERR - bad request. Please try again later')


def cmFileList():
    if not loggedin(): return
    if not properArgumentCount(1, "filelist dir_name"): return

    if verifyAut():
        ans = contactServer('LSF ' + i_command[1] + '\n', 80, 1)

        if ans[1] != 'NOK':
            if ans[3] != 0:
                print('Files saved:')
                for i in range(4, len(ans), 4):
                    print('\t- ' + ans[i] + " " + ans[i+1] + " " + ans[i+2] + " " + ans[i+3])
            else:
                print('There are no files saved in this dir or request was unsuccessful')
        else:
            print('Request cannot be answered')


def cmDelete():
    if not loggedin(): return
    if not properArgumentCount(1, "delete dir_name"): return

    if verifyAut():
        ans = contactServer('DEL ' + i_command[1] + '\n', 8, 0)

        if ans[1] == 'OK':
            print("Directory successfuly deleted.")
        else:
            print("Request unsuccessful.")


def cmLogout():
    global autMsg
    global logged

    if not loggedin(): return

    autMsg = '\n'
    logged = False
    print('Logout successful')


def cmDebug():
    global debbug
    debbug = not debbug

# -----------------------------------------------------------------------------


# --------------------------------- main --------------------------------------
argc     = len(sys.argv)
csName   = socket.gethostname()
csPort   = 58049

commands = { 'login'   : cmLogin   ,
             'deluser' : cmDelUser ,
             'backup'  : cmBackup  ,
             'restore' : cmRestore ,
             'dirlist' : cmDirList ,
             'filelist': cmFileList,
             'delete'  : cmDelete  ,
             'logout'  : cmLogout  ,
             'debug'   : cmDebug   }

autMsg = '\n'
logged = False

if ((argc%2) == 0 or
    (argc != 1 and argc != 3 and argc != 5)):
    raise ValueError("Numero incorreto de argumentos. Ex: python user.py [-n CSname] [-p CSport]")

for i in range(argc):
	if sys.argv[i] == '-n':
		csName = sys.argv[i+1]
	elif sys.argv[i] == '-p':
		csPort = int(sys.argv[i+1])

getInput()

# app cycle
while (i_command[0] != 'exit'):
    # Connect to CS
    connectToServer(csName, csPort)

    # Do command
    try:
        commands[i_command[0]]()
    except KeyError:
        print('Comando invalido')

    sokka.close()   # sokka is closed because is established a new TCP session
                    # for each command given by the user

    # Attain new command
    getInput()
