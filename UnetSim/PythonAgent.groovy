import org.arl.fjage.*
import org.arl.unet.*
import org.arl.unet.phy.RxFrameNtf
import org.arl.unet.phy.TxFrameNtf

class PythonAgent extends UnetAgent {

    final static int PING_PROTOCOL = 10;
    final static int SUPPLY_VOLTAGE_PROTOCOL = 11;
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
    def IDreq = 0;
    def time_ping = 0;
    def function_state = null;
    def data_to_py = null;

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

        def ack = new GenericMessage(req, Performative.INFORM)
        def rsp = new GenericMessage(req, Performative.INFORM)
        println('IDreq = ' + req.IDreq)
      
        if ((req.performative == Performative.REQUEST) && (req.IDreq == 2)) {
            // IDreq = req.IDreq
            // println('IDreq = ' + IDreq)
            //log.info "Generic message request of type ${req.type}"
            function_state = 'None';
            data_to_py = 'None';
            
            switch (req.type) {
                case 'set_address':
                    println("Handling set_address request")
                    ack.state = "Handling set_address request"
                    ack.data = '#A' + corrected_address(myAddress);
                    send ack;
                    rsp.data = ack.data; break;
            }
        }
    })
    
    add new MessageBehavior(GenericMessage, { req ->
        println("In PythonAgent::MessageBehavior req ="+req)
        if (req.performative) println("req.performative is " + req.performative)
        else println("req.performative is null")

        def ack = new GenericMessage(req, Performative.INFORM)
        def rsp = new GenericMessage(req, Performative.INFORM)
        println('IDreq = ' + req.IDreq)
      
        if ((req.performative == Performative.REQUEST) && (req.IDreq == 2)) {
            // IDreq = req.IDreq
            // println('IDreq = ' + IDreq)
            //log.info "Generic message request of type ${req.type}"
            function_state = 'None';
            data_to_py = 'None';
            
            switch (req.type) {
                case 'set_address':
                    println("Handling set_address request")
                    ack.state = "Handling set_address request"
                    ack.data = '#A' + corrected_address(myAddress);
                    send ack; break;
                case 'query_status':
                    println("Handling query_status request");
                    rsp.state = "Handling query_status request"
                    rsp.data = '#A' + corrected_address(myAddress) + 'V' + phy.energy.round(3);
                    send rsp; break;
                case 'supply_voltage':
                    println("Handling supply_voltage request");
                    ack.state = "Handling supply_voltage request"; ack.data = '$V' + corrected_address(req.to_addr);
                    send ack;
                    supply_voltage(req.to_addr);
                    rsp.time_ping = time_ping; rsp.state = function_state; rsp.data = data_to_py;
                    send rsp; break;
                case 'ping':
                    println("Handling ping request");
                    ack.state = "Handling ping request"; ack.data = '$P' + corrected_address(req.to_addr);
                    send ack;
                    ping(req.to_addr);
                    rsp.time_ping = time_ping; rsp.state = function_state; rsp.data = data_to_py;
                    send rsp; break;
                case 'exe':
                    //println("Handling exe request"); 
                    exe(); break;
                case 'sense':
                    //println("Handling sense request"); 
                    sense(); break;
                default: println "Unknown request";
            }

            println "In PythonAgent::MessageBehavior, rsp is " + rsp     
            
        }
    })

    }
    
    void ping(to_addr) {
        println "Pinging ${to_addr} at ${nanoTime()}"

        DatagramReq req = new DatagramReq(to: to_addr, protocol: PING_PROTOCOL)
        phy << req
        def txNtf = receive(TxFrameNtf, 10000) // TO-DO:check protocol
        def rxNtf = receive({ it instanceof RxFrameNtf && it.from == req.to}, 4000)
        if (txNtf && rxNtf && rxNtf.from == req.to) {
            time_ping = (rxNtf.rxTime-txNtf.txTime)/1000 //in ms
            println("rxTime=${rxNtf.rxTime}")
            println("txTime=${txNtf.txTime}")
            println("Response from ${rxNtf.from}: time = ${time_ping}ms")
            function_state = 'Ping processed'
            data_to_py = '#R' + corrected_address(to_addr) + 'T' + rxNtf.data
        }
        else {
            function_state = 'Ping Request timeout'
            data_to_py = '#TO'
            println (function_state)
        }
        println(data_to_py)
    }
    
    void supply_voltage(to_addr) {
        println "Getting supply_voltage ${to_addr} at ${nanoTime()}"
        DatagramReq req = new DatagramReq(to: to_addr, protocol: SUPPLY_VOLTAGE_PROTOCOL)
        phy << req
        def txNtf = receive(TxFrameNtf, 4000) // TO-DO:check protocol
        def rxNtf = receive({ it instanceof RxFrameNtf && it.from == req.to}, 4000)
        if (txNtf && rxNtf && rxNtf.from == req.to) {
            time_ping = (rxNtf.rxTime-txNtf.txTime)/1000 //in ms
            println("Response from ${rxNtf.from}: time = ${time_ping}ms, energy = ${rxNtf.data}")
            function_state = 'Supply_voltage processed'
            data_to_py = '#B' + corrected_address(to_addr) + '06V' + rxNtf.data
        }
        else {
            function_state = 'Supply_voltage timeout'
            data_to_py = '#TO'
            println (function_state)
        }
    }
    
    
    @Override
    void processMessage(Message msg) {
        // pong
        if (msg instanceof DatagramNtf && msg.protocol == PING_PROTOCOL) {
            println("pong : Node "+ myAddress + ' from ' + msg.from +" protocol is "+ msg.protocol)
            send new DatagramReq(recipient: msg.sender, to: msg.from, data: phy.energy.round(3) as byte[], protocol: PING_PROTOCOL)
            println ('processMessage energy : ' + phy.energy)
        }
        // supply_voltage
        if (msg instanceof DatagramNtf && msg.protocol == SUPPLY_VOLTAGE_PROTOCOL) {
            println("pong : Node "+ myAddress + ' from ' + msg.from +" protocol is "+ msg.protocol)
            send new DatagramReq(recipient: msg.sender, to: msg.from, data: phy.energy.round(3) as byte[], protocol: SUPPLY_VOLTAGE_PROTOCOL)
            println ('processMessage energy : ' + phy.energy)
        }
    }
    
    String corrected_address(address) {
        address = address.toString()
        if (address.size() == 1) address = '00' + address
        if (address.size() == 2) address = '0' + address
        return address
    }
}

