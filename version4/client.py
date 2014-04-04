"""

This is the client part of the game, with code extracted from memorygame.py
and networking/client.py.

Implementation of game logic (which is in the server part) should be here,
as well as anything that has to do with the frontend of the game.
(Feel free to edit if there's missing code or extra code.)

Notes:
	- use global keyword to access global variables outside classes
	- global variables player1 and player2 (used in scoring) is integrated
	  with Player class of server.py
	- edit update() function to only implement whatever server sends to client

"""

import pyglet
import time
import thread
import random
import socket
import traceback
import threading
# import eventlet
# from eventlet.green import socket
from game.connect import connection
from pyglet.window import mouse
from pyglet.window import key
from game import resources
from game.card import Card
from game.resources import SharedVar

try: import simplejson as json
except ImportError: import json

# Disable error checking for increased performance
pyglet.options['debug_gl'] = False

from pyglet.gl import *

# --- Global Variables ---------------------------------------------------------------------------------------------

window_width = 120*5
window_height = 120*4

# this is the main game loop
event_loop = pyglet.app.EventLoop()

# this is the main game window
game_window = pyglet.window.Window(window_width,window_height)
game_window.set_location(200,100)


# generate cards
# this is the array for the cards in the boards
cards_list = []

# this is the list of index for the cards on the board
# board is 20x20, a pair of cards has matching index i
# so if we have 20 cards, we have twice of 0-9 indexes
index_list = []

# initialize game_state to WAIT; required data for communication
game_state = SharedVar.state['START']
state = None
msg = None
send_message = False

# for going through a game state once
start = True

# window bg
game_background = pyglet.sprite.Sprite(img=resources.game_background,x=0,y=window_height)

# game title
game_title = pyglet.sprite.Sprite(img=resources.game_title,x=0,y=window_height)

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

# other player's flipped
other_flipped = []

# scores for players (should be deleted and integrate with server?)
player1 = 0
player2 = 0

# for client-server connection
link = None
clientsocket = None
data = None
to_receive = True
player1 = 0
player2 = 0
index_list = []
username = None
user1 = None
user2 = None
player = 0

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

	if game_state == SharedVar.state['PLAY']:
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
				send_data = {'state':"SYNC", 'game_state':game_state, 'flipped':card_select_pos}
				send(send_data)

# on key release events
@game_window.event
def on_key_release(symbol,modifiers):
	if game_state == SharedVar.state['PLAY']:
		if symbol == key.SPACE:
			# if there are already 2 flipped cards on the board
			if len(flipped_cards) == 2:
				check_move()

@game_window.event
def on_close():
	event_loop.exit()
	game_window.close()
	

game_over = pyglet.text.Label("Game Over!",
			font_name = "Liberation Serif",
			font_size = 36,
			x = game_window.width//2,
			y = game_window.height//2 + 150,
			anchor_x = 'center',
			anchor_y = 'center',
			)

player1_label = pyglet.text.Label("Player 1",
			font_name = "Liberation Serif",
			font_size = 24,
			x = game_window.width//2 - 240,
			y = game_window.height//2 + 50,
			)

player2_label = pyglet.text.Label("Player 2",
			font_name = "Liberation Serif",
			font_size = 24,
			x = game_window.width//2 - 240,
			y = game_window.height//2 + 10,
			)

player1_score = pyglet.text.Label("0",
			font_name = "Liberation Serif",
			font_size = 24,
			x = game_window.width//2 + 200,
			y = game_window.height//2 + 70,
			anchor_x = 'center',
			anchor_y = 'center',
			)

player2_score = pyglet.text.Label("0",
			font_name = "Liberation Serif",
			font_size = 24,
			x = game_window.width//2 + 200,
			y = game_window.height//2 + 30,
			anchor_x = 'center',
			anchor_y = 'center',
			)

draw_label = pyglet.text.Label("Draw!",
			font_name = "Liberation Serif",
			font_size = 30,
			x = game_window.width//2,
			y = game_window.height//2 - 80,
			anchor_x = 'center',
			anchor_y = 'center',
			)

player1_win = pyglet.text.Label("Player 1 Wins!",
			font_name = "Liberation Serif",
			font_size = 30,
			x = game_window.width//2,
			y = game_window.height//2 - 80,
			anchor_x = 'center',
			anchor_y = 'center',
			)

player2_win = pyglet.text.Label("Player 2 Wins!",
			font_name = "Liberation Serif",
			font_size = 30,
			x = game_window.width//2,
			y = game_window.height//2 - 80,
			anchor_x = 'center',
			anchor_y = 'center',
			)

