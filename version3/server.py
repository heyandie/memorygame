"""

This is the server part of the game. Connect with clients here.

Game logic will be processed by Player class (in player.py).
Feel free to edit if there's missing code or extra code.

"""

import thread
import socket
import traceback
from threading import Thread
from connect import connection
from player import Player
from game.resources import SharedVar

# --- Global Variables ---------------------------------------------------------------------------------------------

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
	SharedVar.clientlist.append(link)
	print str(addr), " connected!"
	link.sendMessage("Thank you for connecting.\n")

	return (link, addr)

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