#CENTRAL SERVER

import socket
import select
import sys
import os
import time

#split string (without the last \n) to list (by spaces)
def splitToList (s):

	s = s.rstrip()
	splitList = s.split(" ")
	return splitList

#test errors
def error(boolean):

	if boolean == False:
		raise ValueError

def unregisterWS(msgListUDP, end): #receive unregister form WS

	#create message to send to the WS answering the unregister request
	sizeList = len(msgListUDP)
	WSport = msgListUDP [sizeList-1]
	IP = msgListUDP [sizeList-2]
	msgNOK = "UAK NOK\n"
	msgOK = "UAK OK\n"
	#if everything is right with this request remove from the file processing tasks the WS that wants to unregister (ip, port and tasks)
	if WSport.isdigit() and (IP.replace('.', "")).isdigit() and '.' in IP:
		removeLines(IP, WSport)
		print("-" + msgUDP [4:], end="")
		error(sockUDP.sendto(msgOK.encode(), end)) 
	else:
		error(sockUDP.sendto(msgNOK.encode(), end))

def removeLines(IP, WSport): #remove from the file processing tasks the WS that wants to unregister (ip, port and tasks)

	idx=0
	i=0
	while i < len(fileProcessingTasks):
		if fileProcessingTasks[i+1] == IP and fileProcessingTasks[i+2] == WSport:
			idx=i
			del fileProcessingTasks[i+2]
			del fileProcessingTasks[i+1]
			del fileProcessingTasks[i]
			i=idx
		else:
			i+=3

def concatenateFiles(files, fileOutput):
	#open fragment files read from them (if available) and write their data in the output file
	openFileOutput = open(fileOutput, 'w')
	error(openFileOutput) 
	for name in files:
		if os.path.exists(name)==False:
			openFileOutput.close()
			return False
		openFileInput = open(name, 'r')
		error(openFileOutput)
		reading = openFileInput.read()
		error(reading)
		if reading=="":
			openFileOutput.close()
			openFileInput.close()
			return False
		error(openFileOutput.write(reading)) 
		openFileInput.close()
	openFileOutput.close()
	return True


def findLongestWord(files, fileOutput):
	#open fragment files and read from them (if available) 
	x=[]
	i=1
	for name in files:
		if os.path.exists(name)==False:
			return False
		openFileInput = open(name, 'r')
		error(openFileInput) 
		word=openFileInput.read()
		error(word)
		if word=="":
			openFileInput.close()
			return False
		x.append(word) #write the words found in a vector
		openFileInput.close()
	longest = x[0]
	length = len(x)
	for i in range(length):
		if len(longest) <= len(x[i]): #keep comparing until the end to find the longest word
			longest = x[i]
	openFileOutput = open(fileOutput, 'w')
	error(openFileOutput)
	error(openFileOutput.write(longest)) #write longest word in output file
	openFileOutput.close()
	return True

def sumWordCountFiles(files, fileOutput):
	#open fragment files and read from them (if available) 
	sumWords=0
	for name in files:
		if os.path.exists(name)==False:
			return False
		openFileInput = open(name, 'r')
		error(openFileInput)	
		reading=openFileInput.read()
		error(reading)
		if reading=="":
			openFileInput.close()
			return False
		number=int(reading)

		sumWords+=number #sum numbers read in fragment files
		openFileInput.close()
	openFileOutput = open(fileOutput, 'w')
	error(openFileOutput) 
	error(openFileOutput.write(str(sumWords))) #write sum in the output file
	openFileOutput.close()
	return True

