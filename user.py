import socket
import sys
import os


# ----------------------------- Overall Functions -----------------------------
def parseInput(i):
    i = i.rstrip();
    return i.split(" ")


def isNumber(s):
    try:
        return int(s);
    except:
        return -1


def sendAut():
    sokka.sendall(autMsg)
    return sokka.recv(8)


def verifyAut(s):
    if s == aurOK:
        return True
    return False

# -----------------------------------------------------------------------------



# ----------------------------- Command Functions -----------------------------
def cmLogin():
    global autMsg

    if len(i_command) != 3:
	    print("Comando invalido. Ex: login 'username' 'pass'")
	    return

    if ((isNumber(i_command[1]) == -1) or (len(i_command[1]) != 5)):
        print("O username tem que ser 5 digitos")
        return

    if ((len(i_command[2]) != 8) or (not i_command[2].isalnum())):
        print("A passe tem de ser 8 caracteres alfanomericos")
        return

    # usName = i_command[1]
    # usPass = i_command[2]
    autMsg = 'AUT ' + i_command[1] + ' ' + i_command[2] + '\n'
    ans = sendAut()
    if ans == 'AUR NEW\n':
        print("User '" + i_command[1] + "' created")
    elif ans == aurOK:
        print('Login successful')
    elif ans == 'AUR NOK\n':
        print('Invalid password')
    else:
        print('Error - Try again later')


def cmDelUser():
    if not verifyAut(sendAut()):
        print('Autorizacao negada')
        return

    sokka.sendall('DLU\n')
    ans = sokka.recv(8)

    if ans == 'DLR OK\n':
        print("Deletion successful")
    elif ans == 'DLR NOK\n':
        print('Deletion insuccessful - please delete all your backedup files')
    else:
        print('Error - Try again later')


def cmBackup():
    pass


def cmRestore():
    pass


def cmDirList():
    pass


def cmFileList():
    pass


def cmDelete():
    pass


def cmLogout():
    pass

# -----------------------------------------------------------------------------

# ---------------------------------------- main ------------------------------
argc     = len(sys.argv)
csName   = socket.gethostname()
csPort   = 58049
commands = { 'login':    cmLogin,
             'deluser':  cmDelUser,
             'backup':   cmBackup,
             'restore':  cmRestore,
             'dirlist':  cmDirList,
             'filelist': cmFileList,
             'delete':   cmDelete,
             'logout':   cmLogout }
autMsg = ''
aurOK  = 'AUR OK\n'

if ((argc%2) == 0 or
    (argc != 1 and argc != 3 and argc != 5)):
    raise ValueError("Numero incorreto de argumentos. Ex: python user.py [-n CSname] [-p CSport]")

for i in range(argc):
	if sys.argv[i] == '-n':
		csName = sys.argv[i+1]
	elif sys.argv[i] == '-p':
		csPort = int(sys.argv[i+1])

#FIXME
i_command = raw_input('> ')
i_command = parseInput(i_command)

# app cycle
while (i_command[0] != 'exit'):

    # socket creation
    sokka = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connection with the server
    try:
        sokka.connect((csName, csPort))
    except socket.error:
        print("Erro ao conectar com o servidor")
        sokka.close()
        break

    # Do command
    try:
        commands[i_command[0]]()
    except KeyError:
        print('Comando invalido')
    
    sokka.close()   # sokka is closed because is established a new TCP session
                    # for each command given by the user

    # Attain new command
    i_command = raw_input('> ')
    i_command = parseInput(i_command)
