import time
import struct
import numpy as np
import datetime as dt
import json
#import paho.mqtt.client as mqtt
#import paho.mqtt.publish as publish
from gps3.agps3threaded import AGPS3mechanism
from Nanomodem import Nanomodem
from ProcessTOARequest import ProcessTOA
from PerformUPSProcess import PerformUPS

#Commentaires supplémentaires : l6, l7, l32-34,l83-85, l87, l93
#Blocage paho-mqtt, client et agps3

""" Constants """
MAX_UPS_CYCLES = 1
MAX_NUM_ANCHORS = 3
MAX_LOCATION_CYCLE = 3

SOUND_SPEED = 1427  # m/s

# Anchor node IDs
ANCHOR_MASTER = 160
ANCHOR_SLAVE_1 = 161
ANCHOR_SLAVE_2 = 162


""" Initialize Modules """
nm = Nanomodem(SOUND_SPEED)  # Initialize Nanomodem

# Initialize AGP module
#agps_thread = AGPS3mechanism()  # Instantiate AGPS3 Mechanisms
#agps_thread.stream_data()  # From localhost (), or other hosts, by example, (host='gps.ddns.net')
#agps_thread.run_thread()  # Throttle time to sleep after an empty lookup, default '()' 0.2 two tenths of a second


# Get Node Status (ID and Voltage)
node_id, node_voltage = nm.query_self_status()
print("Master Anchor ID is %s and Voltage %0.2f" % (node_id, node_voltage))


# Initialize Slave Anchor's ID
slave_anchors = []
for i in range(MAX_NUM_ANCHORS-1):
    slave_anchors.append(ANCHOR_MASTER+1+i)


# Sensor's IDs
sensors = [171, 172, 173]

# Open a log file to record all the events
#logFile = "/home/pi/Workspace/GitLab/Sensor-Networks/Logs/Anchor-" + str(node_id) + "-" + dt.datetime.now().isoformat() + ".csv"
logFile = "Anchor.log" #+ str(node_id) + "-" + dt.datetime.now().isoformat() + ".csv"
lf = open(logFile, "a+")
""" End of Initialization """


 
MQTT_SERVER = "localhost"
MQTT_PATH = "usmart\ctrl"
 
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
 
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    print("MQTT client subscribing to " + MQTT_PATH)
    client.subscribe(MQTT_PATH)
 
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    m_decode=str(msg.payload.decode("utf-8","ignore"))
    print("data Received type",type(m_decode))
    print("data Received",m_decode)
    print("Converting from Json to Object")
    m_in=json.loads(m_decode)
    handleRequest(int(m_in["cmd"]))
    
    
# more callbacks, etc
 
#client = mqtt.Client()
#client.on_connect = on_connect
#client.on_message = on_message
 
#client.connect(MQTT_SERVER, 1883, 60)
 
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
#client.loop_start()