def joinFragments(nameFile,numWSTask, taskRequested):

	idx=1
	vecFragments=[]
	nameDirOut = "output_files"
	os.makedirs(nameDirOut, exist_ok = True)
	output = nameDirOut+"/"+str(nameFile)+'.txt'

	#write names of the file fragments that were the result of a request command in a list called vecFragments
	while idx<=numWSTask:
		vecFragments.append(nameDirOut +'/'+str(nameFile)+str(idx).zfill(3)+'.txt')
		idx+=1

	result=False #flag to see if the file fragments already exist or have data
	while result==False: #while flag is not true try to execute the task requested
		if taskRequested == 'WCT':
			result=sumWordCountFiles(vecFragments, output)
			modeFile="R"
		elif taskRequested == 'FLW':
			result=findLongestWord(vecFragments, output)
			modeFile="R"
		if taskRequested == 'UPP' or taskRequested == 'LOW' :
			result=concatenateFiles(vecFragments, output)
			modeFile="F"

	#when the file with the data treated is complete read and send the data to the user
	openFileToUser = open(output, 'r')
	error(openFileToUser) 
	readFileToUser=openFileToUser.read()
	error(readFileToUser)
	filenameBytes = os.stat(output).st_size
	openFileToUser.close()

	#create message for user
	msgForUser = "REP "+ modeFile + " " + str(filenameBytes) + " "+ readFileToUser + "\n"
	nrBytes = 0
	nrBytesSend = len(msgForUser)
	#send message for user
	while nrBytes < nrBytesSend:
		nrBytesAlreadySent = connection.send(msgForUser.encode())
		error(nrBytesAlreadySent)
		nrBytes += nrBytesAlreadySent
	

def saveTasks(msgListUDP, end): #receive register from WS 

	i=1
	msgAnswer = "RAK OK\n"
	global fileProcessingTasks
	sizeList = len(msgListUDP)
	WSport = msgListUDP [sizeList-1]
	IP = msgListUDP [sizeList-2]
	while i< sizeList-2:
		#if tasks are correct save tasks IP and port of the WS in the file processing tasks list
		if msgListUDP[i] == 'WCT' or msgListUDP[i] == 'FLW' or msgListUDP[i] == 'UPP' or msgListUDP[i] == 'LOW': 
			fileProcessingTasks.append (msgListUDP[i])
			fileProcessingTasks.append (IP)
			fileProcessingTasks.append (WSport)
			i+=1
		else:
			msgAnswer = "RAK NOK\n"
			break	      
	
	#send answer to the WS by UDP
	error(sockUDP.sendto(msgAnswer.encode(), end))	
	
	print("+" + msgUDP [4:], end="")

def sendListTasks(): #send tasks available to the user

	tasks=[] #save tasks available here
	count = 0 #count the number of available tasks
	i=0
	msgListTasks = "FPT "
	if fileProcessingTasks == []:
		msgListTasks += "EOF"
	else:
		print("List Request:")
		#iterate the file processing tasks list and save the tasks available in tasks list
		while i<len(fileProcessingTasks):
			if (fileProcessingTasks[i]=='WCT' or fileProcessingTasks[i]=='FLW' or fileProcessingTasks[i]=='UPP' or fileProcessingTasks[i]=='LOW') and fileProcessingTasks[i] not in tasks:
				tasks.append(fileProcessingTasks[i])
				count+=1
			print(fileProcessingTasks[i] + " " + fileProcessingTasks[i+1] + " "+ fileProcessingTasks[i+2])
			i+=3
			

		msgListTasks += str(count)
		for i in tasks:
			msgListTasks+= ' ' + str(i)

	msgListTasks+= '\n'
	nrBytes = 0
	nrBytesSend = len(msgListTasks)
	#send tasks and number of tasks to the user
	error(connection.send(msgListTasks.encode()))


