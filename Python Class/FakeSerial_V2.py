from unetpy import *
import socket
import clientSocket as pySocket


# a Serial class emulator
class Serial:

    ## init(): the constructor.  Many of the arguments have default values
    # and can be skipped when calling the constructor.
    def __init__( self, port='5000', baudrate = 19200, timeout=1, write_timeout=1,
                  bytesize = 8, parity = 'N', stopbits = 1, xonxoff=0,
                  rtscts = 0):
        self.name     = port
        self.port     = port
        self.timeout  = timeout
        self.write_timeout  = write_timeout
        self.parity   = parity
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.stopbits = stopbits
        self.xonxoff  = xonxoff
        self.rtscts   = rtscts
        self.last_instruction = ""
        self.node_id = ""
        self.remote_node_id = ""
        self.command = '$A001'
        self._isOpen  = True
        self._receivedData = ""
        self._data = "It was the best of times.\nIt was the worst of times.\n"
        self.phy = ''
        self.socket = pySocket.clientSocket(port)
        


    ## isOpen()
    # returns True if the port to the Arduino is open.  False otherwise
    def isOpen( self ):
        return self._isOpen

    ## open()
    # opens the port
    def open( self ):
        pySocket.connect()
        self._isOpen = True

    ## close()
    # closes the port
    def close( self ):
        pySocket.disconnect()
        self._isOpen = False

    ## write()
    # writes a string of characters to the Arduino
    def write( self, string):
        self.command = string.decode()
        string_test = "0A001"
        print( 'FakeSerial got: ' + self.command)
        # SET_ADDRESS
        if (self.command[0:2] == '$A' and len(self.command) == 5):
            self.node_id = string[2:]
            self.last_instruction = "SET_ADDRESS_INSTRUCTION"
        #elif
        else:
            print("write FAILURE")
        
        pySocket.sendData(self.command)

        return self.command
	
    ## readline()
    # reads characters from the fake Arduino until a \n is found.
    def readline( self ):
        self._receivedData() = pySocket.receiveData()
        return self._receivedData

    def reset_input_buffer( self ):
        return

    def reset_output_buffer( self ):
        return

    ## __str__()
    # returns a string representation of the serial class
    def __str__( self ):
        return  "Serial<id=0xa81c10, open=%s>( port='%s', baudrate=%d," \
               % ( str(self.isOpen), self.port, self.baudrate ) \
               + " bytesize=%d, parity='%s', stopbits=%d, xonxoff=%d, rtscts=%d)"\
               % ( self.bytesize, self.parity, self.stopbits, self.xonxoff,
                   self.rtscts )
    