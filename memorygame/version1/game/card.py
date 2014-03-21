class Card:

	def __init__(self, back, front, card_name):
		self.back = back
		self.front = front
		self.current = back
		self.card_name = card_name