def sendToWS():

	taskRequested = msgListTCP[1] #task requested to execute
	filenameBytes = int(msgListTCP[2]) #number of bytes of data received
	dataReceived = msgTCP[len(msgTCP)-filenameBytes-1:len(msgTCP)-1] #data received
	dataReceivedList = dataReceived.split('\n') #split data received by lines
	numLines = len(dataReceivedList) #number of lines in data received

	#write data received in a folder callep input_files with a specific name: 0's+idxFile+.txt
	nameFile = str(idxFile).zfill(5)
	nameDir = "input_files"
	os.makedirs(nameDir, exist_ok = True)
	fileInput = open(nameDir+"/"+str(nameFile)+ '.txt', 'w')
	error(fileInput) 
	error(fileInput.write(dataReceived))

	IpPortList = [] #list to save IP's and ports of the working servers that execute the task requested
	numWSTask=0 #number of working servers executing the task requested
	for i in range(len(fileProcessingTasks)):
		if fileProcessingTasks[i] == taskRequested:
			numWSTask+=1
			IpPortList.append(fileProcessingTasks[i+1])
			IpPortList.append(fileProcessingTasks[i+2])
		i+=3

	numLinesPerWS = numLines//numWSTask #number of lines to send to each WS that executes the task
	rest = numLines%numWSTask #if there is rest, it means the number of lines to send to each WS will not be the same for all

	idxIpPortList=0 #iterate IpPortList with this idx
	idxWS=0 
	idxNumLinesSend=0 #number of lines sent to the WS 
	fragmentIdx=0 #number of the fragment of the file sent to the WS

	while idxWS < numWSTask: 
		
		WSip=IpPortList[idxIpPortList]
		WSport=IpPortList[idxIpPortList+1]
		fragmentIdx +=1 
		idxIpPortList+=2

		#create folder and file to write a fragment of the data treated
		nameDirOut = "output_files"
		os.makedirs(nameDirOut, exist_ok = True)
		fileOutput = open(nameDirOut+"/"+str(nameFile)+str(fragmentIdx).zfill(3)+ '.txt', 'w')
		error(fileOutput)

		pid=os.fork() #for every WS executing the requested task we create a child process that sends the data and receives it treated
		if pid==0:
			strToSend=""
			idxDataReceivedList=idxNumLinesSend
			countLines=0

			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			error(sock) 
			error(sock.connect ((socket.gethostbyaddr(WSip)[0], int(WSport))))

			#save the lines in strToSend for each WS to treat
			while countLines<numLinesPerWS: 
				if idxDataReceivedList<numLines-1:
					strToSend+=dataReceivedList[idxDataReceivedList]+'\n'
				elif idxDataReceivedList==numLines-1: #last line doesn't need to have a newline
					strToSend+=dataReceivedList[idxDataReceivedList]
				countLines+=1
				idxDataReceivedList+=1

			#if the ws is the last one and the rest is differente from zero we have to send the rest of the lines that were not send to the ws
			if rest != 0 and fragmentIdx == numWSTask: 
				g=0
				while g<rest: 
					if idxDataReceivedList+g<numLines-1:
						strToSend+=dataReceivedList[idxDataReceivedList+g]+'\n'
					elif idxDataReceivedList+g==numLines-1 : #last line doesn't need to have a newline
						strToSend+=dataReceivedList[idxDataReceivedList+g]
					g+=1
			
			#create message to send to WS 
			msgForWS = "WRQ "+taskRequested +" "+str(nameFile)+str(fragmentIdx).zfill(3)+'.txt'+" "+ str(len(strToSend.encode("UTF-8"))) +" "+ strToSend + '\n'
			#send message to WS
			nrBytes = 0
			nrBytesSend = len(msgForWS)
			while nrBytes < nrBytesSend:
				nrBytesAlreadySent = sock.send(msgForWS.encode())
				error(nrBytesAlreadySent)
				nrBytes += nrBytesAlreadySent
			
			#receive data treated from WS
			nrSpaces=0
			nrBytes=0
			dataTreated=""
			while nrSpaces<3:
				dataTreated += sock.recv(1).decode()
				error(dataTreated)
				if dataTreated[-1]==" ":
					nrSpaces+=1
			dataTreatedList= splitToList(dataTreated)

			while nrBytes <= int(dataTreatedList[2]):
				dataTreated += sock.recv(10).decode()
				error(dataTreated)
				nrBytes += 10	

			#if the message received is the right one, save the text already treated in the file created before (fragment)
			if dataTreatedList[0]=='REP' and (dataTreatedList[1]=='R' or dataTreatedList[1]=='F'):
				numBytesDataTreated=dataTreatedList[2]
				text = dataTreated[len(dataTreated)-int(numBytesDataTreated)-1:len(dataTreated)-1]
				error(fileOutput.write(text))
				fileOutput.close()
			elif dataTreatedList[0]=='REP' and dataTreatedList[1]=='EOF':
				print(dataTreated.rstrip())
				fileOutput.close()
			elif dataTreatedList[0] == 'ERR':
				print(dataTreated.rstrip())
				fileOutput.close()
			sock.close()
			os._exit(0)

		elif pid<0:
			raise ValueError

		idxWS+=1
		idxNumLinesSend+=numLinesPerWS #for each ws we send a constant number of lines (except the last one if the rest!=0)

	joinFragments(nameFile,numWSTask, taskRequested) #join all the fragments received by the WS

