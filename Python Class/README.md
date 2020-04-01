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

On your terminal with the right path
- ``` pip install numpy```
- ``` pip install fjagepy```
- ``` pip install unetpy```

## Running the tests

I repeat that you'll need to run first the simulation on UnetStack first (`sim1.groovy`) as explained [here](UnetSim/README.md) then do what is explained here.

# Ping test
For now the only function that can be tested is Ping.

Open a Terminal on the path of this folder then write ``` python ping_test.py```
**First time you run the code there should be an error**. The bug is known but not fixed, the message is not readed by UnetStack.
**Write ```python ping_test.py``` a second time**

The result must be
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

## Details of the code

### MasterAnchor.py

### Nanomodem.py

### FakeSerial_V2.py

### ping_test.py

### clientSocket.py




