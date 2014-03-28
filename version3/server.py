"""

This is the server part of the game, with code extracted from memorygame.py and networking/server.py.

Only game logic is retained from the code.
Anything that has to do with the frontend of the game should be in the client file.
(Feel free to edit if there's missing code or extra code.)

Notes:
	- use global keyword to access global variables outside classes
	- update() function is lifted directly from memorygame and should be integrated with run() method of Person class
	- update() function should then be deleted
	- run() method will check game_state and do necessary setup/computations and send data to clients (more notes below)

"""

import time
import thread
import random
import socket
import traceback
from threading import Thread
from connect import connection
from game import resources,card
from game.resources import SharedVar

try: import simplejson as json
except ImportError: import json

# --- Global Variables ---------------------------------------------------------------------------------------------

# generate cards
# this is the array for the cards in the boards
cards_list = []

# this is the list of index for the cards on the board
# board is 20x20, a pair of cards has matching index i
# so if we have 20 cards, we have twice of 0-9 indexes
index_list = []

# initialize game_state to WAIT
game_state = SharedVar.state['WAIT']

# column position of the selector from 0-4
card_select_x = 0

# row position of the selector from 0-3
card_select_y = 0

# index of card to which the selector is currently located
card_select_pos = 0

# stores the matched indexes 
matched_index = []

# stores the flipped cards
flipped_cards = []

# stores the flipped indexes
flipped_index = []

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

# Each instantiation of the Player class is a thread.
# Add additional parameters if there's a need for them.
class Player(Thread):
    def __init__(self, threadID, name, link, addr, server):
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.link = link
        self.addr = addr
        self.serversocket = server
        self.score = 0

    def send(self, message):
    	message = json.dumps(message)
    	self.link.sendMessage(message)

    def receive(self):
		message = self.link.getMessage()
		return json.loads(message)

    def run(self):
    	while True:
    		data = self.receive()
	    	state = data['state']
	    	print self.name, state

	    	if state == "QUIT":
	    		self.send({"msg":"Goodbye!"})
	    		print "Ending connection..."
	    		self.link.socket.close()
	    		self.serversocket.close()
	    		return

	    	else:
	    		self.send({"msg":"Received state: " + state})

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
				player2 = Player(threadID=2, name="player2", link=link, addr=addr, server=serversocket)
				player2.start()

			# don't connect to other clients (will edit this part later)
			else:
				break

	# if something goes wrong...
	except Exception as error:
		print "Server: Error Occured! " + str(error)
		traceback.print_exc()

if __name__ == "__main__":
	main()