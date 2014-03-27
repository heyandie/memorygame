import socket
import traceback

class _myConnection:

	def __init__(self, s):
		self.socket = s

	def sendMessage(self, msg):
		try:
			return self.socket.send(msg)

		except socket.error as error:
			print "Error occured! " + str(error)
			traceback.print_exc()

	def getMessage(self):
		return self.socket.recv(9999)

def connection(s):
	return _myConnection(s)
