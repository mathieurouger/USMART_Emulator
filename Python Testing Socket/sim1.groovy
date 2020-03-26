import org.arl.fjage.RealTimePlatform

import org.arl.fjage.*
import org.arl.unet.*
import org.arl.unet.phy.*
import org.arl.unet.sim.*
import org.arl.unet.sim.channels.*
import static org.arl.unet.Services.*
import static org.arl.unet.phy.Physical.*

platform = RealTimePlatform           // use real-time mode

simulate {
    node '1', address: 1, web: 8101, api: 1101, stack: {
        container -> container.add 'pyagent1', new PythonAgent()
    }
    
    node '2', address: 2, web: 8102, api: 1102, stack: {
        container -> container.add 'pyagent2', new PythonAgent()
    }
}