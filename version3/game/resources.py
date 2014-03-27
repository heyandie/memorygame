import pyglet

def position_image(image,x,y):

	image.anchor_x = x
	image.anchor_y = y

pyglet.resource.path = ['../resources']
pyglet.resource.reindex()

card_back = pyglet.resource.image("card_back.png")
position_image(card_back, 0, card_back.height)

card_front = []
i = 0 

while i < 10 :

	card_name = "card_" + str(i+1) + ".png"
	card_front.append(pyglet.resource.image(card_name))
	position_image(card_front[i], 0, card_back.height)
	i += 1


card_select_border = pyglet.resource.image("card_select.png")
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
