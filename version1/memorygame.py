import pyglet
import time
import thread
import random
from pyglet.window import mouse
from pyglet.window import key
from game import resources,card


# Disable error checking for increased performance
pyglet.options['debug_gl'] = False

from pyglet.gl import *

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
index_list = [i for i in range(10)] + [i for i in range(10)]

# we shuffle the index list to shuffle their arrangement on the board
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


# check if the two flipped cards are matching pairs
def check_move():
	global flipped_cards
	global flipped_index

	if flipped_cards[0].card_name != flipped_cards[1].card_name:

		# delay the card showing for 1 second
		event_loop.sleep(1)
		for item in flipped_cards:
			item.current = item.back
		
	else:
		for item in flipped_index:
			matched_index.append(item)
		print "Yes"

	# empty the flipped cards
	flipped_cards = []

	# empty the flipped indexes
	flipped_index = []


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
	global card_select_x 
	global card_select_y
	global card_select_pos
	global flipped_cards
	global matched_index

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

		if  card_select_pos not in matched_index and card_select_pos not in flipped_index:
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


# main function
if __name__ == "__main__":
	event_loop.run()