@game_window.event
def on_draw():
	global game_state
	global player1
	global player2
	global user1
	global user2
	game_window.clear()

	player1_score.text = str(player1)
	player2_score.text = str(player2)

	if game_state == SharedVar.state['START']:
		game_background.draw()
		game_title.draw()
		print "statatatat"

	if user1 != '':
		player1_label.text = str(user1) + " (Player 1)"
		player1_win.text = str(user1) + " Wins!"
	if user2 != '':
		player2_label.text = str(user2) + " (Player 2)"
		player2_win.text = str(user2) + " Wins!"


	if game_state == SharedVar.state['END'] or game_state == SharedVar.state['TRANSITION']:
		game_over.draw()
		player1_label.draw()
		player2_label.draw()
		player1_score.draw()
		player2_score.draw()
		if player1 > player2:
			player1_win.draw()
		elif player2 > player1:
			player2_win.draw()
		else:
			draw_label.draw()
	
	else:
		draw_cards(cards_list)

@game_window.event
def on_close():
	global clientsocket
	global game_state
	send_data = {'state':"QUIT", 'game_state':game_state}
	send(send_data)
	clientsocket.close()
	event_loop.exit()
	pyglet.app.exit()

# --- Client Configuration -----------------------------------------------------------------------------------------

def connectToServer(clientsocket, host, port):
	# host = ''#'10.40.72.114' #raw_input("Enter IP Address: ")
	# port = 1111 #int(raw_input("Enter port number: "))
	clientsocket.connect((host, port))
	link = connection(clientsocket)
	print link.getMessage()
	return link

def establishConnection(host, port):
	global link
	global clientsocket
	global game_state
	global state
	global msg
	global to_receive
	global index_list
	global username
	global game_window

	# connect with server first
	while link == None:
		try:
			clientsocket = socket.socket()
			link = connectToServer(clientsocket, host, port)
			data = {'state':"CONNECT", 'game_state':SharedVar.state['WAIT'], 'username': username}
			send(data)
			data = receive()
			print "receiving..."
			state = data['state']
			game_state = data['game_state']
			msg = data['msg']
			if game_state == SharedVar.state['SETUP']:
				index_list = data['index_list']
				if username == '':
					username = data['caption']
				else:
					username = username + " (" + data['caption'] + ")"
				
				game_window.set_caption(username)

		except Exception as error:
			print "Client: Error occured! " + str(error)
			traceback.print_exc()

# --- Communication with Server ------------------------------------------------------------------------------------

def send(data):
	global link
	data = json.dumps(data)
	link.sendMessage(data)

def receive():
	global link
	message = link.getMessage()
	return json.loads(message)

# --- Update/Game Loop ---------------------------------------------------------------------------------------------

"""

NOTES ON UPDATE
	- update() function acts as the game loop
	- some parts should be integrated with the server while others will be retains.
	- update() should implement whatever the server sends to the client
	- use send() and receive() functions to communicate with server
	- send() and receive() functions automatically encode/decode the messages already
	- send() requires one parameter (the data to be sent; use dictionary)
	- receive() returns decoded message
	- don't add additional parameters to update() function

	Other notes about communication between server and client can be found in the Player
	class of server.py.

	BASIC RUNDOWN:
		- update will act as game loop so it should continuously check game states
		- no title screen/menu yet so proceed to game immediately for now
		- feel free to make changes; this is just the suggested rundown

		1. Server will send message to clients to change their game_state to START once
		   both clients have connected.
		
		2. Send message to server if game_state changed to START. Server will check
		   if both clients are ready. (analogous to ACK)
		
		3. Server will setup the game and send the data to clients so clients can
		   setup the game according to server's specifications.
		
		4. Game starts. Yay! Once server knows both clients are setup (clients should
		   send message to let server know), it should send PLAY game_state to player1
		   client, and WAIT game_state to player2.
		
		5. In update(), client will only move if their game_state is PLAY.

		6. Send data if client is done flipping two tiles.

		7. Server receives data, checks if both cards match, adds score of player if so,
		   and sends data to both clients so they can update frontend. Server also sets
		   game_state of client to TRANSITION.
		
		8. During TRANSITION state, clients will update data given by server. Send
		   message to tell server they're done.
		
		9. Server sends PLAY to player2, WAIT to player1. Cycle repeats.
		
		10. When server receives data from clients during PLAY, it should check if all
		    cards have been flipped. If so, the game is over. Server sends END game_state
		    to both clients, with scores of each so they can update frontend.

"""

