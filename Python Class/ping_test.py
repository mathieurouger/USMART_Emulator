import FakeSerial_V2 as serial

serport = serial.Serial()

## SET SELF ADDRESS
nodeID = '001'
nodeID_ping = '002'
command = b'$A' + nodeID.encode()
serport.write(command)

ping_command = b'$P' + nodeID_ping.encode()
serport.write(ping_command)

ack_msg = serport.readline()
println('ack_msg : ', ack_msg)
rsp_msg = serport.readline()
println('rsp_msg : ', rsp_msg)