from unetpy import *
from fjagepy import *
import socket
import json


# a Serial class emulator
class Serial:

    ## init(): the constructor.  Many of the arguments have default values
    # and can be skipped when calling the constructor.
    def __init__( self, port='COM1', baudrate = 19200, timeout=1, write_timeout=1,
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
        self.nodeID = ""
        self.remote_nodeID = ""
        self._isOpen  = True
        self._receivedData = ""
        self._data = "It was the best of times.\nIt was the worst of times.\n"
        self.phy = ''

    ## isOpen()
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
        self._isOpen = False

    ## write()
    # writes a string of characters to the Arduino
    def write( self, string):
        command = string.decode()


        # SET_ADDRESS
        if (command[0:2] == '$A' and len(command) == 5):
            self.nodeID = string[2:]
            self.last_instruction = "SET_ADDRESS_INSTRUCTION"
        # SELF_STATUS
        elif (command == '$?'):
            # self.node_id stored by SET_ADDRESS  
            self.last_instruction = "SELF_STATUS_INSTRUCTION"
        # QUERY_NODE_STATUS
        elif (command[0:2] == '$V' and len(command) == 5):
            self.remote_nodeID = command[2:]
            self.last_instruction = "NODE_STATUS_INSTRUCTION"
        # PING
        elif (command[0:2] == '$P' and len(command) ==5):
            self.remote_nodeID
            self.last_instruction = "PING_INSTRUCTION"
        else:
            print("write FAILURE")
        
        host = socket.gethostname()
        sock = UnetSocket(host, self.nodeID_to_API())
        gw = sock.getGateway()
        self.phy = gw.agentForService(Services.PHYSICAL)
        py_agent = gw.agent(pyagent)
        rsp1 = py_agent << DatagramReq()
        print(rsp1)
        return command

    ## readline()
    # reads characters from the fake Arduino until a \n is found.
    def readline( self ):

        energy = '%.0f' % self.phy.test   #round and convert into a string
        print (energy)
        received_message = 'wait'
        # SET_ADDRESS
        if (self.last_instruction == "SET_ADDRESS_INSTRUCTION"):
            print('type nodeID : ', type(self.nodeID))
            data_bytes = b'#A' + self.nodeID
            print ("data_bytes is :", data_bytes)
            return data_bytes
        # SELF_STATUS
        elif (self.last_instruction == "SELF_STATUS_INSTRUCTION"):
            data_bytes = b'#A' + self.nodeID + b'V' + energy.encode()
            print ("data_bytes is :", data_bytes)
            return data_bytes
        # QUERY_NODE_STATUS ACK
        elif (self.last_instruction == "NODE_STATUS_INSTRUCTION"):
            data_bytes = b'$V' + self.remote_nodeID.encode()
            print ("data_bytes is :", data_bytes)
            self.last_instruction = 'RESP_NODE_STATUS_INSTRUCTION'
            return data_bytes 
        # QUERY_NODE_STATUS RESPONSE
        elif (self.last_instruction == "RESP_NODE_STATUS_INSTRUCTION"):
            if received_message == None or len(received_message) != 5:
                return b'E\r\n'
            else:
                data_bytes = b'#B' + self.remote_nodeID.encode() + b'06V' + energy.encode()
                print ("data_bytes is :", data_bytes)
                return data_bytes 
            # else: error
        #elif:
        else:
            print("readline FAILURE")


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
