# UnetSim

UnetSim is the IDLE of UnetStack. We will see here how to run the UnetStack part of simulation. Remember that you should do that before doing the Python side. Here is the [UnetStack Handbook](https://unetstack.net/handbook/unet-handbook_preface.html). I strongly advise you to read before running this project if you've never heard of UnetStack before. [UnetStack website](https://unetstack.net/index.html#page-top)

## Getting Started

Here is the 3 scripts needed to run the simulation. Firstly we will what are the prerequisites and how to launch UnetSim.

### Prerequisites

Download UnetStack here : [Download](https://unetstack.net/index.html#downloads). You'll need to install a Java 8 run time environment also : [Download](https://www.java.com/en/download/).
You can put your `unet-3.0.0` folder whenever you want on your desktop

All the script on this GitHub folder need to beon your unet-3.0.0 folder so you can work on them with UnetStack. The best option is to create a folder 'USMART_Emulator' where to put all of them in unet-3.0.0 folder.

### Launch UnetSim `version unet-3.0.0`

  1. Open the terminal on unet-3.0.0 folder path 
  2. Tap the command **bin\unet sim** (if you are on Windows)
  3. Tap the command **bin/unet sim** (if you are on Linux)

A UnetStack webshell shall open on your default browser (to see how it works : [Handbook V.29](https://unetstack.net/handbook/unet-handbook_writing_simulation_scripts.html))

## Run the script

**You must run the Simulation script before your Python script !** Select sim1.groovy then press the run button.
On your log-0.txt (accews through  `log`button on the top left on your screen) you should see : 
`pyagent2 running`
`pyagent1 running`

If not the initialisation want wrong.
Only after this step you should run the Python scrip `ping_test.py` (First time will not work. Must be done twice every time `sim1.groovy` is initialised).

## Script details

## sim1.groovy
Simulation script that must be run. There is only two nodes right now but in master a change will be made to have the working configuration of the 104 nodes.

We use an extention of the Modem provided by UnetStack, `USMARTModem.groovy`

## USMARTModem.groovy
This extention of the Modem allow us to get a precise idea of the energy on each node. Remember that it should fakes the real Modem.

## PythonAgent.groovy
That is the agent that all the nodes run. It allow the ling with Python by getting the `GenericMessage` and calling the right function depending of the _type_ of the message.

Right now a progress should be made because for each message sent through Python, we should add the same number of MessageBehavior because they in the `startup()` of the agent. That's not a good way. We should find something like a `processMessage()`but with GenericMessage.

In the `processMessage()` function, there is a bug. The energy of the remote_node sent through the DatagramReq is lost on the pong process. At the end the pinging node get `[-49]` despite of somethinh like `1999.87`.






