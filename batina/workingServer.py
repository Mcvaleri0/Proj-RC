#WORKING SERVER

import socket
import sys
import os
import signal
import select

#split string (without the last \n) to list (by spaces)
def splitToList (s):
	s = s.rstrip()
	splitList = s.split(" ")
	return splitList

#Transforms string to upper case
def upperCase(filenameData):
	upper = filenameData.upper()
	return upper

#Transforms string to low case
def lowCase(filenameData):
	lower = filenameData.lower()
	return lower

#Finds the longest word in string
def longestWord(filenameData):
	x = filenameData.split()
	longest = x[0]
	i = 1
	length = len(x)
	for i in range(length):
		if len(longest) <= len(x[i]):
			longest = x[i]
	return longest

#Counts words in string
def wordCount(filenameData):
	num_words = 0
	for word in filenameData.split():
	    num_words += 1
	return str(num_words)

#send data treated to CS
def sendAnswer():
	numBytes=int(msgListTCP[3]) #number of bytes of the data received
	filenameInput=msgListTCP[2] #name of the file fragment
	taskRequested=msgListTCP[1]	#task requested to execute
	dataTask=msgTCP[len(msgTCP)-numBytes-1:len(msgTCP)-1] #data to execute task

	#save data received in a folder called input files with the name of the file fragment
	nameDir = "input_files"
	directory = os.makedirs(nameDir, exist_ok = True)
	fileInput = open(nameDir+"/"+str(filenameInput), 'w')
	fileInput.write(dataTask)
	fileInput.close()

	#execute the task requested and create the message to send to the central server
	#word count
	if(taskRequested=='WCT'):
		numWords=wordCount(dataTask)
		msgToServer = "REP R "+ str(len(numWords.encode("UTF-8"))) + " " + numWords +'\n'
		print('WCT: '+filenameInput)
		print ('\tNumber of words: ' + numWords)

	#find longest word
	elif (taskRequested=='FLW'):
		longWord = longestWord(dataTask)
		msgToServer = "REP R "+ str(len(longWord.encode("UTF-8"))) + " " + longWord + '\n'
		print('FLW: '+filenameInput)
		print ('\tLongest word: ' + longWord)

	#upper case
	elif (taskRequested=='UPP'):
		upperText = upperCase(dataTask)
		msgToServer = "REP F "+ str(numBytes) + " " + upperText + '\n'
		print('UPP: '+filenameInput)
		print('\t' + str(numBytes) + ' Bytes received')

	#lower case
	elif (taskRequested=='LOW'):
		lowerText = lowCase(dataTask)
		msgToServer = "REP F "+ str(numBytes) + " " + lowerText + '\n'
		print('LOW: '+filenameInput)
		print('\t' + str(numBytes) + ' Bytes received')

	else:
		msgToServer = 'REP EOF'

	#send answer message to central server with file mode, number of bytes and the data treated
	nrBytes = 0
	nrBytesSend = len(msgToServer)

	while nrBytes < nrBytesSend:
		nrBytesAlreadySent = connection.send(msgToServer.encode())
		if nrBytesAlreadySent == False:
			raise ValueError('Send message error')
		nrBytes += nrBytesAlreadySent
		
	if taskRequested == 'LOW' or taskRequested == 'UPP':
		print('\t' + filenameInput+ "("+str(numBytes) + ")" )


#Read arguments like tasks, CS name, WS port, CS port

sizeArgs = len(sys.argv)
CSname = socket.gethostname()
WSport = 59000
CSport = 58025
tasks = [] #tasks that this WS executes
flagTarefas=False #flag that indicates if the tasks written as arguments are correct
flagReg = False #flag that indicates if the WS was registed in the CS or not
i=1


while i<sizeArgs:
	if sys.argv[i] == 'WCT' or sys.argv[i] == 'FLW' or sys.argv[i] == 'UPP' or sys.argv[i] == 'LOW'  :
		tasks.append(sys.argv[i])
		flagTarefas = True
		i+=1
	
	else:		
		break

if flagTarefas==False:
	raise ValueError()

else :
	if sys.argv[i] != '-p' and sys.argv[i] != '-n' and sys.argv[i] != '-e':
		raise ValueError('Invalid syntax')

	else:
		for i in range(sizeArgs):
			if sys.argv[i] == '-p':
				WSport = int(sys.argv[i+1])
			
			if sys.argv[i] == '-n':
				CSname = sys.argv[i+1]
			
			if sys.argv[i] == '-e':
				CSport = int(sys.argv[i+1])

