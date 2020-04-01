# PythonClass - USMART Emulator

You'll find all the code of the Python side of the USMART Emulator project.

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You'll need to install 3 modules to your pip to run the project : `numpy`, `fjagepy` and `unetpy`

- `numpy` is a module that I think everyone know of. You can see a detailed explication here : [NumPy](https://numpy.org/)
- `fjagepy` contain the *PythonAPI* that we need for his *Gateway Class*. UnetStack is based on fjage. We can find the documentation here : [fjage](https://buildmedia.readthedocs.org/media/pdf/fjage/dev/fjage.pdf) and the explication about the module on the *Python Gateway* section.
- `unetpy` is the *UnetStack Python API*. You can refers to the section 2.5 of the [Unet HandBook](https://unetstack.net/handbook/unet-handbook_getting_started.html)

### Installing

On your terminal with the right path :
- ``` pip install numpy```
- ``` pip install fjagepy```
- ``` pip install unetpy```

## Running the tests

***I repeat that you'll need to run first the simulation on UnetStack first (`sim1.groovy`) as explained [here](UnetSim/README.md) then do what is explained here.***

# Ping test
For now the only function that can be tested is Ping.

Open a Terminal on the path of this folder then write ``` python ping_test.py```.
**First time you run the code there should be an error**. The bug is known but not fixed, the message is not readed by UnetStack.
**Write ```python ping_test.py``` a second time**. You should to that whenever you run the simulation on UnetStack. (She would not stop until you want to).

The result must be :
```
FakeSerial got: $A001
UnetStack state : Handling set_address
ack_msg :  #A001
FakeSerial got: $P002
UnetStack state : Handling ping request
ack_msg : $P002
UnetStack state : Ping processed
rsp_msg : #R002T[-49]
```
Normally it should return the energy of the the remode node, not `[-49]`. Work must be done on that bug.

## Details of the code

### MasterAnchor.py
This script is not used for the Ping test. It's the raw code used by the real sensor. When the project is finished we must be able to call `Nanomodem.py` without getting errors.

### Nanomodem.py
This script is not used for the Ping test. It's the raw code used by the real sensor. When the project is finished we must be able to call `FakeSerial_V2.py` without getting errors. To switch from a real Serial to the FakeSerial and work and Emulator we only need to modify ```import Serial as serial``` to ```import FakeSerial_V2 as serial```
We based our tests on what this script does.

### FakeSerial_V2.py
`FakeSerial_V2.py` is a class that fake the real Serial. It must do each function that does the SerialPort but adapted to Emulator.
For now, the works is focused on the `write()` and `readline()`function but at terms each function must be developped to the end.

### ping_test.py
It is the runnable test that you should run on your terminal (twice, the first time the simulation on UnetStack is run)

### clientSocket.py
This is class called by `FakeSerial_V2.py`. It connects Python to UnetStack using a Socket and wrap the data and information in a GenericMessage before sending it to UnetStack.




