"""

This is the server part of the game, with code extracted from memorygame.py and networking/server.py.

Only game logic is retained from the code.
Anything that has to do with the frontend of the game should be in the client file.
(Feel free to edit if there's missing code or extra code.)

Notes:
	- use global keyword to access global variables outside classes
	- edit run() method of Player class (notes below)
	- additional notes can also be found in client.py

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
clientlist = []

# for checking if both players are connected
player1_connected = False
player2_connected = False
connected_wait = False

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
	global clientlist

	remote_socket, addr = serversocket.accept()
	link = connection(remote_socket)
	clientlist.append(link)
	print str(addr), " connected!"
	link.sendMessage("Thank you for connecting.\n")

	return (link, addr)

# --- Threading ----------------------------------------------------------------------------------------------------

"""

NOTES ON PLAYER CLASS
	Each instantiation of the Player class is a thread.
	Add additional parameters if there's a need for them.

	METHODS

	send(data)
		- accepts data (use dictionary) as parameters
		- encodes data to string and sends to own client

	send_other(data)
		- accepts data (use dictionary) as parameters
		- encodes data to string and sends to other client

	send_all(data)
		- accepts data (use dictionary) as parameters
		- encodes data to string and sends to both clients

	receive()
		- receives message from client and returns decoded message

	run()
		- what the thread does
		- game logic and all computations of the server should be implemented here
		- to end thread, use return
		- otherwise, keep everything inside the while True loop.
		- code in update() function of memorygame.py should be integrated here

	BASIC RUNDOWN:
		1. Wait until client sends message
		3. Check game_state
		4. Do necessary setup and computations depending on what state the game is in
		5. Send messages to both clients: (always check which player you are sending the data to)
			- what game_state they should be on
			- necessary variables for setup
		 
	ADDITIONAL NOTES:
		- starting game_state of the server is SharedVar.state['WAIT']
		- change game_state once both clients have connected
		- more notes about communication between server and client in the update()
		  function of client.py.
		- steps for communication is much more detailed in client.py
		  (these are, again suggestions only)

	GAME STATES: (descriptions also in resources.py)
		WAIT (server: wait for clients to connect; client: wait for other player's turn to finish)
		START (for clients only?)
		SETUP (initial setup of game)
		TRANSITION (set client's game_state to this to setup game for next turn)
		PLAY (client's turn to play; other client should have WAIT game state)
		END (game over; scoring)

	REQUIRED DATA
		For consistency, I think we should set what data is required and what they should hold.
		data['game_state'] = current game_state the client is in
		data['state'] = state of communication (analogous to 404 or 200 in HTTP)
		data['msg'] = whatever you want (can be description or something)

		Communication states:
			"OKAY" = server received the data
			"QUIT" = server will disconnect
			...
			(you can add more)

"""

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

    def send_all(self, message):
    	global clientlist
    	message = json.dumps(message)
    	for link in clientlist:
    		link.sendMessage(message)

    def send_other(self, message):
    	global clientlist
    	message = json.dumps(message)

    	if self.name == "player1":
    		link = clientlist[1]
    	elif self.name == "player2":
    		link = clientlist[0]

		link.sendMessage(message)

    def receive(self):
		message = self.link.getMessage()
		return json.loads(message)

    def run(self):
    	global player1_connected
    	global player2_connected
    	connected_wait = False

    	while True:
    		data = self.receive()
	    	state = data['state']
	    	game_state = data['game_state']
	    	print self.name, state

	    	if state == "CONNECT":
	    		if self.name == "player1":
		    		player1_connected = True
	    		elif self.name == "player2":
		    		player2_connected = True

		    	if player1_connected and player2_connected:
		    		self.send_all({'state':"OKAY",
		    				'game_state':SharedVar.state['START'],
		    				'msg': "Start game!"})

		    	elif not connected_wait:
		    		connected_wait = True
		    		self.send({'state':"OKAY",
		    				'game_state':SharedVar.state['WAIT'],
		    				'msg': "Waiting for other player to connect..."})

	    	elif state == "QUIT":
	    		self.send({'state':"OKAY",
	    				'game_state':"END",
	    				'msg': "Goodbye!"})

	    		# self.send_other({'state':"OTHER",
	    		# 		'game_state':"WAIT",
	    		# 		'msg': "The other player disconnected. Please wait for another player to join in..."})

	    		print "Ending connection..."
	    		self.link.socket.close()
	    		self.serversocket.close()
	    		return

	    	else:
	    		self.send({'state':"OKAY",
	    				'game_state':"END",
	    				'msg': "Received state: " + state})

# --- Main ---------------------------------------------------------------------------------------------------------

def main():
	global player1
	global player2
	global serversocket
	global clientlist

	try:
		serversocket = socketSetup()

		while True:

			# first client to connect will be the player1 thread
			if player1 == None:
				link, addr = connectToClient()
				player1 = Player(threadID=1, name="player1", link=link, addr=addr, server=serversocket)
				player1.start()

			# second client to connect will be the player2 thread
			elif player2 == None:
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