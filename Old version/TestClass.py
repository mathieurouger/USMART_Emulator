import struct
import numpy as np
import FakeSerial as serial

class TestClass:
    ## init(): the constructor.  Many of the arguments have default values
    # and can be skipped when calling the constructor.
    # same time as a Serial
    # same readtimeout and writetimeout as used in Nanomodem from MasterAnchor

    def __init__(self):

        self.soundspeed = 1500
        self.portname = "COM1"
        self.baudrate = 19500
        self.readtimeout = 1000
        self.writetimeout = 1000
        self.serport = serial.Serial(self.portname, self.baudrate, timeout=self.readtimeout,
                                     write_timeout=self.writetimeout)


    def run_test(self):
        print("\ntest_set_self_address() should be called at the beginning of the test\n")

        self_address = False
        self_address = self.test_set_self_address()
        print ("self_address test is :", self_address)
        remote_node = "002"

        check_query_response = self.test_check_query_response(remote_node)
        print("check_query_response test is :", check_query_response)

        if self_address == False:
            print("self_address has not been set up correctly, the program can't continue")
            return
        else:
            self_status = self.test_query_self_status()
            print ("self_status test is :", self_status)

            query_node_status = self.test_query_node_id(remote_node)
            print("query_node_status is :", query_node_status)
            if query_node_status == True:
                check_query_response = self.test_check_query_response(remote_node)
            print("check_query_response test is :", check_query_response)
            

    def test_set_self_address(self): 
        """
        test_set_self_address()
        test the setting of a node address, writing to and receiving from the modem
        The address should be of 3 characters, e.g., "000" to "255".
        If successful return True otherwise False
        """
        print('### Testing set up address ###')
        node_id = "001" # node_id of the form of 3 chr string already verified in Nanomodem.py
        
        command = b'$A' + node_id.encode()
        self.serport.write(command)

        received_bytes = self.serport.readline()
        index = received_bytes.find(b'#A')
        #print("SET_ADDRESS len is "+ str(len(received_bytes)) +" and index is "+str(index))

        if (index != -1) and (len(received_bytes) - index == 5 and received_bytes.decode()[1] == 'A'): 
        # received_bytes[1] == b'A' as condition doesn't work because x = b'A' still stay b'A' and x[0] give 65 (the byte for A)
            #print("SET_ADDRESS A was spot on")
            if received_bytes[1:4] == command[1:4]:
                node_id = received_bytes.decode()[2:5]
                print("SET_ADDRESS node is :"+ node_id)
                print("set self address SUCCESS")
                return True
        else: 
            print("set self address FAILURE")
            return False    

    def test_query_self_status(self):
        """
        test_query_self_status()

        Checks that status of the parent Nanomodem.
        Return the address and voltage of the parent Nanomodem otherwise raises Exception

        See also: query_node_status
        """
        print('\n### Testing query self status ###')

        command = b'$?'
        self.serport.write(command)
        received_bytes = self.serport.readline()
        index = received_bytes.find(b'#A')

        if (index != -1) and (len(received_bytes) - index == 10):
            if received_bytes[index+5:index+6] == b'V':
                # print("check_for_valid_ack_signal SELF_STATUS V was spot on")
                for i in range(index+6, index+10):
                    if b'0' <= received_bytes[i:i+1] <= b'9':
                        pass
                    else:
                        print("query self status FAILURE 1")
                        return False
                node_id = received_bytes.decode()[index+2:index+5]
                print("SELF_STATUS node is :", node_id)

                voltage = round(float(received_bytes[index+6:index+10]) * (15.0/65536.0), 3)
                print("SELF_STATUS voltage is :", voltage)
                print("query self status SUCCESS")
                return  True
        else:
            print(" query self status FAILURE 2")
            return False    

    def test_query_node_id(self,node_id):
        """
        test_query_node_status(node_id)

        Requests the status of remote node with specific node_id.
        Returns 0 if query was sent, otherwise -1
        """

        print('\n### Testing query node status ACK ###')
        print('Remember that node_id must be a 3 characters string')

        command = b'$V' + node_id.encode()
        self.serport.write(command)
        received_bytes = self.serport.readline()
        index = received_bytes.find(b'$V')

        #ACK COMMAND
        if (index != -1) and (len(received_bytes) - index == 5 and received_bytes.decode()[1] == 'V'):
            #print("SET_ADDRESS V was spot on")
            if received_bytes[1:4] == command[1:4]:
                node_id = received_bytes.decode()[2:5]
                print("command has well been sent to  node :"+ node_id)
                print("acknowledgement of the command SUCCESS")
                return True
        else: 
            print("acknowledgement of the command FAILURE")
            return False

    def test_check_query_response(self, node_id):
        """
        test_check_query_response(node_id)

        Checks if the node with specific address has replied for the status query.
        Returns the voltage of the queried node if response was received correctly,
        otherwise -1

        Note: Wait for sufficient time after issuing query_node_status command to
        receive the response. Re-issue the check_ping_response command after some
        waiting if required!

        See also
        query_node_status
        """

        print('\n### Testing query node status RESPONSE ###')
        print('Remember that node_id must be the same 3 characters string that in test_query_node_id(node_id)')

        received_bytes = self.serport.readline()
        if received_bytes == b'E\r\n':
            print("You received Error Msg!")
            print(f'Did not receive correct query status response from node {node_id}')
            print(f'Query again the node {node_id} if required')
            return False

        elif (len(received_bytes) == 13) and (received_bytes[0:8] == b'#B' + node_id.encode() + b'06V'):
            supply_voltage = received_bytes.decode()[8:13]
            print(f"supply_voltage of {node_id} is {supply_voltage}")
            print("response from the remote node SUCCESS")
            return True
        else:
            print(f'Did not receive correct query status response from node {node_id}')
            print(f'Query again the node {node_id} if required')
            return False