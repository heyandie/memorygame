import pyglet
import os
import random

def position_image(image,x,y):

	image.anchor_x = x
	image.anchor_y = y

pyglet.resource.path = ['../resources']
pyglet.resource.reindex()

card_back = pyglet.resource.image("cardback.png")
position_image(card_back, 0, card_back.height)

game_background = pyglet.resource.image("game_background.png")
position_image(game_background, 0, game_background.height)

game_title = pyglet.resource.image("game_title.png")
position_image(game_title, 0, game_title.height)

card_front = []
card_front_list = os.listdir("../resources/cards_front")

 
i=0

for item in card_front_list:
	card_name = "cards_front/" + item
	if "a.png" in card_name:
		a,b  = card_name.split("a.png")
	else:
		a,b  = card_name.split("b.png")
	card = {
		'image': pyglet.resource.image(card_name),
		'name': a
	}
	card_front.append(card)
	position_image(card_front[i]['image'], 0, card_back.height)

	i += 1


card_select_border = pyglet.resource.image("cardselect.png")
position_image(card_select_border,0,card_select_border.height)


# --- SharedVar ---------------------------------------------------------------------------------------------------------

# Class SharedVar contains all game states
class SharedVar:
	state = {
			'WAIT':0,						# for the server: wait for clients to connect before starting the game
											# for clients: wait for other player's turn to end

			'START':1,						# start game (will be used for title screen/menu)
			'SETUP':2,						# intialize variables (such as cards on the grid); used before game starts
			'PLAYER1':3,					# player 1's turn (for version2)
			'TRANSITION_PLAYER1':4,			# setup for player 2 (for version2)
			'PLAYER2':5,					# player 2's turn (for version2)
			'TRANSITION_PLAYER2':6,			# setup for player 1 (for version2)
			'END':7,						# game over and scoring
			'PLAY':8,						# for client: turn to play
			'TRANSITION':9					# for client: setup game before each turn
			}

	player1_connected = False
	player2_connected = False
	# clientlist = [None, None]
	clients = [None, None]

	player1 = 0
	player2 = 0

	index_list = [i for i in range(20)]
	random.shuffle(index_list)

	matched_index = []
	other = None

	username1 = ''
	username2 = ''
