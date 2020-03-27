import socket
from unetpy import *
from fjagepy import *

class clientSocket:

	def __init__(self, nodeID = '001'):

		self.host = socket.gethostname()
		self.nodeID = int(nodeID)
		self.port = int(nodeID) + 1100
		self.sock = UnetSocket(self.host, self.port)
		self.gw = self.sock.getGateway()

	def sendData(self, _type, to_addr, data):
		IDreq = 1

		pyagent = 'pyagent' + str(self.nodeID)
		gmsg = GenericMessage(perf = Performative.REQUEST, recipient = pyagent)
		gmsg.IDreq = IDreq
		gw.send(gmsg)

		IDreq = IDreq + 1

		gmsg2 = GenericMessage(perf = Performative.REQUEST, recipient = pyagent)
		gmsg2.type = _type
		gmsg2.data = data
		gmsg2.from_addr = self.nodeID
		gmsg2.to_addr = to_addr
		gmsg2.IDreq = IDreq
		gw.send(gmsg2)

		IDreq = 0

	def receiveData(self):
		rgmsg = self.gw.receive(GenericMessage, 4000)
		print ('rg msg :', rgmsg.state, 'rsp :', rgmsg.data)
		print('Ping time is', rgmsg.time_ping, 'ms')

		return rgmsg.data

	def disconnect(self):
		self.client_socket.close()
		print('Connection to port', port, 'closed')



