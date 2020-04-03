import FakeSerial_V2 as serial

serport = serial.Serial()

## SET SELF ADDRESS
nodeID = '001'
command = b'$A' + nodeID.encode()
serport.write(command)

ack_msg = serport.readline()
print('ack_msg : ', ack_msg)

query_command = b'$?'
serport.write(query_command)

rsp_msg = serport.readline()
print('rsp_msg :', rsp_msg)