#read arguments like central server port
sizeArgs = len(sys.argv)
CSport = 58025
CSname = socket.gethostname()
idxFile=0 #number of text file that will save the result of the executed task
fileProcessingTasks=[] #list with information about the file processing tasks (Task, IP, Port)

if sizeArgs == 3:
	if sys.argv[1] == '-p':
		CSport = int(sys.argv[2])
	else:
		raise ValueError

elif sizeArgs <= 0 and sizeArgs >= 4:
	raise ValueError


sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #socket UDP for the central server to communicate with the working server
sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket TCP for the central server to communicate with the user
error(sockUDP)
error(sockTCP)
error(sockUDP.bind ((CSname, CSport))) #bind - gethostname for socket to be visible to the outside world
error(sockTCP.bind ((CSname, CSport))) 
error(sockTCP.listen(5)) #listen for incoming connetz

inputs = [sockUDP, sockTCP] #sockets from which we expect to read

try:
	while True:
		#wait for at least one of the socketss to be available for processing
		inputready, outputready,exceptready = select.select(inputs, [],[])

		for i in inputready:

			#socket UDP CS-WS is readable
			if i == sockUDP:

				msg, end = sockUDP.recvfrom(1024)
				error(msg) 
				error(end)
				msgUDP = msg.decode()
				msgListUDP = splitToList(msgUDP)

				if not msgUDP: 
					break

				elif msgListUDP[0] == 'REG': #Register working server
					saveTasks(msgListUDP,end)

				elif msgListUDP[0] == 'UNR': #Unregister working server
					unregisterWS(msgListUDP,end)

				else:
					error(sockUDP.sendto('ERR\n'.encode(), end))
		
			#socket TCP user-CS is readable
			elif i == sockTCP:

				connection, addr = sockTCP.accept() 
				msgTCP = connection.recv(4).decode()
				error(msgTCP)
				msgListTCP = splitToList(msgTCP)

				nrSpaces=1
				nrBytes=0

				if not msgTCP: 
					break

				elif msgListTCP[0]=='LST': #user wants list of tasks available
					sendListTasks()

				elif msgListTCP[0]=='REQ': #user wants to execute a certain task on data
					while nrSpaces<3:
						msgTCP += connection.recv(1).decode()
						error(msgTCP)
						if msgTCP[-1]==" ":
							nrSpaces+=1	
					msgListTCP = splitToList(msgTCP)

					while nrBytes <= int(msgListTCP[2]):
						msgTCP += connection.recv(10).decode()
						error(msgTCP)
						nrBytes += 10

					if msgListTCP[1] == 'WCT' or msgListTCP[1] == 'FLW' or msgListTCP[1] == 'UPP' or msgListTCP[1] == 'LOW'  :
						idxFile+=1 #increase number of text file that will save the result of the executed task
						pid=os.fork() #let child process treat the request command
						if pid==0:
							sendToWS()
							os._exit(0)
					else:
						msgListTasks='REP EOF'
						error(connection.send(msgListTasks.encode()))

				else:
					msgListTasks='ERR'
					error(connection.send(msgListTasks.encode()))
				
				connection.close() 
					

	sockTCP.close()	
	sockUDP.close()

except:
	print("\nCentral Server says bye-bye")
	sockTCP.shutdown(socket.SHUT_RDWR) #block both sending and receiving

	sockTCP.close()	
	sockUDP.close()