try:
	#create register message to send to central server
	registerMsg="REG "
	k=0
	while k<len(tasks):
		registerMsg += tasks[k]+' '
		k+=1
	registerMsg+= str(socket.gethostbyname(socket.gethostname()))+ ' ' + str(WSport) + '\n'

	sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #socket UDP to communicate with the central server
	sockUDP.sendto(registerMsg.encode(), (CSname, CSport)) #send register message to central server

	inputs=[sockUDP]
	
	while True:
		#wait 1 second for the socket UDP to be available for processing
		inputready, outputready,exceptready = select.select(inputs, [],[],1)
		if inputready==[] and outputready==[] and exceptready==[]: #time expired: socket is not readable -> send register message again
			print("Timeout Expired. Sending Register Again.")
			sockUDP.sendto(registerMsg.encode(), (CSname, CSport))
		else:
			if inputs[0]==sockUDP: #socket UDP is readable -> receive answer from CS
				info = sockUDP.recvfrom(1024)
				answerRegister = info[0].decode()
				if answerRegister == 'RAK OK\n':
					flagReg=True
					print('Registered')
					break
				elif answerRegister == 'RAK NOK\n':
					print ('Not registered')
					break
				elif answerRegister == 'RAK ERR\n':
					raise ValueError

	sockUDP.close() 


	sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket TCP to communicate with central server
	sockTCP.bind ((socket.gethostname(), WSport)) #bind - gethostname for socket to be visible to the outside world
	sockTCP.listen(5) #listen - we want it to queue up as many 5 connect requests before refusing outside connections

	while True:
      
		connection, addr = sockTCP.accept() #accept connection from central server
		
		pid = os.fork() #create child process to read and treat the data sent by the central server to the working server - parallelism
		if pid == 0:
			#read message of central server
			nrSpaces=0
			nrBytes=0
			msgTCP=""
			while nrSpaces<4:
					msgTCP += connection.recv(1).decode()
					if msgTCP[-1]==" ":
						nrSpaces+=1
			msgListTCP= splitToList(msgTCP)

			if not msgTCP: 
				break

			elif msgListTCP[0]=="WRQ": #read data and execute task in data received
				while nrBytes <= int(msgListTCP[3]):
					msgTCP += connection.recv(10).decode()
					nrBytes += 10
				sendAnswer()

			else:
				msgToServer = 'ERR'
				connection.send(msgToServer.encode())

			connection.close()
			os._exit(0)

		elif pid<0:
			raise ValueError

	sockTCP.close()	

except:
	if flagReg==True: #if WS was registed before -> unregister

		#create unregister message to send to central server
		j=0
		unRegisterMsg="UNR "
		while j<len(tasks):
			unRegisterMsg += tasks[j]+' '
			j+=1
		unRegisterMsg+= str(socket.gethostbyname(socket.gethostname()))+ ' ' + str(WSport) + '\n'

		sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #socket UDP to communicate with the central server
		try:
			sockUDP.sendto(unRegisterMsg.encode(), (CSname, CSport)) #send unregister message to central server

			inputs=[sockUDP]

			while True:
				#wait 1 second for the socket UDP to be available for processing
				inputready, outputready,exceptready = select.select(inputs, [],[],1) 
				if inputready==[] and outputready==[] and exceptready==[]: #time expired: socket is not readable -> send unregister message again
					print("Timeout Expired. Sending Unregister Again.")
					sockUDP.sendto(unRegisterMsg.encode(), (CSname, CSport))
				else:
					if inputs[0]==sockUDP: #socket UDP is readable -> receive answer from CS
						info = sockUDP.recvfrom(1024)
						answerUnRegister = info[0].decode()
						if answerUnRegister == "UAK OK\n":
							sockTCP.close()	
							print('\nUnregistered successfully!')
							break
						elif answerUnRegister == 'UAK NOK\n': #if CS sends this answer send unregister message again
							print("\nLet's try again")
							sockUDP.sendto(unRegisterMsg.encode(), (CSname, CSport))
			sockUDP.close()
		except:
			print("Can't connect to central server.")
	else:
		print("\nCouldn't register.")