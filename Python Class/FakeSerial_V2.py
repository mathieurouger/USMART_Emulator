from unetpy import *
import socket
import clientSocket

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

        self.last_instruction = ''
        self.nodeID = ''
        self.remote_nodeID = ''
        self.command = ''
        self._isOpen  = True
        self._receivedData = ''
        self._data = 'It was the best of times.\nIt was the worst of times.\n'
        self.phy = ''
        self.pySocket = ''
        


    # isOpen()
    # returns True if the port to the Arduino is open.  False otherwise
    def isOpen( self ):
        return self._isOpen

    ## open()
    # opens the port
    def open( self ):
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
        _type = None
        print( 'FakeSerial got: ' + self.command)
        # SET_ADDRESS
        if (self.command[0:2] == '$A' and len(self.command) == 5):
            _type = 'set_address'
            self.nodeID = string[2:]
            self.pySocket = clientSocket.clientSocket(self.nodeID)  # initialize the clientSocket class
            self.pySocket.sendData(_type)    # need to fix the rsp Generic Message on UnetStack
            self.last_instruction = 'SET_ADDRESS_INSTRUCTION'
        # QUERY STATUS
        elif (self.command == '$?'):
            _type = 'query_status'
            self.pySocket.sendData(_type)
            self.last_instruction = 'QUERY_STATUS_INSTRUCTION'
        # SUPPLY VOLTAGE
        elif (self.command[0:2] == '$V' and len(self.command) == 5):
            _type = 'supply_voltage'
            to_addr = self.command[2:]
            self.pySocket.sendData(_type, to_addr)
            self.last_instruction = 'SUPPLY_VOLTAGE_INSTRUCTION'
        # PING
        elif (self.command[0:2] == '$P' and len(self.command) == 5):
            _type = 'ping'
            to_addr = self.command[2:]
            # print(to_addr, type(to_addr))
            self.pySocket.sendData(_type, to_addr)
            self.last_instruction = 'PING_INSTRUCTION'

        else:
            print("write FAILURE")
        
	
    ## readline()
    # reads characters from the fake Arduino until a \n is found.
    def readline( self ):
        self._receivedData = self.pySocket.receiveData()
        return self._receivedData

    def reset_input_buffer( self ):
        return

    def reset_output_buffer( self ):
        return

    def nodeID_to_API(self):
        API = int(self.nodeID) + 1100
        return API

    ## __str__()
    # returns a string representation of the serial class
    def __str__( self ):
        return  "Serial<id=0xa81c10, open=%s>( port='%s', baudrate=%d," \
               % ( str(self.isOpen), self.port, self.baudrate ) \
               + " bytesize=%d, parity='%s', stopbits=%d, xonxoff=%d, rtscts=%d)"\
               % ( self.bytesize, self.parity, self.stopbits, self.xonxoff,
                   self.rtscts )
    