# The callback for when a PUBLISH message is received from the server.
def handleRequest(ans):
        if ans == 1:
            print("Got Option %d." % ans, flush=True)

            PropDelays = np.zeros((MAX_NUM_ANCHORS, len(sensors)), dtype=float)

            # Discovery by Master Anchor

            slave_anchor_counter = 1
            # Discovery by Slave Anchors
            for slave_id in slave_anchors:
                # Request Slave Anchor to perform TDMA-TDA setup
                msg_str = b'*T' + struct.pack('h', ANCHOR_MASTER)
                print ("slave_id =",slave_id, "msg_str =", msg_str)  
                nm.unicast_data_packet_ack(str(slave_id), msg_str)
                time.sleep(0.25)
                print("Request Slave Anchor %d for TDMA-TDA setup" % slave_id)

                # Wait for Acknowledgement from Slave Anchor

                # Try sending the packet multiple times to make sure it is received
                maxTries = 5
                reqReceived = False
                for k in range(maxTries):

                    # Send the packet
                    print("Sending the network discovery request to Node " + str(slave_id))
                    # Transmit the packet requiring an ACK
                    nm.unicast_data_packet_ack(str(slave_id).zfill(3), msg_str)
                    time.sleep(0.25)
                    # Wait for the response on the serial port
                    timeout = 5
                    timeoutCounter = 0.0
                    while not nm.serport.in_waiting:
                        time.sleep(0.025)
                        timeoutCounter += 0.025
                        if timeoutCounter > timeout:
                            break

                    # If there wasn't a timeout
                    if timeoutCounter < timeout:
                        # Check if the ACK was received
                        if nm.check_unicast_ack(str(slave_id).zfill(3)) > 0:

                            # Print message
                            print("  ACK received")
                            # Success, move on
                            reqReceived = True
                            break
                        else:
                            print("  No ACK")

                # If the REQ packet was acknowledged, wait for the network discovery results
                timeoutCounter = 0.0
                timeout = 60.0  # give it maximum two minutes to respond
                while not nm.serport.in_waiting:
                    time.sleep(0.1)
                    timeoutCounter += 0.1
                    if timeoutCounter > timeout:
                        break

                # If there wasn't a timeout
                if timeoutCounter < timeout:
                    # Read the incoming packet
                    out = nm.read_data_packet()
                    # Unicast or broadcast packet?
                    pkt_type = out[0]
                    # If this is a unicast packet, check that it is the network discovery result packet
                    if pkt_type == 'U':
                        data_length = out[1]
                        data = out[2]
                        # If there was a response, parse the packet
                        if (data_length > 4) and (data[0:4] == (b'=T' + struct.pack('h', slave_id))):

                            lat = struct.unpack('f', data[4:8])[0]
                            lon = struct.unpack('f', data[8:12])[0]

                            # Loop through every 4 bytes and parse the float as the propagation delay
                            propDelays = list()
                            logString = 'NodeDiscResp'
                            num_sensors = int((data_length - 12)/4)
                            for k in range(num_sensors):
                                # Decode the propagation delay
                                floatBytes = data[(k + 1) * 4 - 1:(k + 2) * 4 - 1]
                                propDelay = struct.unpack('f', floatBytes)[0]
                                # Add it to the log string
                                logString += '_' + '%0.3f' % propDelay
                                # If it is not 10^9 (node not found), mark this connection in the lists

                                PropDelays[slave_anchor_counter, k] = propDelay
                                if propDelay < 1e8:
                                    PropDelays[slave_anchor_counter, k] = propDelay
                                else:
                                    PropDelays[slave_anchor_counter, k] = -1.0

            print("Performing TDMA-TDA Setup on all Anchors... \r\n")
        elif ans == 2:
            print("Got Option %d. \r\n" % ans, flush=True)
            print("Performing ToA Localization... \r\n")

            # Get anchors positions and ranges from sensor
            # toa = ProcessTOA()
            # sensors = toa.estimate_location(anchors_and_ranges)
        elif ans == 3:
            print("Got Option %d. \r\n" % ans, flush=True)
            print("Performing TDoA Localization...")
            # Initialize UPS class
            ups = PerformUPS(lf, nm, agps_thread, MAX_LOCATION_CYCLE, MAX_NUM_ANCHORS, MAX_UPS_CYCLES)
            # Perform UPS cycle
            ups.perform_ups_signalling()
            print("UPS cycle completed!")
        elif ans == 4:
            print("Got Option %d. \r\n" % ans, flush=True)
        elif ans == 5:
            print("Got Option %d. \r\n" % ans, flush=True)
            # Collect the UPS estimated Locations
        elif ans == 6:
            print("Got Option %d. \r\n" % ans, flush=True)
            #Example of data
            sensorID = 180
            lat = 47.407614681869745
            lon = 8.553115781396627
            depth = -489.23

            temperature = 8.32
            accelleration = 0
            json_payload={"id":str(sensorID),
                           "lat":str(lat),
                           "lon":str(lon),
                           "depth":str(depth),
                           "temperature":str(temperature),
                           "accelleration":str(accelleration)
            }

            print(json_payload)
            print(json.dumps(json_payload))
            publish.single("usmart\data", json.dumps(json_payload), hostname=MQTT_SERVER)
        elif ans == 7:
            print("Got Option %d. \r\n" % ans, flush=True)
        elif ans == 8:
            nm.serport.close()
            time.sleep(1.0)
            lf.close()
            print("Got Option %d. Exiting... \r\n" % ans, flush=True)
            loop.stop()
            exit(1)
        else:
            print("\n Not a valid Choice Try Again!", flush=True)


""" Forever Loop """
while True:
    #  Ask user what to do?
    print("\r\n What would you like to perform?", flush=True)
    print(""" 
    1. Setup TDMA-TDA
    2. Perform ToA Localization
    3. Perform TDoA Localization
    4. Get ToA Estimated Locations
    5. Get TDoA Estimated Locations
    6. Get Sensor Reading Once
    7. Get Sensor Reading Regularly
    8. Exit
    """, flush=True)
    try:
        ans = int(input("Choose your option: "))
    except ValueError:
        print(" \n Not a valid option, Try Again! \r\n")
    else:
        handleRequest(ans)
