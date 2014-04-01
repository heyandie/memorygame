"""

This is the Player class. Game logic will be processed here.

Each instantiation of the Player class is a thread (instantiated in server.py).
Add additional parameters if there's a need for them.

METHODS

	send(data)
		- accepts data (use dictionary) as parameter
		- encodes data to string and sends to own thread

	send_other(data)
		- accepts data (use dictionary) as parameter
		- encodes data to string and sends to other thread

	send_all(data)
		- accepts data (use dictionary) as parameter
		- encodes data to string and sends to both threads

	receive()
		- receives message from thread and returns decoded message

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
	For consistency, some data to be sent should be mandatory in the protocol.

	data['game_state'] = current game_state the client is in
	data['state'] = state of communication (analogous to 404 or 200 in HTTP)
	data['msg'] = whatever you want (can be description or something)

	Communication states:
		"OKAY" = server received data from own thread
		"OTHER" = server received data from own other thread
		"QUIT" = server will disconnect from client
		...
		(you can add more)

"""

import pyglet
import time
import thread
import random
# import socket
import traceback
import eventlet
from eventlet.green import socket
from threading import Thread
from connect import connection
from game import resources
from game.card import Card
from game.resources import SharedVar

try: import simplejson as json
except ImportError: import json

# Disable error checking for increased performance
pyglet.options['debug_gl'] = False

from pyglet.gl import *

# --- Global Variables ---------------------------------------------------------------------------------------------

window_width = 800
window_height = 600

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

# --- Main ---------------------------------------------------------------------------------------------------------

class Player(Thread):
    def __init__(self, threadID, name, link, addr, server):
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.link = link
        self.addr = addr
        self.serversocket = server
        self.score = 0

    # --- Communication -------------------------------

    def send(self, message):
    	message = json.dumps(message)
    	self.link.sendMessage(message)

    def send_other(self, message):
    	message = json.dumps(message)

    	if self.name == "player1":
    		link = SharedVar.clientlist[1]
    	elif self.name == "player2":
    		link = SharedVar.clientlist[0]

		link.sendMessage(message)

    def send_all(self, message):
    	message = json.dumps(message)
    	for link in SharedVar.clientlist:
    		link.sendMessage(message)

    def receive(self):
		message = self.link.getMessage()
		return json.loads(message)

	# --- Game Logic ----------------------------------

    def setup(self):
		global index_list
		global cards_list

		index_list = [i for i in range(10)] + [i for i in range(10)]
		random.shuffle(index_list)

		# generate images for the card
		i = 0
		j = 0
		k = 0

		# 4 rows
		while i<4:
			j=0

			# 5 columns
			while j<5:
				x_pos = j * 160
				y_pos = window_height - (i *150)

				# index is the kth item in the shuffled index list
				index = index_list[k]
				card_name = "card" + str(index+1)
				card_back = pyglet.sprite.Sprite(img=resources.card_back,x=x_pos,y=y_pos)
				card_front = pyglet.sprite.Sprite(img=resources.card_front[index],x=x_pos,y=y_pos)
				new_card = Card(card_back,card_front,card_name)
				cards_list.append(new_card)

				j = j + 1
				k = k + 1

			i = i + 1

		data = {'state':"OKAY",
				'game_state':SharedVar.state['START'],
				'msg': "Start game!",
				# 'cards_list':cards_list
				}

		return data

    # --- Threading -----------------------------------

    def run(self):
    	while True:
    		data = self.receive()
	    	state = data['state']
	    	game_state = data['game_state']
	    	print self.name, state

	    	if state == "CONNECT":
	    		if self.name == "player1":
		    		SharedVar.player1_connected = True
	    		elif self.name == "player2":
		    		SharedVar.player2_connected = True

		    	if SharedVar.player1_connected and SharedVar.player2_connected:
		    		data = self.setup()
		    		self.send_all(data)

		    	else:
		    		self.send({'state':"OKAY",
		    				'game_state':SharedVar.state['WAIT'],
		    				'msg': "Waiting for other player to connect..."})

	    	elif state == "QUIT":
	    		self.send({'state':"OKAY",
	    				'game_state':"END",
	    				'msg': "Goodbye!"})

	    		if self.name == "player1":
		    		SharedVar.player1_connected = False
	    		elif self.name == "player2":
		    		SharedVar.player2_connected = False

	    		if self.name == "player1" and SharedVar.player2_connected or self.name == "player2" and SharedVar.player1_connected:
		    		self.send_other({'state':"OTHER",
		    				'game_state':"WAIT",
		    				'msg': "The other player disconnected. Please wait for another player to join in..."})

	    		print "Ending connection..."
	    		self.link.socket.close()
	    		# self.serversocket.close()

	    		if self.name == "player1":
		    		SharedVar.clientlist[0] = None
	    		elif self.name == "player2":
		    		SharedVar.clientlist[1] = None

	    		return

	    	else:
	    		self.send({'state':"OKAY",
	    				'game_state':"END",
	    				'msg': "Received state: " + state})