def check_move():
	global flipped_cards
	global flipped_index
	global game_state
	global matched_index
	global to_receive
	score = 0

	if flipped_cards[0].card_name != flipped_cards[1].card_name:
		# delay the card showing for 1 second
		event_loop.sleep(1)
		for item in flipped_cards:
			item.current = item.back		
	else:
		if game_state == SharedVar.state['PLAY']:
			score += 1

	send_data = {'state':"PLAY OKAY",
				'game_state':game_state,
				'score':score,
				'flipped_index':flipped_index}
	send(send_data)
	to_receive = True

	# empty the flipped cards
	flipped_cards = []

	# other player's flipped
	other_flipped = []

	# empty the flipped indexes
	flipped_index = []

def update(dt):
	global game_state
	global state
	global msg
	global start
	global link
	global clientsocket
	global data
	global send_message # set to True if client will send to server
	global to_receive
	global player1
	global player2
	global index_list
	global matched_index
	global cards_list
	global username
	global player
	global user1
	global user2
	global other_flipped

	# --- Game Loop ------------------------------------------------------------

	if msg == "Goodbye!":
		print msg
		clientsocket.close()
		event_loop.exit()
		pyglet.app.exit()
	
	if game_state == SharedVar.state['SETUP']:
		# index_list = [i for i in range(10)] + [i for i in range(10)]
		# random.shuffle(index_list)
		# index_list = data['index_list']
		# generate images for the card
		i = 0
		j = 0
		k = 0

		# 4 rows
		while i<4:
			j=0

			# 5 columns
			while j<5:
				x_pos = j * 120
				y_pos = window_height - (i *120)

				# index is the kth item in the shuffled index list
				index = index_list[k]
				card_name = "card" + str(index+1)
				card_back = pyglet.sprite.Sprite(img=resources.card_back,x=x_pos,y=y_pos)
				card_front = pyglet.sprite.Sprite(img=resources.card_front[index]['image'],x=x_pos,y=y_pos)
				new_card = Card(card_back,card_front,resources.card_front[index]['name'])
				cards_list.append(new_card)

				j = j + 1
				k = k + 1

			i = i + 1

		send_data = {'state':"SETUP OKAY",
					'game_state':game_state}
		send(send_data)
		to_receive = True
		game_state = SharedVar.state['WAIT']

	elif game_state == SharedVar.state['WAIT']:
		to_receive = True

	elif game_state == SharedVar.state['END']:
		player1 = data['player1']
		player2 = data['player2']
		print "GAME OVER"
		# print "PLAYER 1 SCORE:", player1
		# print "PLAYER 2 SCORE:", player2
		# if player1 > player2:
		# 	print "PLAYER 1 WINS!!"
		# elif player2 > player1:
		# 	print "PLAYER 2 WINS!!"
		# else:
		# 	print "IT'S A DRAW!!"
		# print user1, user2

		to_receive = False
		game_state = SharedVar.state['TRANSITION']

	# --- Communicate ----------------------------------------------------------

	if send_message:
		start = True
		message = raw_input("> ")
		send_data = {'state':message, 'game_state':message}
		send(send_data)

	try:
		if to_receive:
			print "receiving..."
			data = receive()
			state = data['state']
			game_state = data['game_state']
			msg = data['msg']

			if game_state == SharedVar.state["PLAY"] or game_state == SharedVar.state["END"]:
				for index, card in enumerate(cards_list):
					if index in other_flipped:
						card.current = card.back

				matched_index = data['matched_index']
				for index, card in enumerate(cards_list):
					if index in matched_index:
						card.current = card.front

				

				other_flipped = []



			if game_state == SharedVar.state["END"]:
				player = data['player']
				user1 = data['user1']
				user2 = data['user2']

			if game_state == SharedVar.state["WAIT"]:
				if 'flipped' in data.keys():

					index = data['flipped']
					other_flipped.append(index)
					cards_list[index].current = cards_list[index].front


			print msg
			to_receive = False

	except socket.error, e:
		print "No data to receive."
		msg = None

	send_message = False
	to_receive = False


# --- Main ---------------------------------------------------------------------------------------------------------

def main():
	global link
	global clientsocket
	global game_state
	global state
	global msg
	global to_receive
	global index_list
	global username
	global game_window

	host = raw_input("Host: ")
	port = int(raw_input("Port: "))
	username = raw_input("Username: ")
	if username != None:
		game_window.set_caption(username)

	establishConnection(host, port)

	# start game
	pyglet.clock.schedule_interval(update, 1/120.0)
	pyglet.clock.set_fps_limit(120)
	event_loop.run()

if __name__ == "__main__":
	main()