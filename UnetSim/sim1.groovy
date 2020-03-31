import org.arl.fjage.RealTimePlatform

import org.arl.fjage.*
import org.arl.unet.*
import org.arl.unet.sim.channels.*

platform = RealTimePlatform           // use real-time mode

///////////////////////////////////////////////////////////////////////////////
// channel and modem settings

channel = [
  model:                ProtocolChannelModel,
  soundSpeed:           1500.mps,
  communicationRange:   3.km,
  interferenceRange:    3.km
]

modem.model = USMARTModem

modem.dataRate =        [640.bps, 6400.bps]
modem.frameLength =     [16.bytes, 64.bytes]
modem.powerLevel =      [0.dB, -10.dB]
modem.headerLength = 0
modem.preambleDuration = 0
modem.txDelay = 0

simulate {
    node '1', address: 1, web: 8101, api: 1101, stack: {
        container -> container.add 'pyagent1', new PythonAgent()
    }
    
    node '2', address: 2,location: [500.m ,500.m, -500.m], web: 8102, api: 1102, stack: {
        container -> container.add 'pyagent2', new PythonAgent()
    }
}