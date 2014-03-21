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


