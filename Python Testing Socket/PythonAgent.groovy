import org.arl.fjage.*
import org.arl.unet.*
import org.arl.unet.phy.RxFrameNtf
import org.arl.unet.phy.TxFrameNtf

class PythonAgent extends UnetAgent {

    final static int PING_PROTOCOL = 10;
    final static int NODE_STATUS_PROTOCOL = 11;
    final static int BROADCAST_PROTOCOL = 12;
    final static int UNICAST_PROTOCOL = 13;
    final static int UNICAST_ACK_PROTOCOL = 14;
    final static int TEST_MSG_PROTOCOL = 15;
    final static int ECHO_PROTOCOL = 16;
    final static int QUALITY_PROTOCOL = 17;
    
    def nodeInfo;
    def phy;
    def myLocation;
    def myAddress;
    def data;
    def IDreq = 0;
    def time_ping;

    void startup() {
        println(agentID.name + ' running')
        
    nodeInfo = agentForService Services.NODE_INFO
    phy = agentForService Services.PHYSICAL
    myLocation = nodeInfo.location
    myAddress = nodeInfo.address
    
    subscribe topic(phy)
    
    add new MessageBehavior(GenericMessage, { req ->
        println("In PythonAgent::MessageBehavior req ="+req)
        if (req.performative) println("req.performative is " + req.performative)
        else println("req.performative is null")
      
      if ((req.performative == Performative.REQUEST) && (req.IDreq > IDreq)) {
        IDreq = req.IDreq
        println('IDreq = ' + IDreq)
        //log.info "Generic message request of type ${req.type}"
        switch (req.type) {
            case 'loc':
              //println("Handling localisation request");
              sendUPSBeacon(); break;
            case 'ping':
              println("Handling ping request");
              ping(req.to_addr); break;
            case 'exe':
              //println("Handling exe request"); 
              exe(); break;
            case 'sense':
              //println("Handling sense request"); 
              sense(); break;
            default: println "Unknown request";
        }
        //println "In USMARTBaseAnchorDaemon::MessageBehavior, just after exe"
        def rsp = new GenericMessage(req, Performative.INFORM)
        rsp.ok = 1
        rsp.time_ping = time_ping
        println('time ping = ' + time_ping)
        println "In USMARTBaseAnchorDaemon::MessageBehavior, rsp is " + rsp     
        send rsp
      }
    })

    }

    void ping(to_addr) {

        println "Pinging ${to_addr} at ${nanoTime()}"

        DatagramReq req = new DatagramReq(to: to_addr, protocol: PING_PROTOCOL)
        phy << req
        println('after phy << req')
        def txNtf = receive(TxFrameNtf, 10000) // TO-DO:check protocol
        def rxNtf = receive({ it instanceof RxFrameNtf && it.from == req.to}, 10000)
        if (txNtf && rxNtf && rxNtf.from == req.to) {
            time_ping = (rxNtf.rxTime-txNtf.txTime)/1000 //in ms
            println("Response from ${rxNtf.from}: ")
            println("rxTime=${rxNtf.rxTime}")
            println("txTime=${txNtf.txTime}")
            println("Response from ${rxNtf.from}: time = ${time_ping}ms")
        }
        else {
            println 'Request timeout'
        }
        
    }

    // @Override
    // Message processRequest(Message msg) {
    //     println('PythonAgent processRequest run')
    //     if (msg instanceof DatagramReq) {
    //         println('Got a DatagramNtf with protocol ' + msg.protocol)
    //         // do whatever you want with the request
    //         // data = bytes(ntf.data)
    //         println(msg.data)
    //         // send new DatagramReq (to: 2)
    //         return new Message(msg, Performative.AGREE)
    //     }
    //     return null
    // }
    
    @Override
    void processMessage(Message msg) {

        // pong
        if (msg instanceof DatagramNtf && msg.protocol == PING_PROTOCOL) {
            println("pong : Node "+ myAddress + ' from ' + msg.from +" protocol is "+ msg.protocol)
            send new DatagramReq(recipient: msg.sender, to: msg.from, protocol: PING_PROTOCOL)
        }
    }
}
