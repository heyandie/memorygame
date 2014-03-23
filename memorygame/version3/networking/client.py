##!/usr/bin/python
import socket
import traceback
import Tkinter
import tkSimpleDialog
import threading
from connect import connection

def connectToServer(clientsocket):
	host = ''#'10.40.72.114' #raw_input("Enter IP Address: ")
	port = 1111 #int(raw_input("Enter port number: "))
	clientsocket.connect((host, port))
	link = connection(clientsocket)
	print link.getMessage()
	return link

def sender(link):
	while True:
		message = raw_input("> ")
		sent = link.sendMessage(message)
		if message == "QUIT":
			print link.getMessage()
			break

def communicate(link, clientsocket):
	while True:
		response = link.getMessage()
		print response

		if response == "Goodbye!":
			break
	
	clientsocket.close()

def main():
	try:
		clientsocket = socket.socket()
		link = connectToServer(clientsocket)
		senderThread = threading.Thread(target=sender, args=(link,))
		senderThread.start()
		communicate(link, clientsocket)

	except Exception as error:
		print "CLIENT: ERROR OCCURED! " + str(error)
		traceback.print_exc()

if __name__ == '__main__':
	main()

'''
message = raw_input("> ")
sent = link.sendMessage(message)
if message == "QUIT":
	print link.getMessage()
	break
else:
'''

