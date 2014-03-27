"""

This is the general code for the client.

The client will be able to send messages to the server in the form of a dictionary.
json is used to encode the message into a string. The server will decode the message and print it.

To disconnect, the client only needs to send the message "QUIT".

When integrating with the game code, the client should send the game_state and all necessary data to the server.
The server will handle the computations and setup. The client only needs to implement them and update the server
when the players change the game_state.

"""

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