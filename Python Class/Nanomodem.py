import time
#import serial
import FakeSerial as serial
import struct

START_NODE_ID = 0
END_NODE_ID = 255
MAX_TRIES = 3
INTERVAL = 0.025
DEBUG = True

# ACK signal types
SET_ADDRESS = 1
SELF_STATUS = 2
PING = 3
NODE_STATUS = 4
UNICAST = 5
BROADCAST = 6
UNICAST_ACK = 7
TEST_ACK = 8
QLTY_CHECK = 9
ECHO_ACK = 10

class Nanomodem:
    """
    Nanomodem class
    It Initializes and open the associated serial port, and contains all the methods to manipulate the nanomodem.

    To use this class in your code:

    from Nanomodem import NANOMODEM

    and create instance of it, e.g.:

    nm = NANOMODEM()
    """

    def __init__(self, soundspeed=1530, portname="/dev/ttyUSB_MODEM", baudrate=9600, readtimeout=10, writetimeout=10):
        """
        Initializes and opens the serial port.
        :param portname:
        :param baudrate:
        :param readtimeout:
        :param writetimeout:
        """
        # global serport
        self.soundspeed = soundspeed
        self.portname = portname
        self.baudrate = baudrate
        self.readtimeout = readtimeout
        self.writetimeout = writetimeout
        self.serport = serial.Serial(self.portname, self.baudrate, timeout=self.readtimeout,
                                     write_timeout=self.writetimeout)

    @staticmethod
    def check_for_valid_ack_signal(bytes_line, ack_type):
        if ack_type == SET_ADDRESS:
            index = bytes_line.find(b'#A')
            if (index != -1) and ((len(bytes_line) - index) == 7):
                return 0
            else:
                return -1
        elif ack_type == SELF_STATUS:
            index = bytes_line.find(b'#A')
            print("check_for_valid_ack_signal SELF_STATUS len is "+ str(len(bytes_line)) +" and index is "+str(index))

            if (index != -1) and (len(bytes_line) - index == 13):
                if bytes_line[index+5:index+6] == b'V':
                    print("check_for_valid_ack_signal SELF_STATUS V was spot on")
                    for i in range(index+6, index+11):
                        if b'0' <= bytes_line[i:i+1] <= b'9':
                            pass
                        else:
                            return -1
                    node_id = bytes_line[index+2:index+5]
                    print("check_for_valid_ack_signal SELF_STATUS node is is "+ str(node_id))

                    return node_id.decode(), float(bytes_line[index+6:index+11]) * (15.0/65536.0)
                else:
                    return -1
            else:
                return -1
        elif ack_type == PING:
            index = bytes_line.find(b'$P')
            if (index != -1) and ((len(bytes_line) - index) == 7):
                return 0
            else:
                return -1
        elif ack_type == NODE_STATUS:
            index = bytes_line.find(b'$V')
            if (index != -1) and ((len(bytes_line) - index) == 7):
                return 0
            else:
                return -1
        elif ack_type == UNICAST:
            index = bytes_line.find(b'$U')
            if (index != -1) and ((len(bytes_line) - index) == 9):
                return int(bytes_line[5:7])
            else:
                return -1
        elif ack_type == UNICAST_ACK:
            index = bytes_line.find(b'$M')
            print ("index UNICAST =", index)
            print (len(bytes_line))
            if (index != -1) and ((len(bytes_line) - index) == 9):
                return int(bytes_line[5:7])
            else:
                return -1
        elif ack_type == ECHO_ACK:
            index = bytes_line.find(b'$E')
            if (index != -1) and ((len(bytes_line) - index) == 9):
                return int(bytes_line[5:7])
            else:
                return -1
        elif ack_type == TEST_ACK:
            index = bytes_line.find(b'$T')
            if (index != -1) and ((len(bytes_line) - index) == 7):
                return 0
            else:
                return -1
        elif ack_type == QLTY_CHECK:
            index = bytes_line.find(b'$C')
            if (index != -1) and ((len(bytes_line) - index) == 5):
                return int(bytes_line[2:3])
            else:
                return -1

        else:
            index = bytes_line.find(b'$B')
            if (index != -1) and ((len(bytes_line) - index) == 6):
                return int(bytes_line[2:4])
            else:
                return -1

    def set_self_address(self, node_id):
        """
        set_self_address(node_id)

        Sets address of the Node.
        The address should be of 3 characters, e.g., "000" to "255".
        If successful return 0 otherwise -1
        """
        if (not (len(node_id) == 3)) or (not isinstance(node_id, str)):
            if DEBUG:
                raise Exception("node_id should be a three characters string e.g., \"000\" to \"255\" ")
            else:
                return -1
        else:
            command = b'$A' + node_id.encode()
            self.serport.write(command)
            time.sleep(INTERVAL)

            # query for ack signal, if not, then flush serial write buffer
            # and re-issue the address set command (maximum 4 tires)
            num_of_tries = 1
            while True:
                error_flag = True
                for i in range(3):  # check for valid ACK signal at least in 3 lines
                    received_bytes = self.serport.readline()
                    status = self.check_for_valid_ack_signal(received_bytes, SET_ADDRESS)
                    if status != -1:
                        error_flag = False
                        break
                    else:
                        error_flag = True

                if error_flag and num_of_tries < MAX_TRIES:
                    self.serport.reset_input_buffer()
                    self.serport.reset_output_buffer()
                    time.sleep(INTERVAL)
                    if DEBUG:
                        print("Didn't receive correct ACK signal, re-issuing the set address command!")
                    self.serport.write(command)
                    time.sleep(INTERVAL)
                    num_of_tries += 1
                elif error_flag and num_of_tries >= MAX_TRIES:
                    raise Exception('Exceeded MAX_TRIES! See if Nanomodem is configured/connected correctly?')
                else:
                    return 0

    def query_self_status(self):
        """
        query_self_status()

        Checks that status of the parent Nanomodem.
        Return the address and voltage of the parent Nanomodem otherwise raises Exception

        See also: query_node_status
        """
        command = b'$?'
        self.serport.write(command)
        time.sleep(INTERVAL)

        # Check for ACK,if not then reset the serial read and write buffer and re-issue the command
        num_of_tries = 1
        while True:
            status = -1
            error_flag = True
            for i in range(3):  # check for valid ACK signal at least in 3 lines
                received_bytes = self.serport.readline()
                status = self.check_for_valid_ack_signal(received_bytes, SELF_STATUS)
                if status !=-1:
                    error_flag = False
                    break
                else:
                    error_flag = True

            if error_flag and (num_of_tries < MAX_TRIES):
                self.serport.reset_input_buffer()
                self.serport.reset_output_buffer()
                time.sleep(INTERVAL)
                if DEBUG:
                    print("Re-issuing the self query command!")
                self.serport.write(command)
                time.sleep(INTERVAL)
                num_of_tries += 1
            elif error_flag and (num_of_tries >= MAX_TRIES):
                raise Exception('Exceeded MAX_TRIES! See if the Nanomodem is configured/connected correctly?')
            else:
                return status

    def query_node_status(self, node_id):
        """
        query_node_status(node_id)

        Requests the status of remote node with specific node_id.
        Returns 0 if query was sent, otherwise -1
        """
        if (not (len(node_id) == 3)) or (not isinstance(node_id, str)):
            if DEBUG:
                raise Exception("node_id should be a three characters string e.g., \"000\" to \"255\" ")
            else:
                return -1
        else:
            command = b'$V' + node_id.encode()
            self.serport.write(command)
            time.sleep(INTERVAL)

            # query for ack signal, if not, then flush serial write buffer
            # and re-issue the address set command (maximum 4 tires)
            num_of_tries = 1
            while True:
                error_flag = True
                for i in range(3):  # check for valid ACK signal at least in 3 lines
                    received_bytes = self.serport.readline()
                    status = self.check_for_valid_ack_signal(received_bytes, NODE_STATUS)
                    if status != -1:
                        error_flag = False
                        break
                    else:
                        error_flag = True

                if error_flag and num_of_tries < MAX_TRIES:
                    self.serport.reset_input_buffer()
                    self.serport.reset_output_buffer()
                    time.sleep(INTERVAL)
                    if DEBUG:
                        print("Re-issuing the query status command!")
                    self.serport.write(command)
                    time.sleep(INTERVAL)
                    num_of_tries += 1
                elif error_flag and num_of_tries >= MAX_TRIES:
                    raise Exception('Exceeded MAX_TRIES! See if Nanomodem is configured/connected correctly?')
                else:
                    return 0

    def check_query_response(self, node_id):
        """
        check_query_response(node_id)

        Checks if the node with specific address has replied for the status query.
        Returns the voltage of the queried node if response was received correctly,
        otherwise -1

        Note: Wait for sufficient time after issuing query_node_status command to
        receive the response. Re-issue the check_ping_response command after some
        waiting if required!

        See also
        query_node_status
        """
        if (not (len(node_id) == 3)) or (not isinstance(node_id, str)):
            if DEBUG:
                raise Exception("node_id should be a three characters string e.g., \"000\" to \"255\" ")
            else:
                return -1
        else:
            # query for query response
            line_received = self.serport.readline()
            if line_received == b'E\r\n':
                if DEBUG:
                    print("You received Error Msg!")
                self.serport.reset_input_buffer()
                self.serport.reset_output_buffer()
                time.sleep(INTERVAL)
                if DEBUG:
                    print('Did not receive correct query status response from Node:%s' % node_id)
                    print('Query again the Node:%s if required' % node_id)
                return -1
            elif (len(line_received) == 15) and (line_received[0:8] == b'#B' + node_id.encode() + b'06V'):
                return float(line_received[8:13]) * 15.0/65536
            else:
                if DEBUG:
                    print('Did not receive correct query status response from Node:%s' % node_id)
                    print('Query again the Node:%s if required' % node_id)
                return -1

    def ping_node(self, node_id):
        """
        ping_node(address::String)

        Pings a node with specific address to see if it within reachable range.
        Return 0 if Ping was sent successfully, otherwise -1

        See also
        check_ping_response(node_id)
        """
        if (not (len(node_id) == 3)) or (not isinstance(node_id, str)):
            if DEBUG:
                raise Exception("node_id should be a three characters string e.g., \"000\" to \"255\" ")
            else:
                return -1
        else:
            command = b'$P' + node_id.encode()
            self.serport.write(command)
            time.sleep(INTERVAL)

            # query for ack signal, if not, then flush serial write buffer
            # and re-issue the command (maximum 4 tires)
            num_of_tries = 1
            while True:
                error_flag = True
                for i in range(3):  # check for valid ACK signal at least in 3 lines
                    received_bytes = self.serport.readline()
                    status = self.check_for_valid_ack_signal(received_bytes, PING)
                    if status != -1:
                        error_flag = False
                        break
                    else:
                        error_flag = True

                if error_flag and num_of_tries < MAX_TRIES:
                    self.serport.reset_input_buffer()
                    self.serport.reset_output_buffer()
                    time.sleep(INTERVAL)
                    if DEBUG:
                        print("Re-issuing the ping command!")
                    self.serport.write(command)
                    time.sleep(INTERVAL)
                    num_of_tries += 1
                elif error_flag and num_of_tries >= MAX_TRIES:
                    raise Exception('Exceeded MAX_TRIES! See if Nanomodem is configured/connected correctly?')
                else:
                    return 0

    def check_ping_response(self, node_id):
        """
        check_ping_response(node_id)


        Checks if the node with specific address has replied for Ping query.
        Returns distance from the node if correct reply was received, otherwise -1

        :param node_id: 3 character string e.g. "000" to "255"
        :return: float value containing distance from last pinged node

        Note: Wait for sufficient time after issuing ping_node command. The response
        from the other side may have not reached yet! Re-issue the check_ping_response
        after some waiting if required.

        See also
        ping_node(node_id)
        """
        if (not (len(node_id) == 3)) or (not isinstance(node_id, str)):
            if DEBUG:
                raise Exception("node_id should be a three characters string e.g., \"000\" to \"255\" ")
            else:
                return -1
        else:
            # query for ping response
            line_received = self.serport.readline()
            if line_received == b'E\r\n':
                if DEBUG:
                    print("You received Error Msg!")
                self.serport.reset_input_buffer()
                self.serport.reset_output_buffer()
                time.sleep(INTERVAL)
                if DEBUG:
                    print('Did not receive correct ping response from Node:%s' % node_id)
                    print('Ping the Node:%s again if required' % node_id)
                return -1
            elif (len(line_received) == 13) and line_received[0:6] == b'#R' + node_id.encode() + b'T':
                distance = float(line_received[6:11]) * self.soundspeed * 3.125E-5
                return distance
            elif (len(line_received) == 5) and line_received[0:2] == b'#TO':
                if DEBUG:
                    print('Did not receive ping response from Node:%s' % node_id)
                    print('Ping the Node:%s again if required' % node_id)
                return -1
            else:
                if DEBUG:
                    print('Did not receive correct ping response from Node:%s' % node_id)
                    print('Ping the Node:%s again if required' % node_id)
                return -1

    def unicast_data_packet(self, node_id, data):
        """
        unicast_data_packet(node_id:str, data:bytes)

        Unicasts data packet to particular sensor node.
        :param node_id: 3 character string e.g. "000" to "255"
        :param data: bytes of maximum length 64
        :return: #bytes unicasted successful, otherwise -1.

        Sufficient time interval should be kept between two unicast : acoustic data length ~(0.65 + n * 0.2) Secs

        See also
        broadcast_data_packet, read_data_packet
        """
        if (not (len(node_id) == 3)) or (not isinstance(node_id, str)) or (not isinstance(data, bytes)) or (not (0 < len(data) <= 64)):
            if DEBUG:
                raise Exception("node_id should be a three characters string and data should be <= 64 bytes.")
            else:
                return -1
        else:
            command = ('$U' + node_id + format(len(data), '02d')).encode() + data
            self.serport.write(command)
            time.sleep(INTERVAL)

            # query for ack signal, if not, then flush serial write buffer
            # and re-issue the command (maximum 4 tires)
            num_of_tries = 1
            while True:
                error_flag = True
                for i in range(3):  # check for valid ACK signal at least in 3 lines
                    received_bytes = self.serport.readline()
                    status = self.check_for_valid_ack_signal(received_bytes, UNICAST)
                    if status != -1:
                        error_flag = False
                        break
                    else:
                        error_flag = True

                if error_flag and num_of_tries < MAX_TRIES:
                    self.serport.reset_input_buffer()
                    self.serport.reset_output_buffer()
                    time.sleep(INTERVAL)
                    if DEBUG:
                        print("Re-issuing the unicast command!")
                    self.serport.write(command)
                    time.sleep(INTERVAL)
                    num_of_tries += 1
                elif error_flag and num_of_tries >= MAX_TRIES:
                    raise Exception('Exceeded MAX_TRIES! See if Nanomodem is configured/connected correctly?')
                else:
                    return status

    def broadcast_data_packet(self, data):
        """
        Broadcasts data packet.
        Sufficient time interval should be kept between to broadcast operation: acoustic data length ~ (0.65+ n*0.2) Secs

        :param data: should be bytes of maximum length 64
        :return: 0 if data broadcast was successful, otherwise -1

        See also
        unicast_data_packet, read_data_packet
        """
        if (not isinstance(data, bytes)) or (not (0 < len(data) <= 64)):
            if DEBUG:
                raise Exception("node_id should be a three characters string and data should be bytearray <= 64 bytes")
            else:
                return -1

        else:
            command = ('$B' + format(len(data), '02d')).encode() + data
            self.serport.write(command)
            time.sleep(INTERVAL)

            # query for ack signal, if not, then flush serial write buffer
            # and re-issue the command (maximum 4 tires)
            num_of_tries = 1
            while True:
                error_flag = True
                for i in range(3):  # check for valid ACK signal at least in 3 lines
                    received_bytes = self.serport.readline()
                    status = self.check_for_valid_ack_signal(received_bytes, BROADCAST)
                    if status != -1:
                        error_flag = False
                        break
                    else:
                        error_flag = True

                if error_flag and num_of_tries < MAX_TRIES:
                    self.serport.reset_input_buffer()
                    self.serport.reset_output_buffer()
                    time.sleep(INTERVAL)
                    if DEBUG:
                        print("Re-issuing the broadcast command!")
                    self.serport.write(command)
                    time.sleep(INTERVAL)
                    num_of_tries += 1
                elif error_flag and num_of_tries >= MAX_TRIES:
                    raise Exception('Exceeded MAX_TRIES! See if Nanomodem is configured/connected correctly?')
                else:
                    return status

    def read_data_packet(self):
        """
        read_data_packet()

        Checks for data packet at associated serial port.
        Reads the data packet if available otherwise read timeout happens.
        Returns the transmission type, sender id (if available), and received data,
        otherwise -1 if no data was available before read timeout happened.

        See also
        unicast_data, broadcast_data, unicast_data_packet_ack
        """
        # We may need to read several lines in case some data bytes are line break characters
        line_received = b''
        while self.serport.in_waiting:
            line_received += self.serport.readline()
        if line_received[0:2] == b'#U':
            data_length = int(line_received[2:4])
            data = line_received[4:-2]
            return "U", data_length, data
        elif line_received[0:2] == b'#B':
            node_id = line_received[2:5].decode()
            data_length = int(line_received[5:7])
            data = line_received[7:-2]
            return "B", node_id, data_length, data
        else:
            return -1

    def read_data_line(self):
        """
        read_data_line()

        Checks for data packet at associated serial port.
        Retrieves the data packet from serial buffer if available otherwise read timeout happens.
        Returns the packet type, sender id (if available), and received data(without <CR><LF> charaters),
        otherwise -1 if no data was available before read timeout happened.

        See also
        unicast_data, broadcast_data, unicast_data_packet_ack
        """
        line_received = self.serport.readline()
        if line_received[0:2] == b'#U':
            data_length = int(line_received[2:4])
            data = line_received[4:-2]
            return "U", data_length, data
        elif line_received[0:2] == b'#B':
            node_id = line_received[2:5].decode()
            data_length = int(line_received[5:7])
            data = line_received[7:-2]
            return "B", node_id, data_length, data
        else:
            return -1

    def unicast_data_packet_ack(self, node_id, data):
        """
        unicast_data_packet_ack(node_id:str, data:bytes)

        Unicasts data packet to particular sensor node.
        :param node_id: 3 character string e.g. "000" to "255"
        :param data: bytes of maximum length 64
        :return: #bytes unicasted successful, otherwise -1.

        Sufficient time interval should be kept between two unicast : acoustic data length ~(0.65 + n * 0.2) Secs

        See also
        broadcast_data_packet, read_data_packet
        """
        if (not (len(node_id) == 3)) or (not isinstance(node_id, str)) or (not isinstance(data, bytes)) or (not (0 < len(data) <= 64)):
            if DEBUG:
                raise Exception("node_id should be a three characters string and data should be <= 64 bytes.")
            else:
                return -1
        else:
            command = ('$M' + node_id + format(len(data), '02d')).encode() + data
            self.serport.write(command)
            print (command)
            time.sleep(INTERVAL)

            # query for ack signal, if not, then flush serial write buffer
            # and re-issue the command (maximum 4 tires)
            num_of_tries = 1
            while True:
                error_flag = True
                for i in range(3):  # check for valid ACK signal at least in 3 lines
                    #received_bytes = self.serport.readline()
                    received_bytes = command
                    #print (received_bytes)
                    status = self.check_for_valid_ack_signal(received_bytes, UNICAST_ACK)
                    print ("status =", status)
                    if status != -1:
                        error_flag = False
                        break
                    else:
                        error_flag = True

                if error_flag and num_of_tries < MAX_TRIES:
                    self.serport.reset_input_buffer()
                    self.serport.reset_output_buffer()
                    time.sleep(INTERVAL)
                    if DEBUG:
                        print("Re-issuing the unicast command!")
                    self.serport.write(command)
                    time.sleep(INTERVAL)
                    num_of_tries += 1
                elif error_flag and num_of_tries >= MAX_TRIES:
                    raise Exception('Exceeded MAX_TRIES! See if Nanomodem is configured/connected correctly?')
                else:
                    return status

    def check_unicast_ack(self, node_id):
        """
        check_unicast_ack()

        Checks for ack from the last node where data was unicasted.
        :param node_id: 3 character string e.g. "000" to "255"
        :return: float value containing the distance from the last unicasted node


        Note: Wait for sufficient time after issuing unicast_data_packet_ack command. The response
        from the other side may have not reached yet!

        See also
        ping_node, unicast_data_packet_ack
        """
        if (not (len(node_id) == 3)) or (not isinstance(node_id, str)):
            if DEBUG:
                raise Exception("node_id should be a three characters string e.g., \"000\" to \"255\" ")
            else:
                return -1
        else:
            # query for ping response
            line_received = self.serport.readline()
            if line_received == b'E\r\n':
                if DEBUG:
                    print("You received Error Msg!")
                self.serport.reset_input_buffer()
                self.serport.reset_output_buffer()
                time.sleep(INTERVAL)
                if DEBUG:
                    print('Did not receive correct ping response from Node:%s' % node_id)
                    print('Ping the Node:%s again if required' % node_id)
                return -1
            elif (len(line_received) == 13) and line_received[0:6] == b'#R' + node_id.encode() + b'T':
                distance = float(line_received[6:11]) * self.soundspeed * 3.125E-5
                return distance
            else:
                if DEBUG:
                    print('Did not receive correct ping response from Node:%s' % node_id)
                    print('Ping the Node:%s again if required' % node_id)
                return -1

    def rqst_test_msg(self, node_id):
        """
        rqst_test_msg(node_id:str)

        Request pre-determined test message from a particular node.
        :param node_id: 3 character string e.g. "000" to "255"
        :return: 0 if request was successful, otherwise -1.

        Sufficient time interval should be kept between two request because destination node replies with a long message.

        See also
        read_data_packet
        """
        if (not (len(node_id) == 3)) or (not isinstance(node_id, str)):
            if DEBUG:
                raise Exception("node_id should be a three characters string")
            else:
                return -1
        else:
            command = ('$T' + node_id).encode()
            self.serport.write(command)
            time.sleep(INTERVAL)

            # query for ack signal, if not, then flush serial write buffer
            # and re-issue the command (maximum 4 tires)
            num_of_tries = 1
            while True:
                error_flag = True
                for i in range(3):  # check for valid ACK signal at least in 3 lines
                    received_bytes = self.serport.readline()
                    status = self.check_for_valid_ack_signal(received_bytes, TEST_ACK)
                    if status != -1:
                        error_flag = False
                        break
                    else:
                        error_flag = True

                if error_flag and num_of_tries < MAX_TRIES:
                    self.serport.reset_input_buffer()
                    self.serport.reset_output_buffer()
                    time.sleep(INTERVAL)
                    if DEBUG:
                        print("Re-issuing the rqst_test_msg command!")
                    self.serport.write(command)
                    time.sleep(INTERVAL)
                    num_of_tries += 1
                elif error_flag and num_of_tries >= MAX_TRIES:
                    raise Exception('Exceeded MAX_TRIES! See if Nanomodem is configured/connected correctly?')
                else:
                    return 0

    def rqst_echo_msg(self, node_id, msg):
        """
        rqst_echo_msg(node_id:str, msg:bytes)

        Unicasts data packet to particular sensor node.
        :param node_id: 3 character string e.g. "000" to "255"
        :param msg: bytes of maximum length 64
        :return: 0 if unicast was successful, otherwise -1.

        Sufficient time interval should be kept between two unicast : acoustic data length ~(0.65 + n * 0.2) Secs

        See also
        rqst_test_mgs, read_data_packet
        """
        if (not (len(node_id) == 3)) or (not isinstance(node_id, str)) or (not isinstance(msg, bytes)) or (not (0 < len(msg) <= 64)):
            if DEBUG:
                raise Exception("node_id should be a three characters string and msg should be <= 64bytes.")
            else:
                return -1
        else:
            command = ('$E' + node_id + format(len(msg), '02d')).encode() + msg
            self.serport.write(command)
            time.sleep(INTERVAL)

            # query for ack signal, if not, then flush serial write buffer
            # and re-issue the command (maximum 4 tires)
            num_of_tries = 1
            while True:
                error_flag = True
                for i in range(3):  # check for valid ACK signal at least in 3 lines
                    received_bytes = self.serport.readline()
                    status = self.check_for_valid_ack_signal(received_bytes, ECHO_ACK)
                    if status != -1:
                        error_flag = False
                        break
                    else:
                        error_flag = True

                if error_flag and num_of_tries < MAX_TRIES:
                    self.serport.reset_input_buffer()
                    self.serport.reset_output_buffer()
                    time.sleep(INTERVAL)
                    if DEBUG:
                        print("Re-issuing the unicast command!")
                    self.serport.write(command)
                    time.sleep(INTERVAL)
                    num_of_tries += 1
                elif error_flag and num_of_tries >= MAX_TRIES:
                    raise Exception('Exceeded MAX_TRIES! See if Nanomodem is configured/connected correctly?')
                else:
                    return status

    def get_quality_indicator(self):
        """
        get_quality_indicator

        Indicates the quality of the channel by letting you know the number bytes corrected in last received msg
        :return: an integer value indicating number of bytes corrected in last received msg
        """

        command = b'$Q'
        self.serport.write(command)
        time.sleep(INTERVAL)

        # query for ack signal, if not, then flush serial write buffer
        # and re-issue the address set command (maximum 4 tires)
        num_of_tries = 1
        while True:
            error_flag = True
            for i in range(3):  # check for valid ACK signal at least in 3 lines
                received_bytes = self.serport.readline()
                status = self.check_for_valid_ack_signal(received_bytes, QLTY_CHECK)
                if status != -1:
                    error_flag = False
                    break
                else:
                    error_flag = True

            if error_flag and num_of_tries < MAX_TRIES:
                self.serport.reset_input_buffer()
                self.serport.reset_output_buffer()
                time.sleep(INTERVAL)
                if DEBUG:
                    print("Re-issuing the query status command!")
                self.serport.write(command)
                time.sleep(INTERVAL)
                num_of_tries += 1
            elif error_flag and num_of_tries >= MAX_TRIES:
                raise Exception('Exceeded MAX_TRIES! See if Nanomodem is configured/connected correctly?')
            else:
                return status

    def rqst_node_temperature(self, node_id):
        command = b"?T"
        self.unicast_data_packet(node_id, command)

    def rqst_node_pressure(self, node_id):
        command = b"?P"
        self.unicast_data_packet(node_id, command)

    def rqst_temprature(self):
        command = b"?T"
        self.broadcast_data_packet(command)

    def rqst_pressure(self):
        command = b"?P"
        self.broadcast_data_packet(command)

    def unicast_float32_value(self, node_id, value):
        value_in_bytes = struct.pack('f', value)
        self.unicast_data_packet(node_id, value_in_bytes)

    def broacast_float32_value(self, value):
        value_in_bytes = struct.pack('f', value)
        self.unicast_data_packet(value_in_bytes)

    def unicast_temperature(self, node_id, temperature):
        command = b"=T" + struct.pack('f', temperature)
        self.unicast_data_packet(node_id, command)

    def broadcast_temperature(self, temperature):
        command = b"=T" + struct.pack('f', temperature)
        self.broadcast_data_packet(command)

    def unicast_pressure(self, node_id, pressure):
        command = b"=P" + struct.pack('f', pressure)
        self.unicast_data_packet(node_id, command)

    def broadcast_pressure(self, pressure):
        command = b"=P" + struct.pack('f', pressure)
        self.broadcast_data_packet(command)

    def broadcast_beacon_signal(self, delta_time):
        command = b":T" + struct.pack('f', delta_time)
        self.broadcast_data_packet(command)

    def broadcast_latitude(self, latitude):
        command = b"Lt" + struct.pack('f', latitude)
        self.broadcast_data_packet(command)

    def broadcast_longitude(self, longitude):
        command = b"Ln" + struct.pack('f', longitude)
        self.broadcast_data_packet(command)

    def start_pinging_session(self):
        command = b":P"
        self.broadcast_data_packet(command)

    def rqst_node_for_pinging_session(self, node_id):
        command = b":P"
        self.unicast_data_packet(node_id, command)
