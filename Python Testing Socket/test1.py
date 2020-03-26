from unetpy import *
from fjagepy import *

sock = UnetSocket('localhost', 1101)   # node 1's API port as per sim script
gw = sock.getGateway()
pyagent = gw.agent('pyagent1') # agent name as per sim script
IDreq = 5       #
gmsg = GenericMessage(perf = Performative.REQUEST, recipient = pyagent)
gmsg.type = 'ping'
gmsg.data = [42]
gmsg.from_addr = 1
gmsg.to_addr = 2
gmsg.IDreq = IDreq
gw.send(gmsg)



gmsg2 = GenericMessage(perf = Performative.REQUEST, recipient = pyagent)
gmsg2.type = 'ping'
gmsg2.data = [42]
gmsg2.from_addr = 1
gmsg2.to_addr = 2
gmsg2.IDreq = IDreq
gw.send(gmsg2)
rgmsg = gw.receive(GenericMessage, 40000)
print ('ping time is', rgmsg.time_ping)

IDreq = IDreq + 1

# rsp1 = pyagent << DatagramReq(data = [42])#data = list([42]))
# print(rsp1)

