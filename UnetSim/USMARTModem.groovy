import org.arl.fjage.Message
import org.arl.unet.sim.HalfDuplexModem

import org.arl.fjage.*
import org.arl.unet.*
import org.arl.unet.phy.*
import org.arl.unet.sim.*
import org.arl.unet.sim.channels.*
import static org.arl.unet.Services.*
import static org.arl.unet.phy.Physical.*

/*

Ptx=  V*Itx //power consumed in transmission in watt
    Prx = V*Irx //power consumed in receiving packets in watt
    Etx = Math.floor(avgSent)*(Ptx*0.3675)
    energyAll =  (Math.floor(avgSent)*(Ptx*0.3675)) + (Math.floor(avgReceived)*(Prx*0.3675)) // total energy consumed for all the packets sent and received throughout the simulation
   // EtxSubset = Math.floor(avgTxCountNs)*(Ptx*0.3675) // energy consumed in transmitiing 25% of packets in Joul
    bytesDelivered = Math.floor(avgReceived)* modem.frameLength[1]
    JPerBit = energyAll/(bytesDelivered * 8)

*/
//Duration of data packet in seconds = data packet size (in bits)/bandwidth (in bps) = (15*8)/50000 = 0.0024


class USMARTModem extends HalfDuplexModem {

  static final def txPower = -17.dB
  static final def acousticDataRate = 640.bps
  static final def payLoadSize = 5.bytes
  static final def headerDuration = (30+75+200)/1000  //in seconds --> in our case nanomodem v3 provides us with the header (in ms) to add to the actual payload in the frame length.. refer to the modem datasheet
  static final def V = 5 // supply voltage in volt
  static final def Itx = 0.3, Irx = 0.005, Iidle =  0.0025 //current in Am
  
  float payLoadDuration = (payLoadSize*8)/acousticDataRate //in seconds
  float dataPacketDuration = payLoadDuration +headerDuration //in seconds
  float energy = 2000 //initial energy in Joule
  float test = energy+1
  float Ptx = V*Itx, Prx=V*Irx, Pidle = V*Iidle //power in watt
  float totalEtx =0
  float totalErx =0
  float totalEidle =0
  float totalEnergyConsumed =0 
  float Etx = Ptx * dataPacketDuration //Energy in Joul
  float Erx = Prx * dataPacketDuration
  float Eidle = Pidle * dataPacketDuration
  
  
     
 // float power = 0.00001995262315 //in watt (-17 in db=10log(p/1mw)  .. so p = 10to the power -1.7  = 0.00001995262315
 // BigDecimal Ptx = (Math.pow(10.0,(txPower/10) ))/1000 //????
 // BigDecimal Etx= Ptx *((frameLength[1]*8)/640) // This is consumed energy (in transmission) Etx = Ptx*time it takes to tramsnit tha packet
 //float Etx =10
  
   
  @Override
  boolean send(Message m) {
    if (m instanceof TxFrameNtf)
        {
          energy -= Etx// Remaining energy
          totalEtx += Etx  //total energy consumed in tx
          println(m.data)
        }
    if (m instanceof  RxFrameNtf) 
        {
          energy -= Erx   // Remaining energy
          totalErx += Erx  //total energy consumed in rx
         }
       
    if(!busy) 
     { 
       energy-= Eidle //Remaining energy
       totalEidle += Eidle //total energy consumed while Eidle
     } 
     
     
     totalEnergyConsumed = totalEtx+totalErx+totalEidle
    return super.send(m)
  }
      
}

/*
    if Message instance of $Vxxx {
node_ to = xxx
status = query_status(node_to) //yyyy of the node phy.energy
data_bytes = b'#Bxxx06Vyyyy'
return data_bytes
}

    def query_status(node_id) {
    voltage 
}
*/
