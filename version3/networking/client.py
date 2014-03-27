import socket
import traceback
import threading
from connect import connection

try: import simplejson as json
except ImportError: import json

# --- Client Configuration -----------------------------------------------------------------------------------------

def connectToServer(clientsocket):
	host = ''#'10.40.72.114' #raw_input("Enter IP Address: ")
	port = 1111 #int(raw_input("Enter port number: "))
	clientsocket.connect((host, port))
	link = connection(clientsocket)
	print link.getMessage()
	return link

# --- Communication with Server ------------------------------------------------------------------------------------

# send messages to server
def sender(link):
	while True:
		message = raw_input("> ")
		data = {'msg':message}

		# json converts data to string for sending (very important!)
		data = json.dumps(data)
		sent = link.sendMessage(data)
		if message == "QUIT":
			print link.getMessage()
			break

# receive messages from server; end connection if response is "Goodbye!"
def communicate(link, clientsocket):
	while True:
		response = link.getMessage()
		print response

		if response == "Goodbye!":
			break
	
	clientsocket.close()

# --- Main ---------------------------------------------------------------------------------------------------------

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