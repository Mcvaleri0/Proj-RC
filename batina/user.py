#USER

import socket
import sys
import os

#split string (without the last \n) to list (by spaces)
def splitToList (s):

	s = s.rstrip()
	splitList = s.split(" ")
	return splitList

#test errors
def error(boolean):

	if boolean == False:
		raise ValueError

#request task to execute in a file
def requestTasks():

	if len(splitSpace)!=3:
		print('ERR - Please introduce the right instruction')
	else:
		PTC = splitSpace[1] #task
		filename = splitSpace[2] #name of the file
		filenameBytes = os.stat(filename).st_size #number of bytes of the file

		#read file
		fileToRead = open(filename, 'r')
		error(fileToRead) 
		filenameData = fileToRead.read()
		error(filenameData)
		fileToRead.close()

		#create message to send to central server
		msg='REQ '+ PTC + ' ' + str(filenameBytes) + ' '+filenameData+'\n'
		#send the message to CS
		nrBytes = 0
		nrBytesSend = len(msg)
		while nrBytes < nrBytesSend:
			nrBytesAlreadySent = sock.send(msg.encode())
			error(nrBytesAlreadySent)
			nrBytes += nrBytesAlreadySent
		
		if PTC == 'UPP' or PTC == 'LOW':
			print('\t' + str(filenameBytes) + ' Bytes to transmit')
		
		#receive data treated from central server
		nrSpaces=0
		nrBytes=0
		info=""
		while nrSpaces<3:
				info += sock.recv(1).decode()
				error(info)
				if info == 'REP EOF':
					break
				if info == 'REP ERR':
					break
				if info[-1]==" ":
					nrSpaces+=1
		infoList= splitToList(info)

		if len(infoList)>2:
			while nrBytes <= int(infoList[2]):
				info += sock.recv(10).decode()
				error(info)
				nrBytes += 10


		if infoList[0] == 'REP':
			#save data into file if task is UPP or LOW
			if infoList[1] == 'F':
				nameFileOut = filename.rstrip('.txt') + '_' + PTC + '.txt'
				fileOut = open(nameFileOut, 'w')
				error(fileOut)
				data = info[len(info)-int(infoList[2])-1:len(info)-1]
				error(fileOut.write(data))
				print('received file ' + nameFileOut + '\n\t' + str(infoList[2]) + ' Bytes')
				fileOut.close()
			#print data to screen if task is WCT or FLW
			elif infoList[1] == 'R':
				data = info[len(info)-int(infoList[2])-1:len(info)-1]
				if PTC == 'WCT':
					print ('Number of words: ' + data)
				elif PTC == 'FLW':
					print ('Longest word: ' + data)
			elif infoList[1] == 'EOF':
				print(info.rstrip() + ' - Please try again')
			
			elif infoList[1] == 'ERR':
				print(info.rstrip() + ' - Please introduce the right instruction')
			
	

#list tasks available
def listTasks():

	msg = 'LST\n'
	error(sock.send(msg.encode())) #send msg to central server

	info = sock.recv(1024).decode() #read its reply
	error(info)
	fptList=splitToList(info)

	if fptList[0]=="FPT": 
		if fptList[1] != 'EOF':
			numTasks=int(fptList[1])
			j=1
			for i in range(2,numTasks+2):
				if fptList[i]=='WCT':
					print (str(j) + "- WCT - word count")
				elif fptList[i]=='FLW':
					print (str(j) + "- FLW - find longest word")
				elif fptList[i]=='UPP':
					print (str(j) + "- UPP - convert to upper case")
				elif fptList[i]=='LOW':
					print (str(j) + "- LOW - convert to lower case")
				j += 1
		else:
			print(info.rstrip() + ' - Please try again') #in case there are no tasks available


#read arguments like central server port and central server name
sizeArgs = len(sys.argv)
CSname = socket.gethostname()
CSport = 58025

for i in range(sizeArgs):
	if sys.argv[i] == '-n':
		CSname = sys.argv[i+1]
	if sys.argv[i] == '-p':
		CSport = int(sys.argv[i+1])

if sizeArgs <= 0 and sizeArgs >= 6:
	raise ValueError

try:
	#read the input of the user: list, request, exit
	inputMsg = input("--> ")
	splitSpace = splitToList(inputMsg)
	
	while splitSpace[0] != 'exit':

		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket TCP to communicate with the central server
		error(sock) 
		try:
			error(sock.connect ((CSname, CSport))) #connect to central server
		except socket.error:
			print("Can't connect to server.")
			sock.close()
			break

		if splitSpace[0] == 'list': #list the tasks available
			listTasks()

		elif splitSpace[0] == 'request': #request a task to be executed in a file
			requestTasks()

		elif splitSpace[0] != 'list' and splitSpace[0] != 'request': #wrong instruction
			print('ERR - Please introduce the right instruction')

		inputMsg = input("--> ")
		splitSpace = splitToList(inputMsg)

		sock.close()

#terminate user gracefully	 
except:
	print("Exception found.")
