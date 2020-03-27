from unetpy import *
from fjagepy import *

sock = UnetSocket('localhost', 1101)   # node 1's API port as per sim script
gw = sock.getGateway()
pyagent = gw.agent('pyagent1') # agent name as per sim script
IDreq = 1
gmsg = GenericMessage(perf = Performative.REQUEST, recipient = pyagent)
gmsg.IDreq = IDreq
gw.send(gmsg)

IDreq = IDreq + 1

gmsg2 = GenericMessage(perf = Performative.REQUEST, recipient = pyagent)
gmsg2.type = 'ping'
gmsg2.data = [42]
gmsg2.from_addr = 1
gmsg2.to_addr = 2
gmsg2.IDreq = IDreq
gw.send(gmsg2)


ackmsg = gw.receive(GenericMessage, 1000)
print('ack msg :', ackmsg.data)
rgmsg = gw.receive(GenericMessage, 4000)
print ('rg msg :', rgmsg.state, 'rsp :', rgmsg.data)
print('Ping time is', rgmsg.time_ping, 'ms')