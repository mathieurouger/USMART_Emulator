import socket

class clientSocket:

	def __init__(self, port):

		self.host = socket.gethostname()
		self.port = port
		self.client_socket

	def connect(self, attempt = 0):
			self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        	self.client_socket.connect((self.host, self.port))
        	print('Connection to port', port, 'established')

    def sendData(self, message):
    	message = message + '\n'
		self.client_socket.sendall(message.encode('utf-8'))
    	return message

    def receiveData(self):
    	receivedData = None
    	while receivedData.lower().strip() != 'bye':
			receivedData = self.client_socket.recv(1024).decode('utf-8')
			receivedData = receivedData.strip('\r\n')
			print('Received from server :' + receivedData)
			return receivedData

		print('Server wanted to disconnect')
		self.client_socket.close()

	def disconnect(self):
		self.client_socket.close()
		print('Connection to port', port, 'closed')



