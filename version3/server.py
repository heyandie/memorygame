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

	# check if the two flipped cards are matching pairs (lifted from memorygame.py)
	def check_move():
		global flipped_cards
		global flipped_index
		global game_state
		global player1
		global player2
		global matched_index

		if flipped_cards[0].card_name != flipped_cards[1].card_name:
			# delay the card showing for 1 second
			event_loop.sleep(1)
			for item in flipped_cards:
				item.current = item.back
			if game_state == SharedVar.state['PLAYER1']:
				game_state = SharedVar.state['TRANSITION_PLAYER1']
			elif game_state == SharedVar.state['PLAYER2']:
				game_state = SharedVar.state['TRANSITION_PLAYER2']
			
		else:
			for item in flipped_index:
				matched_index.append(item)
			if game_state == SharedVar.state['PLAYER1']:
				player1 += 1
			elif game_state == SharedVar.state['PLAYER2']:
				player2 += 1
			if len(matched_index) == 20:
				game_state = SharedVar.state['END']

		# empty the flipped cards
		flipped_cards = []

		# empty the flipped indexes
		flipped_index = []
 
 	"""

 	Game logic and all computations of the server should be implemented in the run() method.
 	To end thread, use return. Otherwise, keep everything inside the while True loop.

 	Basic rundown:
 		1. Check game_state
 		2. Do necessary setup and computations
 		3. Send to both clients: what game_state they should be on (may differ between them),
 		   necessary variables for setup
   	 
	Check update() function below. Code there should be integrated with run() function.
	(There shouldn't be too many changes for integration... I think.) 

	Note: starting game_state of the server is SharedVar.state['WAIT']. Change game_state once both clients have connected.
	Game states: (descriptions also in resources.py)
		WAIT (server: wait for clients to connect; client: wait for other player's turn to finish)
		START (for clients only?)
		SETUP (initial setup of game)
		TRANSITION (set client's game_state to this to setup game for next turn)
		PLAY (client's turn to play; other client should have WAIT game state)
		END (game over; scoring)


	More notes about communication between server and client in the update() function of client.py.
	"""

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

# --- Update -------------------------------------------------------------------------------------------------------

# Updated function taken directly from memorygame.py
# This function should be deleted and integrated with the run() function in Player class instead.
def update(dt):
	global game_state
	global player1
	global player2
	global start

	if game_state == SharedVar.state['START']:
		game_state = SharedVar.state['SETUP']

	elif game_state == SharedVar.state['SETUP']:
		# we shuffle the index list to shuffle their arrangement on the board
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
				new_card = card.Card(card_back,card_front,card_name)
				cards_list.append(new_card)

				j = j + 1
				k = k + 1

			i = i + 1

		game_state = SharedVar.state['PLAYER1']

	# elif game_state == SharedVar.state['PLAYER1']:
	# 	print "PLAYER1"

	elif game_state == SharedVar.state['TRANSITION_PLAYER1']:
		game_state = SharedVar.state['PLAYER2']

	elif game_state == SharedVar.state['TRANSITION_PLAYER2']:
		game_state = SharedVar.state['PLAYER1']

	elif game_state == SharedVar.state['END']:
		if start:
			start = False
			print "GAME OVER"
			print "PLAYER 1 SCORE:", player1
			print "PLAYER 2 SCORE:", player2
			if player1 > player2:
				print "PLAYER 1 WINS!!"
			elif player2 > player1:
				print "PLAYER 2 WINS!!"
			else:
				print "IT'S A DRAW!!"

# --- Main ---------------------------------------------------------------------------------------------------------

# main() function taken directly from server.py.
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