import socket
import time
import random
import traceback
import threading
import json
from connect import connection

def socketSetup():
	host = ''
	port = 1111 #int(raw_input("Enter port number: "))
	serversocket = socket.socket()

	serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	serversocket.bind((host, port))
	print "Server ready..."
	serversocket.listen(5)
	return serversocket

def connectToClient(serversocket):
	remote_socket, addr = serversocket.accept()
	link = connection(remote_socket)
	print str(addr), " connected!"
	link.sendMessage("Thank you for connecting.")
	return (link, addr)

def communicate(link, addr):
	jokes = [	"A: Anong hayop ang may walang gilagid?\nB: Ano?\nA: Eh di lang-gum!",
				"A: Ano ang tawag sa maliit na duck?\nB: Ano?\nA: Pan-duck!",
				"A: Use MENTION in a sentence.\nB: Ang laki ng bahay mo, parang MENTION!",
			]
	pickup = [	"B: Barya ka ba?\nG: Bakit?\nB: Kasi umaga pa lang, kailangan na kita. <3",
				"B: Ang KAIBIGAN ay isang makahulugang salita.\nG: Bakit?\nB: Dahil paano ang IBIGAN kung wala KA?",
				"B: Semento ka ba?\nG: Bakit?\nB: KaSEMENTO be tayo.",
			]

	while True:
		message = link.getMessage()
		data = json.loads(message)
		message = data['msg']
		print message

		# print str(addr), ":", message
		
		# if message == "TIME":
		# 	tosend = "The time now is " + time.strftime("%a %b %d %I:%M:%S %Z %Y")
		# elif message[:11] == "MY NAME IS ":
		# 	tosend = "Hello " + message[11:] + "!"
		# elif message == "JOKE TIME":
		# 	tosend = random.choice(jokes)
		# elif message == "PICKUP":
		# 	tosend = random.choice(pickup)
		if message == "QUIT":
			link.sendMessage("Goodbye!")
			print "Ending connection..."
			break
		# else:
		# 	tosend = "I can't understand what you're saying."

		# sent = link.sendMessage(tosend)

	link.socket.close()

def main():
	try:
		serversocket = socketSetup()

		while True:
			commulink = connectToClient(serversocket)
			commThread = threading.Thread(target=communicate, args=(commulink))
			commThread.start()

		serversocket.close()

	except Exception as error:
		print "SERVER: ERROR OCCURED! " + str(error)
		traceback.print_exc()

if __name__ == '__main__':
	main()

















