"""

This is the general code for the server. This server will only connect up to two clients.

The first client to connect to the server will be designated as player1.
The server will print all messages sent by the clients, along with the name of the client that sent the message.
Client names are set to "player1" and "player2".

If the client sends the message "QUIT", the server will disconnect from the client.
The server will only quit once both client connections have been disconnected.
Otherwise, the server will continue running, waiting for messages.

When integrating with the game code, the server should handle all computations and setup.
Clients will implement whatever the server sends them.

"""

import socket
import time
import random
import traceback
from threading import Thread
from connect import connection

try: import simplejson as json
except ImportError: import json

# --- Global Variables ---------------------------------------------------------------------------------------------

# player1 and player2 are clients connected to the server that will implement the Player Class
player1 = None
player2 = None
serversocket = None

# --- Server Configuration -----------------------------------------------------------------------------------------

def socketSetup():
	host = ''
	port = 1111 #int(raw_input("Enter port number: "))
	serversocket = socket.socket()

	serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	serversocket.bind((host, port))
	print "Server ready..."
	serversocket.listen(5)
	return serversocket

def connectToClient():
	global serversocket

	remote_socket, addr = serversocket.accept()
	link = connection(remote_socket)
	print str(addr), " connected!"
	link.sendMessage("Thank you for connecting.")
	return (link, addr)

# --- Threading ----------------------------------------------------------------------------------------------------

# Each instantiation of the Player class is a thread
class Player(Thread):
    def __init__(self, threadID, name, link, addr, server):
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.link = link
        self.addr = addr
        self.serversocket = server
        self.score = 0
 
 	# Game logic and all computations of the server should be implemented in the run() method.
 	# To end thread, use return. Otherwise, keep everything inside the while True loop.
    def run(self):
    	while True:
	    	message = self.link.getMessage()

	    	# json decodes string and converts back to data (very important!)
	    	data = json.loads(message)
	    	message = data['msg']
	    	print self.name, message

	    	if message == "QUIT":
	    		self.link.sendMessage("Goodbye!")
	    		print "Ending connection..."
	    		self.link.socket.close()
	    		self.serversocket.close()
	    		return

# --- Main ---------------------------------------------------------------------------------------------------------

def main():
	global player1
	global player2
	global serversocket

	try:
		serversocket = socketSetup()

		while True:

			# first client to connect will be the player1 thread
			if player1 == None:
				link, addr = connectToClient()
				player1 = Player(threadID=1, name="player1", link=link, addr=addr, server=serversocket)
				player1.start()

			# second client to connect will be the player2 thread
			if player2 == None:
				link, addr = connectToClient()
				player2 = Player(threadID=1, name="player2", link=link, addr=addr, server=serversocket)
				player2.start()

			# don't connect to other clients (will edit this part later)
			else:
				break

	# if something goes wrong...
	except Exception as error:
		print "SERVER: ERROR OCCURED! " + str(error)
		traceback.print_exc()

if __name__ == '__main__':
	main()

















