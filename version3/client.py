"""

This is the client part of the game, with code extracted from memorygame.py and networking/client.py.

Implementation of game logic (which is in the server part) should be here,
as well as anything that has to do with the frontend of the game.
(Feel free to edit if there's missing code or extra code.)

Notes:
	- use global keyword to access global variables outside classes
	- global variables player1 and player2 (used in scoring) should be integrated with Player class of server
	- edit update() function to only implement whatever server sends to client
	- update() function will act as the game loop
	- use sender() and communicate() functions to communicate with server

"""

import pyglet
import time
import thread
import random
import socket
import traceback
import threading
from connect import connection
from pyglet.window import mouse
from pyglet.window import key
from game import resources,card
from game.resources import SharedVar

try: import simplejson as json
except ImportError: import json

# Disable error checking for increased performance
pyglet.options['debug_gl'] = False

from pyglet.gl import *

# --- Global Variables ---------------------------------------------------------------------------------------------

window_width = 800
window_height = 600

# this is the main game loop
event_loop = pyglet.app.EventLoop()

# this is the main game window
game_window = pyglet.window.Window(window_width,window_height)

# generate cards
# this is the array for the cards in the boards
cards_list = []

# this is the list of index for the cards on the board
# board is 20x20, a pair of cards has matching index i
# so if we have 20 cards, we have twice of 0-9 indexes
index_list = []

# initialize game_state to START
game_state = SharedVar.state['START']

# for going through a game state once
start = True

# selector for the card
card_select_border = pyglet.sprite.Sprite(img=resources.card_select_border,x=0,y=window_height)

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

# scores for players (should be deleted and integrate with server?)
player1 = 0
player2 = 0

# --- Frontend -----------------------------------------------------------------------------------------------------

def flip(card):
	card.current.draw()
	
# draw the cards on the board
def draw_cards(cards_list):
	for card in cards_list:
		flip(card)

	card_select_border.draw()

# on key press events
@game_window.event
def on_key_press(symbol, modifiers):
	global game_state
	global card_select_x 
	global card_select_y
	global card_select_pos
	global flipped_cards
	global matched_index
	global player1
	global player2

	# let user move selector to the right
	if symbol == key.RIGHT:
		if card_select_border.x + card_select_border.width >= window_width:
			card_select_border.x = 0
		else:
			card_select_border.x += card_select_border.width

		if card_select_x >= 4:
			card_select_x = 0
		else:
			card_select_x += 1

		card_select_pos = card_select_x + (card_select_y * 5)

	# let user move selector to the left
	if symbol == key.LEFT:
		if card_select_border.x - card_select_border.width < 0:
			card_select_border.x = window_width - card_select_border.width
		else:
			card_select_border.x -= card_select_border.width

		if card_select_x <= 0:
			card_select_x = 4
		else:
			card_select_x -= 1

	card_select_pos = card_select_x + (card_select_y * 5)

	# let user move selector upwards
	if symbol == key.UP:
		if card_select_border.y + card_select_border.height >= window_height + card_select_border.height:
			card_select_border.y= card_select_border.height
		else:
			card_select_border.y += card_select_border.height

		if card_select_y <= 0:
			card_select_y = 3
		else:
			card_select_y -= 1
		
		card_select_pos = card_select_x + (card_select_y * 5)

	# let user move selector downwards
	if symbol == key.DOWN:
		if card_select_border.y - card_select_border.height < card_select_border.height:
			card_select_border.y = window_height
		else:
			card_select_border.y -= card_select_border.height

		if card_select_y >= 3:
			card_select_y = 0
		else:
			card_select_y += 1

		card_select_pos = card_select_x + (card_select_y * 5)

	# let the users flip up a card
	if symbol == key.SPACE:
		if card_select_pos not in matched_index and card_select_pos not in flipped_index:
			cards_list[card_select_pos].current = cards_list[card_select_pos].front
			flipped_cards.append(cards_list[card_select_pos])
			flipped_index.append(card_select_pos)

# on key release events
@game_window.event
def on_key_release(symbol,modifiers):
	if symbol == key.SPACE:
		# if there are already 2 flipped cards on the board
		if len(flipped_cards) == 2:
			check_move()

@game_window.event
def on_close():
	event_loop.exit()
	game_window.close()
	
@game_window.event
def on_draw():
	game_window.clear()
	draw_cards(cards_list)

# --- Client Configuration -----------------------------------------------------------------------------------------

def connectToServer(clientsocket):
	host = ''#'10.40.72.114' #raw_input("Enter IP Address: ")
	port = 1111 #int(raw_input("Enter port number: "))
	clientsocket.connect((host, port))
	link = connection(clientsocket)
	print link.getMessage()
	return link

# --- Communication with Server ------------------------------------------------------------------------------------

# send messages to server (lifted from client.py)
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

# receive messages from server; end connection if response is "Goodbye!"; (lifted from client.py)
def communicate(link, clientsocket):
	while True:
		response = link.getMessage()
		print response

		if response == "Goodbye!":
			break
	
	clientsocket.close()

# --- Update -------------------------------------------------------------------------------------------------------

"""

Notes:
	- update() function should be edited. Some parts will be integrated with the server.
	- update() should implement whatever the server sends to the client.
	- integrate sender() and communicate() to update for communicating with server
	- I don't think you should add additional parameters to update() function. (?)

Basic rundown for update():
	- update will act as game loop so it should continuously check game states
	- no title screen/menu yet so proceed to game immediately for now

	1. Server will send message to change game_state to START once both clients have connected.
	2. Send message to server if game_state changed to START. Server will check if both clients are ready. (analogous to ACK)
	3. Server will setup the game and send the data to clients so clients can setup the game according to server's specifications.
	4. Game starts. Yay! Once server knows both clients are setup (clients should send message to let server know),
		it should send PLAY game_state to player1 client, and WAIT game_state to player2.
	5. In update(), client will only move if game_state is PLAY.
	6. Send data if client is done flipping two tiles.
	7. Server receives data, checks if both cards match, adds score of player if so, and sends data to both clients so they can update frontend.
		Server also sets game_state of client to TRANSITION.
	8. During TRANSITION state, clients will update data given by server. Send message to tell server they're done.
	9. Server sends PLAY to player2, WAIT to player1. Cycle repeats.
	10. When server receives data from clients during PLAY, it should check if all cards have been flipped. If so, the game is over.
		Server sends END game_state to both clients, with scores of each so they can update frontend.

Other notes about communication between server and client in the run() method of Player class of server.py.
"""

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

def main():
	# connect with server first
	try:
		clientsocket = socket.socket()
		link = connectToServer(clientsocket)
		senderThread = threading.Thread(target=sender, args=(link,))
		senderThread.start()
		communicate(link, clientsocket)

	except Exception as error:
		print "Client: Error occured! " + str(error)
		traceback.print_exc()

	# start game
	pyglet.clock.schedule_interval(update, 1/120.0)
	pyglet.clock.set_fps_limit(120)
	event_loop.run()

if __name__ == "__main__":
	main()